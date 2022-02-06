from rest_framework import routers
from django.urls import include, path
from .views import CircleViewSet, ReportViewSet, MessageViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'circles', CircleViewSet),
router.register(r'reports', ReportViewSet),
router.register(r'messages', MessageViewSet),
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]