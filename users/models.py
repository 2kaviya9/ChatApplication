from django.db import models

# Create your models here.

from django.contrib.auth.models import  Group, Permission
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Change the related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Change the related_name
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )
    profile = models.ImageField(null = True, blank = True, upload_to="media/profile/")

class UserConnect(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='connections'
    )
    connected_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='connected_to',
        null=True,  
        blank=True 
    )
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='requests_made',
        null=True,  
        blank=True 
    )
    is_approved = models.BooleanField(default=False)
    
class ChatBot(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sender',
        db_index=True
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='receiver',
        db_index=True
    )
    message = models.TextField()
    is_seen = models.BooleanField(default=False, db_index=True)