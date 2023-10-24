from django.contrib.gis.db import models
from authentications.models import (
    MyUser,
    Location
)
# Create your models here.




class TheareOwnerDetails(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.PROTECT,related_name='theatreowner')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,unique=True)
    phone = models.CharField(max_length=13,unique=True)
    id_proof = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False,null=True,blank=True)






# class TheatreDetails(models.Model):

#     theatre_name = models.CharField(max_length=255)
#     movies = models.ForeignKey('MovieDetails',on_delete=models.PROTECT)
#     location = models.ForeignKey(Location,on_delete=models.CASCADE)
#     num_of_screens = models.IntegerField()  
#     certification = models.FileField()
    
    
#     def save(self,*args,**kwargs):
#         super(TheatreDetails,self).save(*args,**kwargs)
#         for i in range(self.num_of_screens):
#             screen = ScreenDetails(theatre=self)
#             screen.save()


# class ScreenDetails(models.Model):

#     theatre = models.ForeignKey(TheatreDetails,on_delete=models.CASCADE)
#     screen_number = models.IntegerField()
#     number_of_seats = models.IntegerField()
#     row_count = models.IntegerField()
#     column_count = models.IntegerField()
#     seat_arrangement = models.JSONField()
    
    
        
                