from django.core.management.base import BaseCommand
from django.urls import resolve
from django.urls.exceptions import Resolver404

class Command(BaseCommand):
    def handle(self, *args, **options):
        test_paths = [
            '/agent/dashboard/',
            '/agent/profile/',
            '/agent/products/',
            '/agent/product/add/',
        ]
        
        for path in test_paths:
            try:
                match = resolve(path)
                self.stdout.write(f"✓ {path}")
                self.stdout.write(f"  View: {match.func.__name__}")
                self.stdout.write(f"  Module: {match.func.__module__}")
                self.stdout.write(f"  Name: {match.url_name}")
                if match.namespace:
                    self.stdout.write(f"  Namespace: {match.namespace}")
            except Resolver404:
                self.stdout.write(self.style.ERROR(f"✗ {path} - NOT FOUND"))
