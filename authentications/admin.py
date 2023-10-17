from django.contrib import admin
from .models import MyUser,UserProfile
# Register your models here.


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id','username','phone','email')
@admin.register(UserProfile)
class UserProfiileAdmin(admin.ModelAdmin):
    list_display = ('user_id','first_name','last_name','address','location')