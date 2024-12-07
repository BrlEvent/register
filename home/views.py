from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from .models import User
from .serializers import userSerializer
import re


class Signup(APIView):

    def post(self, request):
        try:
            fullname = request.data.get('fullname')
            branch = request.data.get('branch')
            student_no = request.data.get('student_no')
            email = request.data.get('email')
            phone_no = request.data.get('phone_no')
            gender = request.data.get('gender')
            hostel=request.data.get('hostel')

            student_no_pattern = r"^\d{6,9}$"
            if not re.match(student_no_pattern, student_no):
                return JsonResponse(
                    {"msg": "Invalid student number. Must be between 6 and 9 digits."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            email_pattern = r"^[a-zA-Z]+\d+@akgec\.ac\.in$"
            if not re.match(email_pattern, email):
                return JsonResponse(
                    {"msg": "Invalid email format. Must be (name)(number)@akgec.ac.in"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            phone_pattern = r"^(?:\+91)?[6-9]\d{9}$"
            if not re.match(phone_pattern, phone_no):
                return JsonResponse(
                    {"msg": "Invalid phone number. Must be 10 digits or start with +91 followed by 10 digits."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(student_no=student_no).exists():
                return JsonResponse(
                    {"msg": "User with this student number has already registered"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {"msg": "A user with this email has already registered"},
                    status=status.HTTP_403_FORBIDDEN
                )

            data = {
                "fullname": fullname,
                "branch": branch,
                "student_no": student_no,
                "email": email,
                "phone_no": phone_no,
                "gender": gender,
                "hostel":hostel
            }

            serializer = userSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"msg": "Registered successfully"},
                    status=status.HTTP_201_CREATED
                )
            else:
                return JsonResponse(
                    {"msg": "Validation errors", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
