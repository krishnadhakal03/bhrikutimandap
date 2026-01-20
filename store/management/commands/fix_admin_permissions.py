"""
Management command to fix admin user permissions.
Ensures all users with role='admin' have is_staff and is_superuser set to True.
"""
from django.core.management.base import BaseCommand
from store.models import User


class Command(BaseCommand):
    help = 'Fix admin user permissions - ensures users with role=admin have is_staff and is_superuser set'

    def handle(self, *args, **options):
        # Find all admin users
        admin_users = User.objects.filter(role='admin')
        
        if not admin_users.exists():
            self.stdout.write(self.style.WARNING('No users with role=admin found'))
            return
        
        updated = 0
        for user in admin_users:
            needs_update = False
            
            if not user.is_staff:
                user.is_staff = True
                needs_update = True
            
            if not user.is_superuser:
                user.is_superuser = True
                needs_update = True
            
            if needs_update:
                user.save(update_fields=['is_staff', 'is_superuser'])
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {user.username}')
                )
                updated += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {user.username} already has correct permissions')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total updated: {updated} user(s)')
        )
