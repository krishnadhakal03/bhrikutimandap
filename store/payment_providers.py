from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
import json
import time
from typing import Any

import requests

from .models import PaymentGatewayConfig

try:
    import stripe
except Exception:  # pragma: no cover - optional import in non-stripe environments
    stripe = None


class PaymentProviderError(Exception):
    pass


class PaymentProvider(ABC):
    def __init__(self, gateway_config: PaymentGatewayConfig):
        self.gateway_config = gateway_config
        self.active_config = gateway_config.get_active_config()

    @abstractmethod
    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def handle_webhook(self, request) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def refund_payment(self, transaction_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def validate_configuration(self) -> tuple[bool, str]:
        return True, 'Gateway configuration looks valid.'


class StripeProvider(PaymentProvider):
    def _secret_key(self) -> str:
        key = (self.active_config or {}).get('secret_key', '')
        if not key:
            raise PaymentProviderError('Stripe secret key is missing.')
        return key

    def _webhook_secret(self) -> str:
        return (self.active_config or {}).get('webhook_secret', '')

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        if stripe is None:
            raise PaymentProviderError('Stripe SDK is not installed.')

        stripe.api_key = self._secret_key()
        unit_amount = int((amount * Decimal('100')).quantize(Decimal('1')))
        success_url = f"{return_url}&session_id={{CHECKOUT_SESSION_ID}}" if '?' in return_url else f"{return_url}?session_id={{CHECKOUT_SESSION_ID}}"

        session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[
                {
                    'quantity': 1,
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {'name': f'Order #{order_id}'},
                        'unit_amount': unit_amount,
                    },
                }
            ],
            metadata={'order_id': str(order_id)},
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return {
            'redirect_url': session.url,
            'external_id': session.id,
            'raw': session.to_dict() if hasattr(session, 'to_dict') else dict(session),
        }

    def verify_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        if stripe is None:
            raise PaymentProviderError('Stripe SDK is not installed.')

        session_id = payload.get('session_id') or payload.get('external_id')
        if not session_id:
            raise PaymentProviderError('Stripe session_id is required for verification.')

        stripe.api_key = self._secret_key()
        session = stripe.checkout.Session.retrieve(session_id)
        paid = (session.payment_status == 'paid')

        return {
            'success': paid,
            'external_id': session.id,
            'order_id': int(session.metadata.get('order_id')) if session.metadata and session.metadata.get('order_id') else None,
            'raw': session.to_dict() if hasattr(session, 'to_dict') else dict(session),
        }

    def handle_webhook(self, request) -> dict[str, Any]:
        if stripe is None:
            raise PaymentProviderError('Stripe SDK is not installed.')

        webhook_secret = self._webhook_secret()
        if not webhook_secret:
            raise PaymentProviderError('Stripe webhook secret is missing.')

        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        event = stripe.Webhook.construct_event(request.body, signature, webhook_secret)

        event_type = event.get('type', '')
        if event_type == 'checkout.session.completed':
            data = event['data']['object']
            metadata = data.get('metadata', {}) or {}
            order_id = metadata.get('order_id')
            return {
                'success': True,
                'event_type': event_type,
                'external_id': data.get('id', ''),
                'order_id': int(order_id) if order_id else None,
                'raw': event,
            }

        return {'success': False, 'event_type': event_type, 'raw': event}

    def refund_payment(self, transaction_id: str) -> dict[str, Any]:
        if stripe is None:
            raise PaymentProviderError('Stripe SDK is not installed.')

        stripe.api_key = self._secret_key()
        session = stripe.checkout.Session.retrieve(transaction_id)
        payment_intent = session.get('payment_intent')
        if not payment_intent:
            raise PaymentProviderError('Stripe payment intent is missing for this transaction.')

        refund = stripe.Refund.create(payment_intent=payment_intent)
        return {
            'success': refund.get('status') in {'succeeded', 'pending'},
            'external_id': refund.get('id', ''),
            'raw': refund,
        }

    def validate_configuration(self) -> tuple[bool, str]:
        if stripe is None:
            return False, 'Stripe SDK not installed. Add stripe package.'

        active = self.active_config or {}
        missing = [k for k in ('publishable_key', 'secret_key', 'webhook_secret') if not active.get(k)]
        if missing:
            return False, f"Missing Stripe fields: {', '.join(missing)}"
        return True, 'Stripe config is valid.'


