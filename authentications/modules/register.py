from authentications.models import MyUser
from django.contrib.auth import authenticate
from django.conf import settings
from authentications import views
from rest_framework.exceptions import AuthenticationFailed

def register_social_user(provider,user_id,email,name):
    
    filterd_user_by_email = MyUser.objects.filter(email=email)
    
    if filterd_user_by_email.exists():
        if provider==filterd_user_by_email[0].auth_provider:          
            registered_user = authenticate(
                email=email,password=settings.CLIENT_SECRET
            )

            return {
                'username' : registered_user.username,
                'email' : registered_user.email,
                'tokens': views.get_tokens_for_user(registered_user)
            }
        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filterd_user_by_email[0].auth_provider
            )
            
    else:
        user = {
            'username' : name,
            'email' : email,
            'password':settings.CLIENT_SECRET
        }
        user = MyUser.objects.create_user(**user)
        user.auth_provider = provider
        user.save()
        
        new_user = authenticate(
            email=email,password=settings.CLIENT_SECRET
        )

        return {
            'username' : new_user.username,
            'email' : new_user.email,
            'tokens': views.get_tokens_for_user(new_user)
        }
        