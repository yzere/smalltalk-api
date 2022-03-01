
from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('panel/', panel, name='panel'),

    # path('find_session/', find_session, name='find_session'),
    path('leave_session/', leave_session, name='leave_session'),
    path('join_session/', join_session, name='join_session'),

    path('join_waitingroom/', join_waitingroom, name='join_waitingroom'),
    path('leave_waitingroom/', leave_waitingroom, name='leave_waitingroom'),

    path('instant_match/', instant_match, name='instant_match'),
    path('instant_abort/', instant_abort, name='instant_abort'),

    # path('add_user_to_session/<str:desired_session_id>/<str:desired_user_id>/', add_user_to_session, name='add_user_to_session'),
    path('remove_user_from_session/<str:desired_session_id>/<str:desired_user_id>/', remove_user_from_session, name='remove_user_from_session'),
    path('add_user_to_session/<str:desired_session_id>/<str:desired_user_id>/', add_user_to_session, name='add_user_to_session'),
    path('add_all_waitingroom_to_sessions/', add_all_waitingroom_to_sessions, name='add_all_waitingroom_to_sessions'),
    
    path('get_room_id/', get_room_id, name='get_room_id'),
    path('get_room_messages/', get_room_messages, name='get_room_messages'),
    path('close_session/', close_session, name='close_session'),
    path('<str:room_name>/', room, name='room')
]
