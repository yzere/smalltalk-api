from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializer import (
    CircleSerializer, 
    ReportSerializer, 
    MessageSerializer,
    CustomUserSerializer,
    CircleUsersSerializer, 
    CircleReportsSerializer
    )

from .models import (
    Circle, 
    Report,
    Message, 
    CustomUser, 
    CircleUsers,
    CircleReports)

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

class CircleUsersViewSet(viewsets.ModelViewSet):
    queryset = CircleUsers.objects.all()
    serializer_class = CircleUsersSerializer

class CircleReportsViewSet(viewsets.ModelViewSet):
    queryset = CircleReports.objects.all()
    serializer_class = CircleReportsSerializer