# posts/management/commands/setup_google_oauth.py
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up Google OAuth provider for django-allauth'

    def handle(self, *args, **options):
        # Get the default site
        try:
            site = Site.objects.get(id=1)
        except Site.DoesNotExist:
            site = Site.objects.create(domain='localhost:8000', name='localhost')
            self.stdout.write(self.style.SUCCESS('Created default site'))

        # Check if the Google provider already exists
        if SocialApp.objects.filter(provider='google').exists():
            self.stdout.write(self.style.WARNING('Google OAuth provider already exists'))
            return

        # Create the Google provider
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id='246062216998-s43e8a5v19r1k4kaujehrdjkvuqkv07h.apps.googleusercontent.com',
            secret='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'
        )

        # Associate the provider with your site
        social_app.sites.add(site)
        social_app.save()

        self.stdout.write(self.style.SUCCESS('Google OAuth provider successfully registered!'))