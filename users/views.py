from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .models import User,PendingUser
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
import random
import string
from django.conf import settings
from django.contrib.auth.hashers import make_password

def send_verification_email(user):
    # إنشاء رمز مكون من 6 محارف (أرقام + أحرف كبيرة وصغيرة)
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    user.verification_code = verification_code
    user.code_expiration = now() + timedelta(minutes=5)  # صلاحية 5 دقائق
    user.save()

    subject = "Your verification code"
    message = f" Your verification code: {verification_code}\n Please enter it within 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
# رابط اعادة ارسال رسالة التحقق

class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"message": "هذا البريد الإلكتروني غير مسجل أو تم تفعيله مسبقًا."}, status=status.HTTP_400_BAD_REQUEST)

        if pending_user.created_at + timedelta(minutes=5) > now():
            return Response({"message": "تم إرسال رمز التحقق مؤخرًا. يرجى المحاولة لاحقًا."}, status=status.HTTP_400_BAD_REQUEST)

        send_verification_email(pending_user)
        return Response({"message": "تم إرسال رمز التحقق مرة أخرى. يرجى التحقق من بريدك الإلكتروني."}, status=status.HTTP_200_OK)

# رابط التحقق و ادخال الرموز ال 6
class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"message": "هذا البريد الإلكتروني غير مسجل."}, status=status.HTTP_400_BAD_REQUEST)

        if not pending_user.is_code_valid(code):
            return Response({"message": "رمز التحقق غير صالح أو منتهي الصلاحية."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password
        )
        user.is_active = True
        user.is_client = pending_user.is_client
        user.save()
        pending_user.delete()

        return Response({"message": "تم تفعيل الحساب بنجاح."}, status=status.HTTP_200_OK)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')  # كلمة المرور الجديدة

        if len(new_password) < 8:
            return Response(
                {"message": "يجب اقل شيء 8 محارف لكلمة المرور"},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "هذا البريد الإلكتروني غير مسجل."}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء رمز تحقق
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.code_expiration = now() + timedelta(minutes=5)
        user.temp_password = make_password(new_password)  # تخزين كلمة المرور بشكل مؤقت
        user.save()

        # إرسال البريد الإلكتروني
        subject = "إعادة تعيين كلمة المرور"
        message = f"رمز التحقق الخاص بك هو: {verification_code}\nيرجى إدخاله خلال 5 دقائق."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني."}, status=status.HTTP_200_OK)

class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')  # رمز التحقق

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "هذا البريد الإلكتروني غير مسجل."}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من الرمز وصلاحيته
        if user.verification_code != code or user.code_expiration < now():
            return Response({"message": "رمز التحقق غير صالح أو منتهي الصلاحية."}, status=status.HTTP_400_BAD_REQUEST)

        # تحديث كلمة المرور
        if user.temp_password:
            user.password = user.temp_password
            user.temp_password = None  # إزالة كلمة المرور المؤقتة
            user.verification_code = None  # إزالة الرمز
            user.code_expiration = None
            user.save()
            return Response({"message": "تم تحديث كلمة المرور بنجاح."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "لم يتم تقديم كلمة مرور جديدة."}, status=status.HTTP_400_BAD_REQUEST)

# Admin API  


class AdminRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        if len(data['password']) < 8:
            return Response(
                {"message": "يجب أن تكون كلمة المرور مكونة من 8 محارف على الأقل"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "هذا البريد الإلكتروني مسجل بالفعل. يرجى تسجيل الدخول"},status=status.HTTP_400_BAD_REQUEST)
        # البحث عن سجل موجود بنفس البريد الإلكتروني
        pending_user, created = PendingUser.objects.get_or_create(
            email=data['email'],
            defaults={
                'username': data['username'],
                'password': data['password']  # تأكد من تشفير كلمة المرور
            }
        )
        
        if not created:
            # إذا لم يتم إنشاء سجل جديد، تحقق من انتهاء صلاحية السجل القديم
            if pending_user.created_at + timedelta(minutes=5) > now():
                return Response({"message": "يرجى الانتظار حتى تنتهي صلاحية المحاولة السابقة."}, status=status.HTTP_400_BAD_REQUEST)
            # تحديث السجل القديم
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "تم ارسال رمز التحقق الى بريدك الالكتروني. يرجى تأكيد بريدك الإلكتروني خلال 5 دقائق."}, status=status.HTTP_200_OK)


class AdminLoginView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            if user.is_client:
                return Response({"error": "Clients are not allowed to log in from this link"}, status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class AdminLogoutView(APIView):
    def post(self, request):
        try:
            # Delete the token associated with the user
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token or already logged out"}, status=status.HTTP_400_BAD_REQUEST)
        
# Client API 
        
class ClientRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        
        if len(data['password']) < 8:
            return Response(
                {"message": "يجب أن تكون كلمة المرور مكونة من 8 محارف على الأقل"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "هذا البريد الإلكتروني مسجل بالفعل. يرجى تسجيل الدخول"}, status=status.HTTP_400_BAD_REQUEST)

        pending_user, created = PendingUser.objects.get_or_create(
            email=data['email'],
            defaults={
                'username': data['username'],
                'password': data['password'],  # تأكد من تشفير كلمة المرور
                'is_client': True
            }
        )

        if not created:
            if pending_user.created_at + timedelta(minutes=5) > now():
                return Response({"message": "يرجى الانتظار حتى تنتهي صلاحية المحاولة السابقة."}, status=status.HTTP_400_BAD_REQUEST)
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "تم إرسال رمز التحقق. يرجى إدخاله خلال 5 دقائق."}, status=status.HTTP_200_OK)


class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_client:  # التأكد من أن المستخدم عميل
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials or not a client"}, status=status.HTTP_401_UNAUTHORIZED)

class ClientLogoutView(APIView):
    def post(self, request):
        try:
            # التحقق من أن المستخدم هو عميل
            if request.user.is_client:
                token = Token.objects.get(user=request.user)
                token.delete()
                return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Not a client"}, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token or already logged out"}, status=status.HTTP_400_BAD_REQUEST)
