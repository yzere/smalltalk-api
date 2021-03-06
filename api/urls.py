from rest_framework import routers
from django.urls import include, path
from .views import (
    CircleViewSet, 
    ReportViewSet, 
    MessageViewSet, 
    CustomUserViewSet,
    ProfileViewSet,
    WaitingRoomViewSet,
    ActiveSessionViewSet
    )

router = routers.DefaultRouter()
router.register(r'circles', CircleViewSet),
router.register(r'reports', ReportViewSet),
router.register(r'messages', MessageViewSet),
router.register(r'users', CustomUserViewSet),
router.register(r'profile', ProfileViewSet),
router.register(r'WaitingRoom', WaitingRoomViewSet),
router.register(r'ActiveSession', ActiveSessionViewSet)

urlpatterns = [
    path('models/', include(router.urls)),
    # For further development
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('auth/', include('rest_auth.urls')),    
    path('auth/register/', include('rest_auth.registration.urls'))
]