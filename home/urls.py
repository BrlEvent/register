from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.Signup.as_view()),
    path('member/',views.members.as_view()),
    path('attendance/',views.MarkAttendance.as_view()),
    path('students/',views.studentsAttended.as_view()),
    path('manual-attendance/', views.ManualAttendance.as_view()),
    path('delete-user/', views.DeleteUser.as_view(), name='delete-user'),
    path('mark-absent/', views.MarkAbsentView.as_view(), name='mark_absent'),
]