class KhaltiProvider(PaymentProvider):
    def _secret_key(self) -> str:
        key = (self.active_config or {}).get('secret_key', '')
        if not key:
            raise PaymentProviderError('Khalti secret key is missing.')
        return key

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        active = self.active_config or {}
        init_url = active.get('initiate_url') or active.get('base_url', '').rstrip('/') + '/epayment/initiate/'
        if not init_url:
            raise PaymentProviderError('Khalti initiate_url/base_url not configured.')

        payload = {
            'return_url': return_url,
            'website_url': cancel_url,
            'amount': int((amount * Decimal('100')).quantize(Decimal('1'))),
            'purchase_order_id': str(order_id),
            'purchase_order_name': f'Order #{order_id}',
        }
        headers = {
            'Authorization': f"Key {self._secret_key()}",
            'Content-Type': 'application/json',
        }

        response = requests.post(init_url, json=payload, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'Khalti initiate failed: {response.text[:500]}')

        data = response.json()
        return {
            'redirect_url': data.get('payment_url', ''),
            'external_id': data.get('pidx', ''),
            'raw': data,
        }

    def verify_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        active = self.active_config or {}
        verification_url = active.get('verification_url') or active.get('base_url', '').rstrip('/') + '/epayment/lookup/'
        if not verification_url:
            raise PaymentProviderError('Khalti verification_url/base_url not configured.')

        pidx = payload.get('pidx') or payload.get('external_id')
        if not pidx:
            raise PaymentProviderError('Khalti pidx is required for verification.')

        headers = {
            'Authorization': f"Key {self._secret_key()}",
            'Content-Type': 'application/json',
        }
        response = requests.post(verification_url, json={'pidx': pidx}, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'Khalti verification failed: {response.text[:500]}')

        data = response.json()
        status = str(data.get('status', '')).lower()
        success = status in {'completed', 'success'}

        return {
            'success': success,
            'external_id': pidx,
            'order_id': int(data.get('purchase_order_id')) if str(data.get('purchase_order_id', '')).isdigit() else None,
            'raw': data,
        }

    def handle_webhook(self, request) -> dict[str, Any]:
        try:
            payload = request.body.decode('utf-8')
            data = {} if not payload else json.loads(payload)
        except Exception as exc:
            raise PaymentProviderError(f'Invalid Khalti webhook payload: {exc}')

        return self.verify_payment(data)

    def refund_payment(self, transaction_id: str) -> dict[str, Any]:
        active = self.active_config or {}
        refund_url = active.get('refund_url')
        if not refund_url:
            raise PaymentProviderError('Khalti refund_url is not configured.')

        headers = {
            'Authorization': f"Key {self._secret_key()}",
            'Content-Type': 'application/json',
        }
        response = requests.post(refund_url, json={'pidx': transaction_id}, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'Khalti refund failed: {response.text[:500]}')

        data = response.json()
        return {'success': True, 'external_id': transaction_id, 'raw': data}

    def validate_configuration(self) -> tuple[bool, str]:
        active = self.active_config or {}
        missing = [k for k in ('public_key', 'secret_key') if not active.get(k)]
        if missing:
            return False, f"Missing Khalti fields: {', '.join(missing)}"
        if not (active.get('verification_url') or active.get('base_url')):
            return False, 'Khalti verification_url or base_url is required.'
        return True, 'Khalti config is valid.'


