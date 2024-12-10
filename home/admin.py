from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import User

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass
    list_display = ('fullname', 'student_no', 'email' , 'branch', 'phone_no', 'gender', 'hostel', 'attendance')
    search_fields = ('fullname', 'student_no', 'email', 'branch',  'gender','phone_no')
    list_filter = ('gender', 'attendance','hostel','branch')