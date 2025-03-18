from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    """
    يتيح الإذن فقط للـ superuser إمكانية تعديل الصلاحيات
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
