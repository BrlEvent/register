from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from .models import User
from .serializers import userSerializer
import re
import pyqrcode 
from io import BytesIO
from django.core.mail import EmailMessage
import pyzbar.pyzbar as pyzbar
from PIL import Image
import requests
from django.conf import settings

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
            recaptcha_token = request.data.get('recaptcha_token')

            # Validate reCAPTCHA
            recaptcha_response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": recaptcha_token
                }
            ).json()

            if not recaptcha_response.get("success"):
                return JsonResponse(
                    {"msg": "Invalid reCAPTCHA. Please try again."},
                    status=status.HTTP_400_BAD_REQUEST
                )


            student_no_pattern = r"^2\d{5,8}$"
            if not re.match(student_no_pattern, student_no):
                return JsonResponse(
                    {"msg": "Invalid student number."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            email_pattern = rf"^[a-zA-Z]+{student_no}@akgec\.ac\.in$"
            if not re.match(email_pattern, email):
                return JsonResponse(
                    {"msg": "Invalid email format"},
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
                
                qr_data = f"Name: {fullname}\nStudent No: {student_no}\nEmail: {email}"
                qr_code = pyqrcode.create(qr_data)

                qr_image = BytesIO()
                qr_code.png(qr_image, scale=6)
                qr_image.seek(0)

                # Send Email with QR Code
                subject = "Welcome to Our Platform!"
                message = f"Hi {fullname},\n\nThank you for registering on our platform. We're excited to have you on board!"
                email_msg = EmailMessage(
                    subject,
                    message,
                    from_email='your_email@example.com',  # Use settings.DEFAULT_FROM_EMAIL in production
                    to=[email]
                )
                email_msg.attach(f"{student_no}_qr.png", qr_image.getvalue(), 'image/png')
                email_msg.send()

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
         

class members(APIView):

    def get(self,request):
        try:
            users = User.objects.all()
            serializer = userSerializer(users, many=True)
            return JsonResponse(
                {"members": serializer.data},
                status=status.HTTP_200_OK,
                safe=False
            )
        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class MarkAttendance(APIView):
    
    def post(self, request):
        try:
            qr_image = request.FILES.get('qr_image')  
            
            if not qr_image:
                return JsonResponse(
                    {"error": "No QR code image provided."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            img = Image.open(qr_image)
            decoded_objects = pyzbar.decode(img)

            if not decoded_objects:
                return JsonResponse(
                    {"error": "Could not decode QR code."},
                    status=status.HTTP_400_BAD_REQUEST
                )


            qr_data = decoded_objects[0].data.decode('utf-8')
            student_no = qr_data.split("\n")[1].split(": ")[1]  

            try:
                user = User.objects.get(student_no=student_no)
                user.attendance = True
                user.save()

                return JsonResponse(
                    {"msg": f"Attendance marked as present for {user.fullname}."},
                    status=status.HTTP_200_OK
                )

            except User.DoesNotExist:
                return JsonResponse(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class studentsAttended(APIView):
    
    def get(self,request):
        try:
            data = User.objects.filter(attendance = True)
            serializer = userSerializer(data , many=True)
            return JsonResponse(
                {"members": serializer.data},
                status=status.HTTP_200_OK,
                safe=False
            )
        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class studentsAttended(APIView):
    def get(self,request):
        try:
            data = User.objects.filter(attendance = True)
            serializer = userSerializer(data , many=True)
            return JsonResponse(
                {"members": serializer.data},
                status=status.HTTP_200_OK,
                safe=False
            )
        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )