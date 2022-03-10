from django.forms.models import model_to_dict
from django.utils import timezone
import datetime
from tabnanny import check
from django.shortcuts import render, get_object_or_404
from api.models import ActiveSession, Message, WaitingRoom, CustomUser, Circle
from random import choice, choices
import string
import copy
import math
import json
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from chat.views_methods import (    find_free_sessions,
                                    find_user_session,
                                    find_user_waitingroom_object,
                                    choose_session,
                                    check_if_session_free,
                                    find_user_waitingroom_object_by_ID,
                                    find_free_sessions_circle_match
                                )

#   FLOW UŻYTKOWNIKA:
#
#   /join_waitingroom
#   ...czekanie na odpowiedź serwera, z przydzielonym numerem pokoju
#   ...pisanie na czacie (patrz: consumers.py, tam cała mechanika)
#   /leave_session (wyjście z pokoju) - wyjście z sesji nie usuwa waitingroomu
#   /leave_waitingroom (wyjście z poczekalni)
#
#   /get_room_id - pobieranie ID przydzielonego pokoju



response_object = {}
#DEKORATORY służące do zbierania odpowiedzi od poszczególnych funkcji składowych (de facto widoków)
#trzeba naprawić tak, aby poszczególne zapytania również zwracały funkcje
def gather_response(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)

        if type(res) != dict:
            #zakładamy że jest tym: <class 'django.http.response.JsonResponse'>
            #dzieje się to po to, byśmy mogli w funkcjach zwracać dobrą odpowiedź json
            json_res = copy.deepcopy(res)
            res = res._container[0].decode('utf-8')
            res = json.loads(res)

        if type(res) == dict:
            for key in res.keys():
                if key in response_object.keys():
                    if type(response_object[key]) == list: 
                        response_object[key].append(res[key])
                    else:
                        response_object[key] = [res[key]]
                else:
                    response_object[key] = [res[key]]
        return json_res
    return wrapper

def clear_response(func):
    def wrapper(*args, **kwargs):
        global response_object
        res = copy.deepcopy(response_object)
        response_object = {}
        return func(res)
    return wrapper

def check_if_staff(func):
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
        except BaseException as err:
            return JsonResponse({
                'error': f'ERROR: {err}'
            })
        
        user_id = request.user.user_ID
        user = CustomUser.objects.get(pk=user_id)
        if user.is_staff:
            return func(*args, **kwargs)
        else:
            return JsonResponse({
                'error': f'Too low permission level.'
            })
    return wrapper

@clear_response
def send_response(res):
    return JsonResponse(res)

#VIEWS
# Create your views here.
@gather_response
def find_session(request):
    return JsonResponse({'session_id': 1})

@login_required                                                                                         # login_required też pododaję
@gather_response
def leave_session(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    if ActiveSession.objects.filter(member2_ID=user.user_ID):
        session = ActiveSession.objects.get(member2_ID=user.user_ID)
        session.member2_ID = None
        session_id = session.session_ID
        session.save()

        message = f'User {user_id} has left session {session_id}.'

    elif ActiveSession.objects.filter(member1_ID=user.user_ID):
        session = ActiveSession.objects.get(member1_ID=user.user_ID)  
        session.member1_ID = None
        session_id = session.session_ID
        session.save()

        message = f'User {user_id} has left session {session_id}.'

    else:
        message = f'User {user_id} has no active sessions.'
    
    
    # print(ActiveSession.objects.filter(member2_ID=user.user_ID))
    return JsonResponse(
        {   
            'message': message
        })

@login_required                                                                                         # login_required też pododaję
#@gather_response
def join_waitingroom(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    now = timezone.now()
    try:
        circles = Circle.objects.filter(users_IDs=user).values_list('pk', flat=True)
    except Circle.DoesNotExist:
        return JsonResponse({
            'message': f'User {user_id} has not got any circles.'
        })
    newCircles = []
    for cir in circles:
        CirObject = Circle.objects.get(pk = cir)
        if CirObject.expire_date > now:
            newCircles.append(CirObject.pk)
    if newCircles:
        circle = choice(newCircles)
        circle = Circle.objects.get(pk=circle)
    else:
        return JsonResponse({   
            'message': f'User {user_id} has no non-expired circles.'
        })

    if WaitingRoom.objects.filter(user_that_want_to_join_ID = user_id):
        message = f'User {user_id} is already in waiting room.'
    else:
        new_waiting_room = WaitingRoom(user_that_want_to_join_ID = user, circle=circle)
        new_waiting_room.save()
        # waiting_room.save()
        message = f'User {user_id} has been added to the waiting room.'

    return JsonResponse({   
            'message': message
        })

@login_required                                                                                         # login_required też pododaję
@gather_response
def leave_waitingroom(request):

    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    
    if WaitingRoom.objects.filter(user_that_want_to_join_ID = user_id):
        waiting_room = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)
        waiting_room.delete()
        # waiting_room.save()
        message = f'User {user_id} has left the waiting room.'
    else:
        message = f'User {user_id} is not in waiting room.'
    
    return JsonResponse({   
            'message': message

        })

@login_required                                                                     # Już zapomniałem o istnieniu tej funkcji
@gather_response
def join_session(request):

    WAITINGROOM_NEEDED = True #jak na razie i tak trzeba w nim być
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    message = 'placeholder'
    # Check WaitingRoom
    try:
        waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user)
        waitingroom_ID = model_to_dict(waitingroom, fields='circle')
    except WaitingRoom.DoesNotExist:
        #join_waitingroom(request)               # Jeżeli chcemy mieć automatyczne dodawanie do WaitingRoom
        message = f'Prior to being added to the session you need to join the waitingroom.'              # Jeżeli chcemy po prostu walnąć errora
        waitingroom = False
    # Chyba może się przydać ^
    # Do testowania (najpierw trzeba dodać circle)
    
    usersCircle = Circle.objects.get(pk=waitingroom_ID['circle'])

    if not ActiveSession.objects.exists() and waitingroom:
        new_session = ActiveSession(member1_ID = find_user_waitingroom_object(request), circle = usersCircle)         
        new_session.save()
        session_id = new_session.session_ID

        #waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
        waitingroom.active_sessions_IDs = new_session
        waitingroom.save()

        message = f'Created new session {session_id} and added user {user_id}.'
        
    elif find_user_session(request)[1] != None and waitingroom:
        message = f'User {user_id} already in session of id {find_user_session(request)[0]}'
    else: 
        free_sessions = find_free_sessions_circle_match(request)                                                                         
        if find_user_waitingroom_object(request) == None and WAITINGROOM_NEEDED:
            #print('z waiti')
            message = f'Prior to being added to the session you need to join the waitingroom.'
        
        elif not free_sessions and waitingroom:
            #sprawdzanie warunku bycia w waitingroomie                                              Trzeba ogarnąć, czy nie sprawdzamy warunku 2x
            #try:
            #    waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user)
            #except WaitingRoom.DoesNotExist:
            #    waitingroom = False
            
            if waitingroom:
                new_session = ActiveSession(member1_ID = waitingroom, circle = usersCircle)
                new_session.save()
                session_id = new_session.session_ID

            #waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
                waitingroom.active_sessions_IDs = new_session
                waitingroom.save()

                message = f'Created new session {session_id} and added user {user_id}.'
            elif not waitingroom:
                message = f'Prior to being added to the session you need to join the waitingroom.'
        
        else:
            chosen_session = choose_session(free_sessions)
            print(free_sessions, chosen_session)
            if chosen_session.member1_ID == None:
                chosen_session.member1_ID = find_user_waitingroom_object(request)
            else:
                chosen_session.member2_ID = find_user_waitingroom_object(request)
            # chosen_session[0][f'member{chosen_session[1]}_ID'] = user_id
            chosen_session.save()
            
            session_id = chosen_session.session_ID
            #waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
            waitingroom.active_sessions_IDs = chosen_session
            waitingroom.save()
            
            
            message = f'Chosen session {session_id} and added user {user_id}.'

    # print(ActiveSession.objects.filter(member2_ID=user.user_ID))
    return JsonResponse({   
            'message': message
        })

