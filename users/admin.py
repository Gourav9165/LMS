# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Automatically fetch your active user model (whether it's named User, Member, CustomUser, etc.)
User = get_user_model()

# Register it with the admin site
admin.site.register(User, UserAdmin)