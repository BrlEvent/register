from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.Signup.as_view()),
    path('member/',views.members.as_view()),
    path('attendance/',views.MarkAttendance.as_view()),
    path('students/',views.studentsAttended.as_view()),
]