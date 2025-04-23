from django.urls import path
from .views import RequestPasswordResetView,VerifyAndResetPasswordView,AdminRegisterView,ResendVerificationEmailView,VerifyCodeView, AdminLoginView,AdminLogoutView,ClientRegisterView, ClientLoginView, ClientLogoutView,UserListView, UpdateUserPermissionsView,UserDetailView,UpdateAdminPermissions,UserPermissionsView,PermissionsListView,UserSearchView,get_logged_in_user,delete_user


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
    # admin pages
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('users/<uuid:pk>/update/', UpdateUserPermissionsView.as_view(), name='user-permissions-update'),
    path('user/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:pk>/permissions/', UpdateAdminPermissions.as_view(), name='update-user-permissions'),
    path('users/permissions/', PermissionsListView.as_view(), name='permissions-list'),
    path('user/', get_logged_in_user, name='get_logged_in_user'),
    path('delete_user/<uuid:user_id>/', delete_user, name='delete_user'),
    path('user/<uuid:user_id>/permissions/', UserPermissionsView.as_view(), name='user-permissions'),
]