@check_if_staff                                                         # Żeby ktoś się nie dodał przypadkiem do nie losowej sesji
@gather_response
def add_user_to_session(request, **kwargs):
    #/chat/add_user_to_session/<session_id>/    <user_id>
    WAITINGROOM_NEEDED = True
    print(f'REQUEST: {request}')
    if int(kwargs['desired_user_id']):
        user_id = int(kwargs['desired_user_id'])
        user = get_object_or_404(CustomUser, pk=user_id)

        message = 'from desired user'
        # if not user:
        #     message = f'User {user_id} not found.'

        if (ActiveSession.objects.filter(member1_ID = user_id).exists() or 
        ActiveSession.objects.filter(member2_ID = user_id).exists()):
            message = f'User {user_id} already in session.'

        else:
            m1 = ActiveSession.objects.filter(member1_ID = None)
            if not m1:
                m2 = ActiveSession.objects.filter(member2_ID = None)
                if not m2 :
                    #sprawdzanie warunku bycia w waitingroomie
                    new_session = ActiveSession(member1_ID = find_user_waitingroom_object_by_ID(user_id))
                    new_session.save()
                    session_id = new_session.session_ID

                    waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
                    waitingroom.active_sessions_IDs = new_session
                    waitingroom.save()

                    message = f'Created new session {session_id} and added user {user_id}.'
                else:
                    session = m2.last()
                    session_id = session.session_ID
                    session.member2_ID = find_user_waitingroom_object_by_ID(user_id)
                    message = f'Found {session_id} and added user {user_id}.'
            else:
                session = m1.last()
                session_id = session.session_ID
                session.member1_ID = find_user_waitingroom_object_by_ID(user_id)
                message = f'Found {session_id} and added user {user_id}.'
            session.save()

    else:
        user_id = request.user.user_ID
        user = CustomUser.objects.get(pk=user_id)
    

        if int(kwargs['desired_session_id']):
            desired_session_id = kwargs['desired_session_id']
        else:
            return JsonResponse({'error' : 'Bad URL!'})

        message = ''
        print(desired_session_id)

        if find_user_session(request)[1] != None:
            message = f'User {user_id} already in session of id {find_user_session(request)[0]}'
        else: 
            free_session = check_if_session_free(request, desired_session_id)
            if find_user_waitingroom_object(request) == None and WAITINGROOM_NEEDED:
                print('z waiti')
                message = f'Prior to being added to the session you need to join the waitingroom.'

            #jeżeli dana sesja nie jest wolna
            elif not free_session:
                #sprawdź, czy jest zajęta, czy jeszcze nie stworzona 
                if not ActiveSession.objects.get(session_ID = desired_session_id):
                    new_session = ActiveSession(member1_ID = find_user_waitingroom_object_by_ID(user_id), session_ID = desired_session_id)
                    new_session.save()
                    session_id = new_session.session_ID

                    waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
                    waitingroom.active_sessions_IDs = new_session
                    waitingroom.save()

                    message = f'Created new session {session_id} and added user {user_id}.'
                else:
                    message = f'Desired session {session_id} is full!.'

            #jeżeli sesja jest wolna (czyli ma co najmniej jedno wolne miejsce), dodaj tam użytkownika
            else:
                chosen_session = ActiveSession.objects.get(session_ID = desired_session_id)
                if chosen_session.member1_ID == None:
                    chosen_session.member1_ID = find_user_waitingroom_object(request)
                else:
                    chosen_session.member2_ID = find_user_waitingroom_object(request)
                # chosen_session[0][f'member{chosen_session[1]}_ID'] = user_id
                chosen_session.save()
                
                session_id = chosen_session.session_ID
                waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
                waitingroom.active_sessions_IDs = chosen_session
                waitingroom.save()

                message = f'Added user {user_id} to session {session_id}'

    return JsonResponse({'message' : message})

@check_if_staff                                                                                 # To chyba też zadanie dla nas
@gather_response
def remove_user_from_session(request, **kwargs):
    #/chat/remove_user_from_session/<session_id>/<user_id>
    

    remove_all_users = False
    message = ''
    members = []
    if kwargs['desired_session_id']:
        desired_session_id = kwargs['desired_session_id']
    else:
        return JsonResponse({'error' : 'Bad URL!'})

    if kwargs['desired_user_id']:
        desired_user_id = kwargs['desired_user_id']
    else:
        remove_all_users = True

    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)


    if remove_all_users:
        session = ActiveSession.objects.get(session_ID = desired_session_id)
        members = [session.member1_ID, session.member2_ID]
        session.member1_ID = None
        session.member2_ID = None
        session_id = session.session_ID
        session.save()
        message = f'Users {members} have been removed from session {session_id}.'
    else:
        if ActiveSession.objects.filter(member2_ID=desired_user_id):
            session = ActiveSession.objects.get(member2_ID=desired_user_id)
            members = [session.member2_ID]
            session.member2_ID = None
            session_id = session.session_ID
            session.save()

            message = f'User {members} has been removed from session {session_id}.'

        elif ActiveSession.objects.filter(member1_ID=desired_user_id):
            session = ActiveSession.objects.get(member1_ID=desired_user_id)  
            members = [session.member1_ID]
            session.member1_ID = None
            session_id = session.session_ID
            session.save()

            message = f'User {members} has been removed from session {session_id}.'

        else:
            message = f'User {desired_user_id} has no active sessions.'
        
    for member in members:
        try:
            waiting_room = WaitingRoom.objects.get(room_ID = member.room_ID)
            waiting_room.delete()
        except BaseException as err:
            print(err)

    return JsonResponse(
        {   
            'message': message
        })

@check_if_staff                                                                                 # Raczej się przyda
@gather_response
def add_all_waitingroom_to_sessions(request):
    message = ''
    if not WaitingRoom.objects.exists():
        message = f'Aborting operation, there are no waiting users!'
    waitingrooms = WaitingRoom.objects.filter(active_sessions_IDs = None)
    print(f'waitingrooms: {waitingrooms}')
    if not waitingrooms:
        return JsonResponse({'message': 'No users waiting for match.'})

    users_to_match = waitingrooms.count()
    if ActiveSession.objects.exists():
        sessions = find_free_sessions()
        if not sessions:
            return JsonResponse({'message': 'No free sessions'})
        free_seats = 0
        for ses in sessions:
            session_object = ActiveSession.objects.get(session_ID = ses)
            if session_object.member1_ID == None:
                free_seats += 1
            if session_object.member2_ID == None:
                free_seats += 1
            print(free_seats)

        if users_to_match > free_seats:
            lacking_seats =  users_to_match - free_seats
            lacking_sessions = math.ceil(lacking_seats/2)
            print(f'Preparing {lacking_sessions} sessions...')
        else:
            lacking_sessions = 0
        message = f'There are {free_seats} free seats'
    else:  
        lacking_sessions = math.ceil(waitingrooms.count()/2)
        print(f'Preparing {lacking_sessions} sessions...')

    for i in range(lacking_sessions):
        ses = ActiveSession()
        print(f'Preparing {lacking_sessions} sessions...')
        message += f'Created session of id {ses.session_ID}'
        ses.save()
    
    free_sessions = find_free_sessions()
    # print(free_sessions)
    if free_sessions:
        sessions = ActiveSession.objects.filter(pk__in=free_sessions)
        stop_flag = False
        pointer = 0
        members = {0: 'member1_ID', 1: 'member2_ID'}
        for j in range(len(sessions)):
            ses = sessions[j]
            for k in range(2):
                if getattr(ses, members[k]) == None:
                    if pointer > len(waitingrooms)-1:
                        break
                    waitingroom = waitingrooms[pointer]
                    setattr(ses, members[k], waitingroom)
                    waitingroom.active_sessions_IDs = ses
                    waitingroom.save()
                    pointer += 1 
                    if pointer > len(waitingrooms)-1:
                        stop_flag = True
                        break
            
            ses.save()
  
    message = 'Everything done.'
    return JsonResponse({'message': message})

