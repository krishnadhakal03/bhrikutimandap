from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_payment_gateway_config_and_transactions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentgatewayconfig',
            name='name',
            field=models.CharField(
                choices=[
                    ('stripe', 'Stripe'),
                    ('khalti', 'Khalti'),
                    ('ailepay', 'AilePay'),
                    ('dummy', 'Dummy (Local Test)'),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='gateway',
            field=models.CharField(
                choices=[
                    ('stripe', 'Stripe'),
                    ('khalti', 'Khalti'),
                    ('ailepay', 'AilePay'),
                    ('dummy', 'Dummy (Local Test)'),
                ],
                max_length=20,
            ),
        ),
    ]
