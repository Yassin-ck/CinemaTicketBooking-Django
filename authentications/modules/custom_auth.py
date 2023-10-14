from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from authentications.models import MyUser



class CustomBackend(BaseBackend):
    def authenticate(self,request,phone,**kwargs):
        try:
            user = MyUser.objects.get(phone=phone)
            return user
        except MyUser.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            return None