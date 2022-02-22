
from multiprocessing.connection import wait
from tabnanny import check
from django.shortcuts import render
from api.models import ActiveSession, Message, Profile, WaitingRoom, CustomUser
from random import choice
import copy
import json
from django.http import JsonResponse
from chat.views_methods import ( find_free_sessions,
 find_user_session,
 find_user_waitingroom_object,
 choose_session,
  )


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
    if find_user_session(request)[1] != None:
        message = f'User {user_id} already in session of id {find_user_session(request)[0]}'
    else: 
        free_sessions = find_free_sessions(request)
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

#Paczki, dla klienta
def instant_match(request):
    join_waitingroom(request)
    join_session(request)
    return send_response()


def instant_abort(request):
    leave_session(request)
    leave_waitingroom(request)
    return send_response()
    

def index(request):
    
    #definicje obiektów
    user_id = request.user.user_ID
    user = CustomUser.objects.get(pk=user_id)

    freeSessions = find_free_sessions(request)
    print('Totally empty sessions: ', freeSessions)

    # Jak na jeżeli są jakieś sesje, lub nie ma sesji, to dodaje użytkownika lub tworzy sesję, pozostało: jeśeli użytkownik ma sesję to do niej dodaje
    

    if freeSessions and not ActiveSession.objects.filter(member2_ID=user_id):
        randomSessionPk = choice(freeSessions)
        randomSessionObj = ActiveSession.objects.get(pk=randomSessionPk)
        randomSessionObj.member2_ID = WaitingRoom.objects.get(user_that_want_to_join_ID=user)
        randomSessionObj.save()
    elif not ActiveSession.objects.filter(member1_ID=user_id) and not ActiveSession.objects.filter(member2_ID=user_id):
        newSession = ActiveSession(member1_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user))
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