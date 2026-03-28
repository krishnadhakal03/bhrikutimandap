from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_add_dummy_gateway_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='featured_subtitle',
            field=models.CharField(default='Handpicked highlights from verified sellers.', max_length=255),
        ),
        migrations.AddField(
            model_name='homepage',
            name='featured_title',
            field=models.CharField(default='Featured Picks', max_length=200),
        ),
    ]
