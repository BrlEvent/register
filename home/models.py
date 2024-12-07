from django.db import models

# Create your models here.
class User(models.Model):
    fullname = models.CharField(max_length=30)
    branch = models.CharField(max_length=50)
    gender = models.CharField(max_length=6,default='MALE')
    hostel=models.CharField(max_length=5,default='YES')
    student_no = models.CharField(max_length=10,unique=True)
    email = models.EmailField(unique=True)
    phone_no = models.IntegerField()
    attendance=models.BooleanField(default=False)

