from django.db import models

# Create your models here.
class User(models.Model):
    fullname = models.CharField(max_length=30)
    branch = models.CharField(max_length=10)
    student_no = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)
    phone_no = models.IntegerField()