@check_if_staff                                                                         # Zdecydowanie się przyda
def add_all_waitingroom_to_sessions_circle(request):
    message = ''
    if not WaitingRoom.objects.exists():
        message = f'Aborting operation, there are no waiting users!'

    circlesWaiting = WaitingRoom.objects.all().values_list('circle', flat=True)
    circlesWaiting = list(dict.fromkeys(circlesWaiting))
    for circleWaiting in circlesWaiting:
        circle = Circle.objects.get(pk=circleWaiting)
        waitingrooms = WaitingRoom.objects.filter(active_sessions_IDs = None, circle=circle)
        users_to_match = waitingrooms.count()
        if ActiveSession.objects.exists():
            sessions = ActiveSession.objects.filter(Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True), circle=circle).values_list('pk', flat=True)
            free_seats = 0
            for ses in sessions:
                session_object = ActiveSession.objects.get(session_ID = ses)
                if session_object.member1_ID == None:
                    free_seats += 1
                if session_object.member2_ID == None:
                    free_seats += 1
            if users_to_match > free_seats:
                lacking_seats =  users_to_match - free_seats
                lacking_sessions = math.ceil(lacking_seats/2)
                print(f'Preparing {lacking_sessions} sessions...')
            else:
                lacking_sessions = 0
            message = f'There are {free_seats} free seats'
        else:  
            lacking_sessions = math.ceil(waitingrooms.count()/2)
            print(f'Preparing {lacking_sessions} sessions...')
        for i in range(lacking_sessions):
            ses = ActiveSession(circle=circle)
            print(f'Preparing {lacking_sessions} sessions...')
            message += f'Created session of id {ses.session_ID}'
            ses.save()
        free_sessions = sessions = ActiveSession.objects.filter(Q(member2_ID__isnull=True) | Q(member1_ID__isnull=True), circle=circle).values_list('pk', flat=True)
        
        if free_sessions:
            sessions = ActiveSession.objects.filter(pk__in=free_sessions)
            stop_flag = False
            pointer = 0
            members = {0: 'member1_ID', 1: 'member2_ID'}
            for j in range(len(sessions)):
                ses = sessions[j]
                for k in range(2):
                    if getattr(ses, members[k]) == None:
                        if pointer > len(waitingrooms)-1:
                            break
                        waitingroom = waitingrooms[pointer]
                        setattr(ses, members[k], waitingroom)
                        waitingroom.active_sessions_IDs = ses
                        waitingroom.save()
                        pointer += 1 
                        if pointer > len(waitingrooms)-1:
                            stop_flag = True
                            break
                ses.save()
    message = 'Everything done.'
    return JsonResponse({'message': message})

@login_required                                                                                         # login_required też pododaję
def get_room_id(request):
    user_id = request.user.user_ID
    user = get_object_or_404(CustomUser, pk=user_id)

    session_tuple = find_user_session(request)
    session = session_tuple[0]
    if session == None:
        message = f'User {user_id} not matched to session yet.'
        
    else:
        message = session.session_ID
    return JsonResponse({'message': message})

@login_required                                                                                         # login_required też pododaję
def get_room_messages(request):
    user_id = request.user.user_ID
    user = get_object_or_404(CustomUser, pk=user_id)

    session = find_user_session(request)[0]
    if session:
        session_id = session.session_ID

    msg_list = []
    messages = Message.objects.filter(active_session_ID=session_id)
    for msg in messages:
        msg_list.append({
            'id': msg.message_ID,
            'message': msg.content,
            'username': 'anonymous' 
        }) 
    
    return JsonResponse({'content': msg_list})

# Nie wiem czy tutaj dawać jakiś dekorator
def close_session(request): #czyści sesję z wiadomości i przygotowuje do następnego matcha
    user_id = request.user.user_ID
    user = get_object_or_404(CustomUser, pk=user_id)
    session = find_user_session(request)[0]
    if session:
        session_id = session.session_ID
        messages = Message.objects.filter(active_session_ID=session_id)
        messages.delete()
        remove_user_from_session(request, desired_session_id=session_id, desired_user_id=False)
        session.delete() #opcjonalne
        return JsonResponse({'message': 'Messages deleted and session cleared.'})
    else:
        return JsonResponse({'message': 'No session to close.'})


