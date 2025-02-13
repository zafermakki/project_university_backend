from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
    PermissionsMixin,
    Permission,Group
)
from django.contrib.auth.validators import UnicodeUsernameValidator
import uuid

from django.utils.timezone import now
from datetime import timedelta

class User(AbstractUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key= True,
        editable= False,
        default= uuid.uuid4
    )
    username = models.CharField(
        max_length= 250,    
        # unique=True,
        validators= [UnicodeUsernameValidator],
    )
    email = models.EmailField(
        max_length= 250,
        unique= True
    )
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expiration = models.DateTimeField(null=True, blank=True)
    temp_password = models.CharField(max_length=128, null=True, blank=True)  
    groups = models.ManyToManyField(
        Group, related_name= 'users', related_query_name= 'user' 
    )
    Permissions = models.ManyToManyField(
        Permission, related_name= 'users', related_query_name= 'user' 
    )
    
    is_superuser = models.BooleanField(default= False)
    is_staff = models.BooleanField(default= False)
    is_active = models.BooleanField(default= True)
    last_login = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(
        auto_now_add= True
    )
    is_client = models.BooleanField(default= False)
    
    objects = UserManager()
    
    # REQUIRED_FIELDS = ['email']
    REQUIRED_FIELDS = []
    
    USERNAME_FIELD = 'email'
    # USERNAME_FIELD = 'username'
    
    class Meta:
        db_table = "users"

class PendingUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=250, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_client = models.BooleanField(default= False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expiration = models.DateTimeField(null=True, blank=True)
    

    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=5)
    
    def is_code_valid(self, code):
        return self.verification_code == code and now() < self.code_expiration
