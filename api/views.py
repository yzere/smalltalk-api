from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import (
    CircleSerializer, 
    ReportSerializer, 
    MessageSerializer,
    CustomUserSerializer,
    ProfileSerializer,
    WaitingRoomSerializer,
    ActiveSessionSerializer
    )

from .models import (
    Circle, 
    Report,
    Message, 
    CustomUser,
    Profile,
    WaitingRoom,
    ActiveSession
    )

class CircleViewSet(viewsets.ModelViewSet):
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class WaitingRoomViewSet(viewsets.ModelViewSet):
    queryset = WaitingRoom.objects.all()
    serializer_class = WaitingRoomSerializer

class ActiveSessionViewSet(viewsets.ModelViewSet):
    queryset = ActiveSession.objects.all()
    serializer_class = ActiveSessionSerializer