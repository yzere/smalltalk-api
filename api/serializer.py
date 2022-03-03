from .models import (
    Circle, 
    Report, 
    Message, 
    CustomUser,
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

class WaitingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingRoom
        fields = '__all__'

class ActiveSessionSerializer(serializers.ModelSerializer):
    # tu jest problem z wyświetlaniem ActiveSession, kiedy są memberzy. Najprawdopodobniej coś jest nie tak z WaitingRoom
    # >>> session = ActiveSession.objects.get(member1_ID = 4)
    # >>> session.member1_ID
    # <WaitingRoom: 12>
    # >>> session.member1_ID.user_that_want_to_join_ID
    # <CustomUser: 4>
    
    class Meta:
        model = ActiveSession
        fields = ['session_ID', 'member1_ID', 'member2_ID']