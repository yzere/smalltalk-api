from csv import list_dialects
from django.contrib import admin
from .models import Circle, Report, Message, User

# Register your models here.

admin.site.register(User)

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ['name', 'admins', 'expireDate']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reason', 'reportedUserID']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['senderUserID', 'reciverUserID']