# Generated by Django 5.1.1 on 2024-12-07 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_user_attendance_user_gender_user_hostel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='hostel',
            field=models.CharField(default='NO', max_length=5),
        ),
    ]
