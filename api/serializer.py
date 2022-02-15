from .models import (
    Circle, 
    Report, 
    Message, 
    CustomUser,
    Profile,
    WaitingRoom,
    ActiveSession
    )
    
from rest_framework import serializers
# JWT Stuff
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class WaitingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingRoom
        fields = '__all__'

class ActiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveSession
        fields = '__all__'