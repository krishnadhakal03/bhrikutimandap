"""
Seed delivery partners for the platform
"""
from django.core.management.base import BaseCommand
from store.models import DeliveryPartner


class Command(BaseCommand):
    help = 'Seed delivery partners for the platform'

    def handle(self, *args, **options):
        # Sample delivery partners
        delivery_partners = [
            {
                'name': 'SpeedyExpress',
                'phone': '+91-8765432100',
                'email': 'info@speedyexpress.in',
                'vehicle_type': 'bike',
                'vehicle_number': 'DL-01-AB-1001',
                'current_location': 'Delhi',
                'avg_delivery_time_hours': 24,
                'success_delivery_rate': 98.5,
            },
            {
                'name': 'QuickDeliver',
                'phone': '+91-9876543210',
                'email': 'support@quickdeliver.in',
                'vehicle_type': 'auto',
                'vehicle_number': 'DL-02-CD-2002',
                'current_location': 'Delhi',
                'avg_delivery_time_hours': 18,
                'success_delivery_rate': 96.0,
            },
            {
                'name': 'TrustCourier',
                'phone': '+91-8765432111',
                'email': 'hello@trustcourier.in',
                'vehicle_type': 'car',
                'vehicle_number': 'DL-03-EF-3003',
                'current_location': 'Delhi',
                'avg_delivery_time_hours': 12,
                'success_delivery_rate': 97.5,
            },
            {
                'name': 'FastShip Services',
                'phone': '+91-9876543211',
                'email': 'contact@fastship.in',
                'vehicle_type': 'truck',
                'vehicle_number': 'DL-04-GH-4004',
                'current_location': 'Delhi',
                'avg_delivery_time_hours': 36,
                'success_delivery_rate': 95.0,
            },
            {
                'name': 'LocalDeliver',
                'phone': '+91-8765432122',
                'email': 'ops@localdeliver.in',
                'vehicle_type': 'bike',
                'vehicle_number': 'DL-05-IJ-5005',
                'current_location': 'Delhi',
                'avg_delivery_time_hours': 8,
                'success_delivery_rate': 99.0,
            },
        ]

        for partner_data in delivery_partners:
            partner, created = DeliveryPartner.objects.get_or_create(
                name=partner_data['name'],
                defaults=partner_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created delivery partner: {partner.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Delivery partner already exists: {partner.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded delivery partners')
        )
