from django.db import models


class GenderType(models.TextChoices):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
# Create your models here.
class User(models.Model):
    fullname = models.CharField(max_length=30)
    branch = models.CharField(max_length=50)
    student_no = models.CharField(max_length=10,unique=True)
    email = models.EmailField(unique=True)
    phone_no = models.IntegerField()
    gender = models.CharField(max_length=20,choices=GenderType.choices,null=True)
    hostel=models.CharField(max_length=5,default='NO')
    attendance=models.BooleanField(default=False)

