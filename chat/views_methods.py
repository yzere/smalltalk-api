from django.shortcuts import render
from api.models import ActiveSession, Message, Profile, WaitingRoom, CustomUser
from random import choice
from django.db.models import Q

def check_if_session_free(request, desired_session_id):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    free_session = ActiveSession.objects.filter(Q(session_ID = desired_session_id), (Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True))).values_list('pk', flat=True)
    # freeSessions += ActiveSession.objects.filter(member1_ID__isnull=True).values_list('pk', flat=True)
    if not free_session:
        return None
    return free_session

def find_free_sessions():
    # user_id = request.user.user_ID
    # user = CustomUser.objects.get(pk=user_id)
    # isWaiting = WaitingRoom.objects.filter(user_that_want_to_join_ID=user)
    # if not isWaiting:
    #     addWaiting = WaitingRoom(user_that_want_to_join_ID=user)
    #     addWaiting.save()
    if not ActiveSession.objects.exists():
        return (None, None)
    freeSessions = ActiveSession.objects.filter(Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True)).values_list('pk', flat=True)
    # freeSessions += ActiveSession.objects.filter(member1_ID__isnull=True).values_list('pk', flat=True)
    if not freeSessions:
        return (None, None)
    return freeSessions

def find_user_session(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    if not ActiveSession.objects.exists():
        return (None, None)
    if ActiveSession.objects.filter(member2_ID=user.user_ID):
        session = ActiveSession.objects.get(member2_ID=user.user_ID)
        member = 2

    elif ActiveSession.objects.filter(member1_ID=user.user_ID):
        session = ActiveSession.objects.get(member1_ID=user.user_ID) 
        member = 1 

    else:
        session = None
        member = None
    
    return (session, member)

def find_user_waitingroom_object(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)

    if WaitingRoom.objects.filter(user_that_want_to_join_ID = user_id):
        user_object = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)
        return user_object
    else:
        return None

def choose_session(sessions, **kwargs):
    #magiczny algorytm doboru sesji
    return ActiveSession.objects.get(session_ID = choice(sessions)) 
    # choice(sessions)