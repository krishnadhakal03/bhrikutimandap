from django.core.management.base import BaseCommand
from store.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Check agent1
        agent1 = User.objects.get(username='agent1')
        print(f"agent1 username: {agent1.username}")
        print(f"agent1 first_name: {agent1.first_name}")
        print(f"agent1 last_name: {agent1.last_name}")
        print(f"agent1 role: {agent1.role}")
        print(f"agent1 is_active: {agent1.is_active}")

        # Who is Ramesh
        try:
            ramesh = User.objects.get(first_name='Ramesh')
            print(f"\nRamesh found: {ramesh.username}")
            print(f"Ramesh role: {ramesh.role}")
        except:
            print("\nRamesh user not found or multiple matches")
