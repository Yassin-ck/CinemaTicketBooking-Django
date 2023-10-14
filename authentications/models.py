from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self,phone=None,email=None,username=None, **kwargs):

        user = self.model(
            phone=phone,
            email=self.normalize_email(email),
            username=username,
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, phone=None,username=None,password=None,**kwargs):
        user = self.create_user(
            phone=phone,
            username=username            
        )
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(
        max_length=20,
        unique=True,
        null=True
    )
    email = models.EmailField(max_length=255)
    date_joined = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    

    objects = MyUserManager()

    USERNAME_FIELD = "phone"

    def __str__(self):
        return str(self.is_active)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin






class UserProfile(models.Model):
    user = models.OneToOneField(MyUser,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=30,null=True)
    address = models.TextField(null=True)
    # location = models.ForeignKey(Location,on_delete=models.PROTECT)
    
    
   