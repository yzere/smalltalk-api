from .models import (
    Circle, 
    Report, 
    Message, 
    CustomUser, 
    CircleReports, 
    CircleUsers
    )
    
from rest_framework import serializers
# JWT Stuff
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = '__all__'

class CircleReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleReports
        fields = '__all__'

class CircleUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleUsers
        fields = '__all__'


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'last_login', 'date_joined', 'is_staff')