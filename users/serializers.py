from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
# admin pages

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email','is_client' ,'is_staff', 'is_superuser', 
            'is_delivery_provider','is_active', 'date_joined', 'last_login'
        ]
        
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_email_verified',
            'is_staff', 'is_superuser','is_delivery_provider','is_active',
            'last_login', 'date_joined', 'is_client'
        ]
        
class UserPermissionSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'permissions']