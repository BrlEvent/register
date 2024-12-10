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
import requests
from django.conf import settings
from PIL import Image
from django.template.loader import render_to_string
from email.mime.image import MIMEImage

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
                
                qr_data = f"Student No: {student_no}"
                qr_code = pyqrcode.create(qr_data)

                qr_image = BytesIO()
                qr_code.png(qr_image, scale=6)
                qr_image.seek(0)

                # Send Email with QR Code
                context = {
                    'fullname': fullname,
                    'student_no': student_no,
                    'email': email,
                    'event_name': 'Seminar on Blockchain',
                    'event_date': '12 December 2024',
                    'event_time': '8:30 am to 11:00 am',
                    'location': 'CSIT Auditorium',
                }
                image_paths = [
                    {'path': 'templates/images/image-1.png', 'cid': 'img001'},
                    {'path': 'templates/images/image-2.png', 'cid': 'img002'},
                    {'path': 'templates/images/image-4.png', 'cid': 'img004'},
                    {'path': 'templates/images/image-5.png', 'cid': 'img005'},
                    {'path': 'templates/images/image-6.png', 'cid': 'img006'}
                ]
                qr_img = MIMEImage(qr_image.getvalue(), _subtype="png")
                qr_img.add_header('Content-ID', '<qr_code>')  

                
                images = []


                for image in image_paths:
                    with open(image['path'], 'rb') as img_file:
                        img_data = img_file.read()
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', f"<{image['cid']}>")
                        images.append(img) 
                img.add_header('Content-ID', '<qr_code>')
                images.append(qr_img)


                html_content = render_to_string('mail.html', context)

                subject = "Welcome to Our Platform!"
                email_msg = EmailMessage(
                    subject=subject,
                    body=html_content,
                    from_email='brl@example.com', 
                    to=[email]
                )
                email_msg.content_subtype = 'html'

                # email_msg.attach(img)
                for img in images:
                    email_msg.attach(img)
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
        
class ManualAttendance(APIView): 
    def post(self, request):
        try:
            student_no = request.data.get('student_no')

            if not student_no:
                return JsonResponse(
                    {"msg": "Student number is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = User.objects.get(student_no=student_no)
            except User.DoesNotExist:
                return JsonResponse(
                    {"msg": "Student not found with the given student number."},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Mark the student as present
            user.attendance = True
            user.save()

            return JsonResponse(
                {"msg": f"Attendance marked as present for student {student_no}."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )