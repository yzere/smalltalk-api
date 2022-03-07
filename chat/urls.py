
from django.urls import path

from .views import *

urlpatterns = [
    path('index', index, name='index'),
    path('panel/', panel, name='panel'),
    path('', root, name='root'),

    path('find_session/', find_session, name='find_session'),
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
    path('add_all_waitingroom_to_sessions_circle/', add_all_waitingroom_to_sessions_circle, name='add_all_waitingroom_to_sessions_circle'),
    path('refresh_expire_date/<str:desired_circle_id>/<str:desired_expire_date>/', refresh_expire_date, name='refresh_expire_date'),
    
    path('get_room_id/', get_room_id, name='get_room_id'),
    path('get_room_messages/', get_room_messages, name='get_room_messages'),
    path('close_session/', close_session, name='close_session'),

    path('join_circle/<str:desired_circle>/', join_circle, name='join_circle'),
    path('leave_circle/<str:desired_circle_id>/', leave_circle, name='leave_circle'),
    path('get_user_circles_ids/', get_user_circles_ids, name='get_user_circles_ids'),
    
    path('check_session/', check_session, name='check_session'),

    path('<str:room_name>/', room, name='room')
]
