from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,BasePermission
from django.shortcuts import get_object_or_404
from .permissions import IsSuperUser
from .serializers import UsersSerializer
from .serializers import UserDetailSerializer
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import User,PendingUser
from .serializers import UserPermissionSerializer
from django.contrib.auth.models import Permission
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
            return Response({"message": "this email is not registered or has been activated in advance."}, status=status.HTTP_400_BAD_REQUEST)

        if pending_user.created_at + timedelta(minutes=5) > now():
            return Response({"message": "The verification code has been sent recently,please try later."}, status=status.HTTP_400_BAD_REQUEST)

        send_verification_email(pending_user)
        return Response({"message": "The verification code has been sent again, please check your email."}, status=status.HTTP_200_OK)

# رابط التحقق و ادخال الرموز ال 6
class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if not pending_user.is_code_valid(code):
            return Response({"message": "The verification code is incorrect or expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password
        )
        user.is_active = True
        user.is_client = pending_user.is_client
        user.save()
        pending_user.delete()

        return Response({"message": "The account was successfully activated."}, status=status.HTTP_200_OK)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')  # كلمة المرور الجديدة

        if len(new_password) < 8:
            return Response(
                {"message": "The password must be 8 or more letters."},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء رمز تحقق
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.code_expiration = now() + timedelta(minutes=5)
        user.temp_password = make_password(new_password)  # تخزين كلمة المرور بشكل مؤقت
        user.save()

        # إرسال البريد الإلكتروني
        subject = "password reset"
        message = f"your verification code is: {verification_code}\n Please enter it within 5 minutes."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "The verification code has been sent to your email."}, status=status.HTTP_200_OK)

class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')  # رمز التحقق

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من الرمز وصلاحيته
        if user.verification_code != code or user.code_expiration < now():
            return Response({"message": "The verification code is incorrect or expired."}, status=status.HTTP_400_BAD_REQUEST)

        # تحديث كلمة المرور
        if user.temp_password:
            user.password = user.temp_password
            user.temp_password = None  # إزالة كلمة المرور المؤقتة
            user.verification_code = None  # إزالة الرمز
            user.code_expiration = None
            user.save()
            return Response({"message": "The password has been successfully updated."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "A new password has not been presented."}, status=status.HTTP_400_BAD_REQUEST)

# Admin API  


class AdminRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        if len(data['password']) < 8:
            return Response(
                {"message": "The password must be 8 or more letters."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "This email is already registered please login."},status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message": "Please wait until the previouse attempt ends."}, status=status.HTTP_400_BAD_REQUEST)
            # تحديث السجل القديم
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "The verification code has been sent to your email, please confirm your email within 5 minutes."}, status=status.HTTP_200_OK)


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
                {"message": "The password must be 8 or more letters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "This email is already registered please login."}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"message": "Please wait until the previouse attempt ends."}, status=status.HTTP_400_BAD_REQUEST)
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "The verification code has been sent to your email, please enter it within 5 minutes."}, status=status.HTTP_200_OK)


class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_client:  # التأكد من أن المستخدم عميل
            first_login = user.last_login is None
            token, created = Token.objects.get_or_create(user=user)
            if first_login:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            return Response({"token": token.key, "user_id": user.id,"username": user.username,"first_login": first_login}, status=status.HTTP_200_OK)
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
        
# admin pages

class HasDynamicPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.is_superuser or 
                (required_permission and request.user.has_perm(required_permission))
            )
        )

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [HasDynamicPermission] 
    required_permission = 'users.view_user'
    
class UpdateUserPermissionsView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]  # فقط superuser مسموح له

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        is_staff = request.data.get('is_staff')
        is_superuser = request.data.get('is_superuser')
        is_active = request.data.get('is_active')
        
        if is_staff and user.is_client:
            return Response(
                {"error": "you can't do that for a client"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_staff is not None:
            user.is_staff = is_staff
        if is_superuser is not None:
            user.is_superuser = is_superuser
        if is_active is not None:
            user.is_active = is_active

        user.save()
        return Response({"message": "تم تحديث الصلاحيات بنجاح!"})
    
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]  # يسمح فقط للمستخدمين المسجلين بالوصول
    lookup_field = 'id'

class UpdateAdminPermissions(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [IsAuthenticated,IsSuperUser]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        
        if user.is_client:
            return Response({"error": "you can't do this operation for a client"},status=status.HTTP_403_FORBIDDEN)

        permissions = request.data.get('permissions', [])
        print("الصلاحيات المطلوبة:", permissions)

        permission_objects = Permission.objects.filter(id__in=permissions)
        print("الصلاحيات الفعلية الموجودة في قاعدة البيانات:", permission_objects)

        if permission_objects.count() != len(permissions):
            return Response({"error": "بعض الصلاحيات غير موجودة في النظام."}, status=status.HTTP_400_BAD_REQUEST)

        user.user_permissions.set(permission_objects)
        user.save()

        print("الصلاحيات بعد التحديث:", user.user_permissions.all())

        return Response({"message": "تم تحديث الصلاحيات بنجاح!"}, status=status.HTTP_200_OK)

class UserPermissionsView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        permission = user.user_permissions.values('id', 'codename', 'name')
        return Response({"permissions": list(permission)}, status=200)

class PermissionsListView(APIView):
    def get(self, request):
        permissions = Permission.objects.values('id', 'name')
        return Response(permissions)
    
# details of user
@api_view(['Get'])
def get_logged_in_user(request):
    serializer =UsersSerializer(request.user)
    return Response(serializer.data)

# delete user from superuser
@api_view(['DELETE'])
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return Response(
            {"detail": "you don't have a permission"},
            status= status.HTTP_403_FORBIDDEN
        )
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response(
            {"detail": "user was successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )
    