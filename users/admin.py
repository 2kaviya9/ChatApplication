from django.contrib import admin
from users.models import User

from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)