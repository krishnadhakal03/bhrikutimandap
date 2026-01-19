from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_sitesettings_facebook_url_sitesettings_instagram_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='email_host',
            field=models.CharField(default='smtp.hostinger.com', help_text='SMTP server host (e.g., smtp.hostinger.com)', max_length=255),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='email_port',
            field=models.PositiveIntegerField(default=587, help_text='SMTP port (usually 587 for TLS or 465 for SSL)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='email_use_tls',
            field=models.BooleanField(default=True, help_text='Use TLS for SMTP connection'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='email_host_user',
            field=models.EmailField(default='admin@bhrikutimandap.com', help_text='SMTP username (usually your email address)', max_length=254),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='email_host_password',
            field=models.CharField(blank=True, default='', help_text='SMTP password (stored securely)', max_length=255),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='default_from_email',
            field=models.EmailField(default='admin@bhrikutimandap.com', help_text='Default sender email address', max_length=254),
        ),
    ]
