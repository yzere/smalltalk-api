from django.shortcuts import render
from api.models import ActiveSession, Message, Profile, WaitingRoom, CustomUser, Circle
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
        return None
    
    freeSessions = ActiveSession.objects.filter(Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True)).values_list('pk', flat=True)
    # freeSessions += ActiveSession.objects.filter(member1_ID__isnull=True).values_list('pk', flat=True)
    if not freeSessions:
        return None
    return freeSessions

def find_free_sessions_circle_match(request):                                       # bardzo jestem ciekawy, czy to działa, jeśli działa, to chyba można podmienić z find_free_sessions, ale nie wiem, czy gdzieś nie jest jeszcze do czegoś innego używana tamta
    user_id = request.user.user_ID                                                  # Wygląda na to, że działa
    user = CustomUser.objects.get(pk=user_id)
    if not ActiveSession.objects.exists():
        return None
    usersCircles = Circle.objects.filter(users_IDs=user).values_list('pk', flat=True)
    freeSessions = False
    i = 0
    while not freeSessions:
        try:
            freeSessions = ActiveSession.objects.filter(Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True), circle = Circle.objects.get(pk = usersCircles[i])).values_list('pk', flat=True)
        except ActiveSession.DoesNotExist:
            pass
        if i < len(usersCircles)-1:
            i += 1
        else:
            break

    if not freeSessions:
        return None
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

def find_user_waitingroom_object_by_ID(user_id):
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