from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import (
    CircleSerializer, 
    ReportSerializer, 
    MessageSerializer,
    CustomUserSerializer
    )

from .models import (
    Circle, 
    Report,
    Message, 
    CustomUser
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