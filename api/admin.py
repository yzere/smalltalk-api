from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm
    )

from .models import (
    Circle,
    Report, 
    Message, 
    CustomUser
    )



@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ['name', 'admins', 'expireDate']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reason', 'reportedUserID']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['senderUserID', 'reciverUserID']

class CustomUserAdmin(UserAdmin):    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email']

admin.site.register(CustomUser, CustomUserAdmin)