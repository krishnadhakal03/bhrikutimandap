# Payment Gateway Setup

This project now supports configurable payment gateways using database-driven settings and a strategy-based provider layer.

## Supported gateways

- Stripe
- Khalti
- AilePay
- Dummy (Local Test, no signup required)

## What was added

- Models:
  - `PaymentGatewayConfig`
  - `PaymentTransaction`
  - `PaymentGatewayAudit`
- Provider implementations:
  - `store/payment_providers.py`
- Service orchestration:
  - `store/payment_service.py`
- API endpoints:
  - `GET /api/payment-gateways/`
  - `POST /api/payments/create/`
  - `POST /api/payments/verify/`
  - `POST /api/payments/webhook/{gateway}/`
- Checkout integration:
  - users can choose enabled gateways directly on checkout page.

## Admin configuration

1. Run migrations.
2. Open admin payment gateway page:
   - `/admin/payment-gateways/`
3. Create or edit a gateway config.
4. Fill clear key/URL fields in Sandbox and/or Production sections.
5. Set environment (`sandbox` or `production`).
6. Enable the gateway.
7. Optionally set one gateway as default.
8. Use action `Validate selected gateway configurations` from list page.

## Non-technical setup shortcut (Dummy)

Use this when you do not have company registration yet.

1. Create gateway with name `Dummy (Local Test)`.
2. Turn on `Is enabled`.
3. Optionally turn on `Is default`.
4. Set `Environment` to `sandbox`.
5. In sandbox section set `Sandbox - Dummy Status` to `success`.

Now checkout will show this gateway and simulate payment completion with redirect + verification.

## Config JSON structure

`PaymentGatewayConfig` stores encrypted JSON shaped like:

```json
{
  "sandbox": {
    "publishable_key": "...",
    "secret_key": "...",
    "webhook_secret": "..."
  },
  "production": {
    "publishable_key": "...",
    "secret_key": "...",
    "webhook_secret": "..."
  }
}
```

Use keys appropriate for each gateway:

- Stripe: `publishable_key`, `secret_key`, `webhook_secret`
- Khalti: `public_key`, `secret_key`, `base_url` and optionally `initiate_url`, `verification_url`, `refund_url`
- AilePay: `api_key`, `merchant_id`, `base_url` and optionally `create_url`, `verify_url`, `refund_url`
- Dummy: `dummy_status` (`success`, `failed`, or `pending`)

## Checkout flow

1. User creates order from checkout page.
2. If an online gateway is selected:
  - Transaction is created in `pending` state.
   - User is redirected to gateway payment page.
3. On return/webhook verification:
   - Transaction becomes `success` or `failed`.
   - Order is marked paid on success.
   - Inventory/delivery processing is triggered after first successful verification.

## Security notes

- Gateway config values are encrypted at rest before storing in DB.
- Only selected safe values are exposed in public API (`publishable_key`, etc).
- Do not expose secret keys in frontend code.

## Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

## Dependencies

- `cryptography`
- `requests`
- `stripe`
