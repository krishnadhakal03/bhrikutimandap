# Generated migration for AgentDeliveryPartner model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_add_agent_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentDeliveryPartner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_preferred', models.BooleanField(default=False, help_text='Mark as preferred delivery partner')),
                ('is_active', models.BooleanField(default=True, help_text='Is this delivery partner active for this agent?')),
                ('notes', models.TextField(blank=True, help_text='Special instructions or notes for this partner')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_partners', to='store.agentprofile')),
                ('delivery_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_preferences', to='store.deliverypartner')),
            ],
            options={
                'ordering': ['-is_preferred', '-is_active', 'delivery_partner__name'],
                'unique_together': {('agent', 'delivery_partner')},
            },
        ),
    ]
