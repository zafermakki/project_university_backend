from django.urls import path
from .views import RequestPasswordResetView,VerifyAndResetPasswordView,AdminRegisterView,ResendVerificationEmailView,VerifyCodeView, AdminLoginView,AdminLogoutView,ClientRegisterView, ClientLoginView, ClientLogoutView


urlpatterns = [
    path('register/', AdminRegisterView.as_view(), name='register'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    path('resend-verifycodeview/', VerifyCodeView.as_view(), name='resend-verifycodeview'),
    path('login/', AdminLoginView.as_view(), name='login'),
    path('logout/', AdminLogoutView.as_view(), name='logout'),
    # client
    path('client/register/', ClientRegisterView.as_view(), name='register'),
    path('client/login/', ClientLoginView.as_view(), name='login'),
    path('client/logout/', ClientLogoutView.as_view(), name='logout'),
    # forget password 
    path('password-reset/', RequestPasswordResetView.as_view(), name='password-reset'),
    path('make-reset/', VerifyAndResetPasswordView.as_view(), name='make-reset'),
]
