
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        """
        Override the get_app method to handle the case where multiple apps exist.
        """
        try:
            if client_id:
                app = SocialApp.objects.get(provider=provider, client_id=client_id)
            else:
                # Get the most recently created app if multiple exist
                app = SocialApp.objects.filter(provider=provider).order_by('-id').first()
                
                if not app:
                    raise SocialApp.DoesNotExist()
            
            return app
        except SocialApp.DoesNotExist:
            raise