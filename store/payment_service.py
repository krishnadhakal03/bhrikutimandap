from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import Order, PaymentGatewayAudit, PaymentGatewayConfig, PaymentTransaction
from .payment_providers import (
    AilePayProvider,
    DummyProvider,
    KhaltiProvider,
    PaymentProvider,
    PaymentProviderError,
    StripeProvider,
)


class PaymentServiceError(Exception):
    pass


PROVIDER_MAP: dict[str, type[PaymentProvider]] = {
    'stripe': StripeProvider,
    'khalti': KhaltiProvider,
    'ailepay': AilePayProvider,
    'dummy': DummyProvider,
}


class PaymentService:
    @staticmethod
    def get_gateway(name: str | None = None) -> PaymentGatewayConfig:
        qs = PaymentGatewayConfig.objects.filter(is_enabled=True)
        if name:
            gateway = qs.filter(name=name.lower()).first()
            if gateway:
                return gateway
            raise PaymentServiceError(f'Payment gateway {name} is not enabled.')

        gateway = qs.filter(is_default=True).first() or qs.first()
        if not gateway:
            raise PaymentServiceError('No enabled payment gateway found. Configure one in admin.')
        return gateway

    @staticmethod
    def get_enabled_gateways() -> list[PaymentGatewayConfig]:
        return list(PaymentGatewayConfig.objects.filter(is_enabled=True).order_by('-is_default', 'name'))

    @staticmethod
    def get_provider(gateway: PaymentGatewayConfig) -> PaymentProvider:
        provider_cls = PROVIDER_MAP.get(gateway.name.lower())
        if not provider_cls:
            raise PaymentServiceError(f'No provider implementation found for gateway {gateway.name}.')
        return provider_cls(gateway)

    @staticmethod
    def create_transaction(
        order: Order,
        gateway_name: str,
        amount: Decimal,
        currency: str = 'NPR',
    ) -> PaymentTransaction:
        return PaymentTransaction.objects.create(
            order=order,
            gateway=gateway_name.lower(),
            amount=amount,
            currency=currency,
            status=PaymentTransaction.Status.PENDING,
            metadata={},
        )

    @staticmethod
    def initiate_payment(
        order: Order,
        gateway_name: str,
        return_url: str,
        cancel_url: str,
        currency: str = 'NPR',
    ) -> dict[str, Any]:
        gateway = PaymentService.get_gateway(gateway_name)
        provider = PaymentService.get_provider(gateway)

        tx = PaymentService.create_transaction(
            order=order,
            gateway_name=gateway.name,
            amount=order.total(),
            currency=currency,
        )

        try:
            result = provider.create_payment(
                order_id=order.id,
                amount=order.total(),
                currency=currency,
                return_url=return_url,
                cancel_url=cancel_url,
            )
            tx.external_id = result.get('external_id', '')
            tx.metadata = result.get('raw', {})
            tx.status = 'pending'
            tx.save(update_fields=['external_id', 'metadata', 'status', 'updated_at'])

            PaymentGatewayAudit.objects.create(
                gateway=gateway,
                action='create_payment',
                details={'order_id': order.id, 'transaction_id': tx.id, 'gateway': gateway.name},
            )

            return {
                'transaction_id': tx.id,
                'external_id': tx.external_id,
                'redirect_url': result.get('redirect_url', ''),
                'gateway': gateway.name,
                'status': tx.status,
            }
        except Exception as exc:
            tx.status = 'failed'
            tx.last_error = str(exc)
            tx.save(update_fields=['status', 'last_error', 'updated_at'])
            raise PaymentServiceError(str(exc))

    @staticmethod
    @transaction.atomic
    def verify_payment(
        gateway_name: str,
        payload: dict[str, Any],
        actor=None,
        from_webhook: bool = False,
    ) -> dict[str, Any]:
        gateway = PaymentService.get_gateway(gateway_name)
        provider = PaymentService.get_provider(gateway)

        try:
            verification = provider.verify_payment(payload)
        except PaymentProviderError as exc:
            raise PaymentServiceError(str(exc))

        external_id = verification.get('external_id') or payload.get('external_id') or payload.get('session_id') or payload.get('pidx')

        tx = PaymentTransaction.objects.select_for_update().filter(
            gateway=gateway.name,
            external_id=external_id,
        ).first()

        if not tx:
            tx = PaymentTransaction.objects.select_for_update().filter(
                gateway=gateway.name,
                order_id=verification.get('order_id') or payload.get('order_id'),
            ).order_by('-created_at').first()

        if not tx:
            raise PaymentServiceError('Payment transaction not found for verification payload.')

        tx.verification_attempts += 1
        tx.metadata = {**(tx.metadata or {}), 'verification': verification, 'webhook': from_webhook}

        if verification.get('success'):
            tx.status = 'success'
            tx.last_error = ''
            tx.save(update_fields=['verification_attempts', 'metadata', 'status', 'last_error', 'updated_at'])

            order = tx.order
            was_paid = order.paid
            order.paid = True
            order.status = 'confirmed'
            order.save(update_fields=['paid', 'status'])

            # For online payments, finalize inventory and delivery only after payment verification.
            if not was_paid:
                from .services import process_order_created
                process_order_created(order)
        else:
            tx.status = 'failed'
            tx.last_error = 'Verification failed'
            tx.save(update_fields=['verification_attempts', 'metadata', 'status', 'last_error', 'updated_at'])

        PaymentGatewayAudit.objects.create(
            gateway=gateway,
            actor=actor if getattr(actor, 'is_authenticated', False) else None,
            action='webhook_verify' if from_webhook else 'verify_payment',
            details={
                'transaction_id': tx.id,
                'external_id': tx.external_id,
                'success': bool(verification.get('success')),
            },
        )

        return {
            'success': bool(verification.get('success')),
            'transaction_id': tx.id,
            'order_id': tx.order_id,
            'status': tx.status,
        }

    @staticmethod
    def handle_webhook(gateway_name: str, request) -> dict[str, Any]:
        gateway = PaymentService.get_gateway(gateway_name)
        provider = PaymentService.get_provider(gateway)

        try:
            provider_payload = provider.handle_webhook(request)
            return PaymentService.verify_payment(
                gateway_name=gateway.name,
                payload=provider_payload,
                from_webhook=True,
            )
        except Exception as exc:
            PaymentGatewayAudit.objects.create(
                gateway=gateway,
                action='webhook_error',
                details={'error': str(exc)},
            )
            raise PaymentServiceError(str(exc))

    @staticmethod
    def validate_gateway_configuration(gateway: PaymentGatewayConfig) -> tuple[bool, str]:
        provider = PaymentService.get_provider(gateway)
        return provider.validate_configuration()
