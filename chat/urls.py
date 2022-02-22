
from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),

    path('find_session/', find_session, name='find_session'),
    path('leave_session/', leave_session, name='leave_session'),
    path('join_session/', join_session, name='join_session'),

    path('join_waitingroom/', join_waitingroom, name='join_waitingroom'),
    path('leave_waitingroom/', leave_waitingroom, name='leave_waitingroom'),

    path('instant_match/', instant_match, name='instant_match'),
    path('instant_abort/', instant_abort, name='instant_abort'),
    path('<str:room_name>/', room, name='room')
]