class AilePayProvider(PaymentProvider):
    def _api_key(self) -> str:
        key = (self.active_config or {}).get('api_key', '')
        if not key:
            raise PaymentProviderError('AilePay api_key is missing.')
        return key

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        active = self.active_config or {}
        base_url = active.get('base_url', '').rstrip('/')
        create_url = active.get('create_url') or f"{base_url}/payments/create"
        if not create_url:
            raise PaymentProviderError('AilePay create_url/base_url not configured.')

        payload = {
            'order_id': str(order_id),
            'amount': str(amount),
            'currency': currency,
            'return_url': return_url,
            'cancel_url': cancel_url,
            'merchant_id': active.get('merchant_id', ''),
        }
        headers = {
            'Authorization': f"Bearer {self._api_key()}",
            'Content-Type': 'application/json',
        }

        response = requests.post(create_url, json=payload, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'AilePay create failed: {response.text[:500]}')

        data = response.json()
        return {
            'redirect_url': data.get('payment_url') or data.get('redirect_url', ''),
            'external_id': data.get('transaction_id', ''),
            'raw': data,
        }

    def verify_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        active = self.active_config or {}
        base_url = active.get('base_url', '').rstrip('/')
        verify_url = active.get('verify_url') or f"{base_url}/payments/verify"
        if not verify_url:
            raise PaymentProviderError('AilePay verify_url/base_url not configured.')

        tx = payload.get('transaction_id') or payload.get('external_id')
        if not tx:
            raise PaymentProviderError('AilePay transaction_id is required for verification.')

        headers = {
            'Authorization': f"Bearer {self._api_key()}",
            'Content-Type': 'application/json',
        }
        response = requests.post(verify_url, json={'transaction_id': tx}, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'AilePay verify failed: {response.text[:500]}')

        data = response.json()
        status = str(data.get('status', '')).lower()
        success = status in {'success', 'completed', 'paid'}

        return {
            'success': success,
            'external_id': tx,
            'order_id': int(data.get('order_id')) if str(data.get('order_id', '')).isdigit() else None,
            'raw': data,
        }

    def handle_webhook(self, request) -> dict[str, Any]:
        try:
            payload = request.body.decode('utf-8')
            data = {} if not payload else json.loads(payload)
        except Exception as exc:
            raise PaymentProviderError(f'Invalid AilePay webhook payload: {exc}')

        tx = data.get('transaction_id') or data.get('external_id')
        success = str(data.get('status', '')).lower() in {'success', 'completed', 'paid'}
        return {
            'success': success,
            'external_id': tx or '',
            'order_id': int(data.get('order_id')) if str(data.get('order_id', '')).isdigit() else None,
            'raw': data,
        }

    def refund_payment(self, transaction_id: str) -> dict[str, Any]:
        active = self.active_config or {}
        base_url = active.get('base_url', '').rstrip('/')
        refund_url = active.get('refund_url') or f"{base_url}/payments/refund"
        if not refund_url:
            raise PaymentProviderError('AilePay refund_url/base_url not configured.')

        headers = {
            'Authorization': f"Bearer {self._api_key()}",
            'Content-Type': 'application/json',
        }
        response = requests.post(refund_url, json={'transaction_id': transaction_id}, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise PaymentProviderError(f'AilePay refund failed: {response.text[:500]}')

        data = response.json()
        return {'success': True, 'external_id': transaction_id, 'raw': data}

    def validate_configuration(self) -> tuple[bool, str]:
        active = self.active_config or {}
        missing = [k for k in ('api_key', 'merchant_id') if not active.get(k)]
        if missing:
            return False, f"Missing AilePay fields: {', '.join(missing)}"
        if not (active.get('base_url') or active.get('create_url')):
            return False, 'AilePay base_url or create_url is required.'
        return True, 'AilePay config is valid.'


class DummyProvider(PaymentProvider):
    """Local fake gateway for development without external accounts."""

    def _status(self, payload: dict[str, Any] | None = None) -> str:
        payload = payload or {}
        status = (
            payload.get('dummy_status')
            or payload.get('status')
            or (self.active_config or {}).get('dummy_status')
            or 'success'
        )
        return str(status).strip().lower()

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        _ = cancel_url  # cancel URL is not used for local simulation.
        status = self._status()
        external_id = f"dummy_{order_id}_{int(time.time())}"
        sep = '&' if '?' in return_url else '?'
        redirect_url = (
            f"{return_url}{sep}external_id={external_id}"
            f"&dummy_status={status}&order_id={order_id}"
        )
        return {
            'redirect_url': redirect_url,
            'external_id': external_id,
            'raw': {
                'gateway': 'dummy',
                'order_id': order_id,
                'amount': str(amount),
                'currency': currency,
                'dummy_status': status,
            },
        }

    def verify_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        status = self._status(payload)
        success = status in {'success', 'completed', 'paid'}
        order_id = payload.get('order_id')
        return {
            'success': success,
            'external_id': payload.get('external_id', ''),
            'order_id': int(order_id) if str(order_id).isdigit() else None,
            'raw': {'dummy_status': status, 'payload': payload},
        }

    def handle_webhook(self, request) -> dict[str, Any]:
        try:
            payload = request.body.decode('utf-8')
            data = {} if not payload else json.loads(payload)
        except Exception as exc:
            raise PaymentProviderError(f'Invalid Dummy webhook payload: {exc}')
        return self.verify_payment(data)

    def refund_payment(self, transaction_id: str) -> dict[str, Any]:
        return {
            'success': True,
            'external_id': transaction_id,
            'raw': {'gateway': 'dummy', 'refunded': True},
        }

    def validate_configuration(self) -> tuple[bool, str]:
        return True, 'Dummy gateway is ready for local testing.'
