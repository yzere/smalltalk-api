from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm
    )

from .models import (
    CustomUser,
    Circle,
    Report,
    WaitingRoom,
    ActiveSession,
    Message,
    Icebreaker
    )

class CustomUserAdmin(UserAdmin):    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email']

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ['circle_ID']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_ID']

@admin.register(WaitingRoom)
class WaitingRoomAdmin(admin.ModelAdmin):
    list_display = ['room_ID']

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ['session_ID']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_ID']

@admin.register(Icebreaker)
class IcebreakerAdmin(admin.ModelAdmin):
    list_display = ['icebreaker_ID']