@login_required                                                                                         # login_required też pododaję
def join_circle(request, **kwargs):
    #/chat/join_circle/<circle_code>
    message = ''
    if kwargs['desired_circle']:
        desired_circle = kwargs['desired_circle']
    else:
        return JsonResponse({'error' : 'Bad URL!'})
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    now = timezone.now()
    try:
        circle = Circle.objects.get(code = desired_circle)
    except Circle.DoesNotExist:
        message = f'Circle {desired_circle} not found.'
        return JsonResponse({   
            'message': message
        })
    maxU = circle.users_IDs.all()

    if circle.expire_date < now:
        return JsonResponse({   
            'message': f'Circle {desired_circle} is expired.'
        })
    
    if circle.max_users > len(maxU):
        user.user_circles_IDs.add(circle)
        circle.users_IDs.add(user)
        message = f'User {user_id} has been added to the circle {desired_circle}.'
    else:
        message = f'Circle {desired_circle} has no free sits.'
    
    return JsonResponse({   
            'message': message
        })

@login_required                                                                                         # login_required też pododaję
def leave_circle(request, **kwargs):
    #/chat/join_circle/<circle_id>
    message = ''
    if kwargs['desired_circle_id']:
        desired_circle_id = kwargs['desired_circle_id']
    else:
        return JsonResponse({'error' : 'Bad URL!'})
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    try:
        circle = Circle.objects.get(pk = desired_circle_id)
    except Circle.DoesNotExist:
        message = f'Circle {desired_circle_id} not found.'
        return JsonResponse({   
            'message': message
        })
    user.user_circles_IDs.remove(circle)
    circle.users_IDs.remove(user)
    message = f'User {user_id} has been removed from the circle {desired_circle_id}.'
    
    return JsonResponse({   
            'message': message
        })

@check_if_staff                                                                                 # Jak na razie chyba też nasza funkcja
def refresh_expire_date(request, **kwargs):
    # chat/refresh_expire_date/<circle_id>/<new_expire_date>
    # expire date in format "YYYY-MM-DD-HH-MM-SS"
    # circle id bez problemu mogę zamienić na dotychczasowy circle code
    if kwargs['desired_circle_id']:
        desired_circle_id = kwargs['desired_circle_id']
    else:
        return JsonResponse({'error' : 'Bad URL! You have to specify desired circle.'})

    if kwargs['desired_expire_date']:
        desired_expire_date = kwargs['desired_expire_date']
    else:
        return JsonResponse({'error' : 'Bad URL! You have to specify valid expire date.'})
    
    try:
        circle = Circle.objects.get(pk=desired_circle_id)
    except Circle.DoesNotExist:
        return JsonResponse({'error' : f'Bad URL! Circle {desired_circle_id} not found'})
    
    newDate = desired_expire_date.split("-")
    dateToSave = datetime.datetime(int(newDate[0]), int(newDate[1]), int(newDate[2]), int(newDate[3]), int(newDate[4]), int(newDate[5]))
    circle.expire_date = dateToSave
    while True:
        code = ''.join(choices(string.ascii_uppercase + string.digits, k=8))
        if Circle.objects.filter(code=code).count() == 0:
            break
    circle.code = code
    circle.save()
    
    return JsonResponse({'message' : f'Expire date in circle {desired_circle_id} changed to {desired_expire_date}. New circle code: {code}'})
    

#Paczki
@check_if_staff                                                             # chyba też
def instant_match(request):
    join_waitingroom(request)
    join_session(request)
    return send_response()

@login_required                                                                                         # A tutaj też dam
def instant_abort(request):
    leave_session(request)
    leave_waitingroom(request)
    return send_response()


def room(request, room_name):
    room = ActiveSession.objects.filter(session_ID=room_name).first()
    msg = []

    if room:
        msg = Message.objects.filter(active_session_ID=room)
    else:
        room = ActiveSession(session_ID=room_name)
        room.save()

    return render(request, 'chatroom.html', {
        'room_name': room_name
    })

@check_if_staff                                                         # na wszelki wypadek
def root(request):

    return render(request, 'base.html', {})