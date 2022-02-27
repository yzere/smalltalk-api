
from tabnanny import check
from django.shortcuts import render, get_object_or_404
from api.models import ActiveSession, Message, Profile, WaitingRoom, CustomUser, Circle
from random import choice
import copy
import math
import json
from django.http import JsonResponse
from chat.views_methods import ( find_free_sessions,
 find_user_session,
 find_user_waitingroom_object,
 choose_session,
 check_if_session_free,
 find_user_waitingroom_object_by_ID
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

@gather_response
def join_session(request):

    WAITINGROOM_NEEDED = True #jak na razie i tak trzeba w nim być
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    message = 'placeholder'
    
    if not ActiveSession.objects.exists():
        new_session = ActiveSession(member1_ID = find_user_waitingroom_object(request))
        new_session.save()
        session_id = new_session.session_ID

        waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
        waitingroom.active_sessions_IDs = new_session
        waitingroom.save()

        message = f'Created new session {session_id} and added user {user_id}.'
        
    elif find_user_session(request)[1] != None:
        message = f'User {user_id} already in session of id {find_user_session(request)[0]}'
    else: 
        free_sessions = find_free_sessions()
        if find_user_waitingroom_object(request) == None and WAITINGROOM_NEEDED:
            print('z waiti')
            message = f'Prior to being added to the session you need to join the waitingroom.'
        
        elif not free_sessions:
            #sprawdzanie warunku bycia w waitingroomie
            new_session = ActiveSession(member1_ID = user)
            new_session.save()
            session_id = new_session.session_ID

            waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
            waitingroom.active_sessions_IDs = new_session
            waitingroom.save()

            message = f'Created new session {session_id} and added user {user_id}.'
        
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
            waitingroom = WaitingRoom.objects.get(user_that_want_to_join_ID = user_id)            
            waitingroom.active_sessions_IDs = chosen_session
            waitingroom.save()
            
            
            message = f'Chosen session {session_id} and added user {user_id}.'

    # print(ActiveSession.objects.filter(member2_ID=user.user_ID))
    return JsonResponse({   
            'message': message
        })

@gather_response
def join_waitingroom(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)

    if WaitingRoom.objects.filter(user_that_want_to_join_ID = user_id):
        message = f'User {user_id} is already in waiting room.'
    else:
        new_waiting_room = WaitingRoom(user_that_want_to_join_ID = user)
        new_waiting_room.save();
        # waiting_room.save()
        message = f'User {user_id} has been added to the waiting room.'
    
    return JsonResponse({   
            'message': message
        })

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
            waiting_room.delete();
        except BaseException as err:
            print(err)


        # waiting_room.save()
        # print(f'member {member}')
        # print(f'member_user {member_user}')
        
    #     if WaitingRoom.objects.filter(user_that_want_to_join_ID = member_user):
    #         waiting_room = WaitingRoom.objects.get(user_that_want_to_join_ID = member_user)
    #         waiting_room.delete()
    #         # waiting_room.save()
    #         message += f'User {member} has left the waiting room.'
    #     else:
    #         message += f'User {member} is not in waiting room.'
    
    # # print(ActiveSession.objects.filter(member2_ID=user.user_ID))
    # print (message)
    return JsonResponse(
        {   
            'message': message
        })

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
    # sessions = ActiveSession.objects.all()
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


#Paczki
def instant_match(request):
    join_waitingroom(request)
    join_session(request)
    return send_response()


def instant_abort(request):
    leave_session(request)
    leave_waitingroom(request)
    return send_response()


def index(request):
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)
    userProfile = Profile.objects.get(pk=user)
    usersCircles = Circle.objects.filter(users_IDs=user).values_list('pk', flat=True)
    usersCircles = choice(usersCircles)
    usersCircles = Circle.objects.get(pk=usersCircles)
    isWaiting = 0
    try:
        isWaiting = WaitingRoom.objects.get(user_that_want_to_join_ID=user)
    except WaitingRoom.DoesNotExist:
        pass
    #Trzeba przetestować czy to ma jakiś sens
    if not isWaiting:
        addWaiting = WaitingRoom(user_that_want_to_join_ID=user)
        addWaiting.save()
        isWaiting = WaitingRoom.objects.get(user_that_want_to_join_ID=user)
    circlesID = Circle.objects.filter(users_IDs=user)
    freeSessions = ActiveSession.objects.filter(member2_ID__isnull=True).filter(circle=usersCircles).values_list('pk', flat=True)
    print(freeSessions)

    if freeSessions and not ActiveSession.objects.filter(member1_ID=user_id) and not ActiveSession.objects.filter(member2_ID=user_id):
        randomSessionPk = choice(freeSessions)
        randomSessionObj = ActiveSession.objects.get(pk=randomSessionPk)
        randomSessionObj.member2_ID = WaitingRoom.objects.get(user_that_want_to_join_ID=user)
        randomSessionObj.save()
    elif not ActiveSession.objects.filter(member1_ID=user_id) and not ActiveSession.objects.filter(member2_ID=user_id):
        newSession = ActiveSession(member1_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user), circle=usersCircles)
        newSession.save()

    if ActiveSession.objects.filter(member1_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user)):
        r_id = ActiveSession.objects.filter(member1_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user)).values_list('pk', flat=True)
    elif ActiveSession.objects.filter(member2_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user)):
        r_id = ActiveSession.objects.filter(member2_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user)).values_list('pk', flat=True)
    r_id = r_id[0]
    waiting_id = WaitingRoom.objects.get(user_that_want_to_join_ID=user_id)

    return render(request, 'index.html', {
        'room_id': r_id,
        'waiting_id': waiting_id
    })

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

def root(request):

    return render(request, 'base.html', {})