from django.shortcuts import render
from api.models import ActiveSession, Message, Profile, WaitingRoom
from random import choice

# Create your views here.
def index(request):

    # Jak na jeżeli są jakieś sesje, lub nie ma sesji, to dodaje użytkownika lub tworzy sesję, pozostało: jeśeli użytkownik ma sesję to do niej dodaje

    user_id = request.user.user_ID
    isWaiting = WaitingRoom.objects.get(user_that_want_to_join_ID=user_id)
    if not isWaiting:
        addWaiting = WaitingRoom(user_that_want_to_join_ID=user_id)
        addWaiting.save()
    freeSessions = ActiveSession.objects.filter(member2_ID__isnull=True).values_list('pk', flat=True)
    print(freeSessions)

    if freeSessions  and not ActiveSession.objects.filter(member2_ID=user_id):
        randomSessionPk = choice(freeSessions)
        randomSessionObj = ActiveSession.objects.get(pk=randomSessionPk)
        randomSessionObj.member2_ID = WaitingRoom.objects.get(user_that_want_to_join_ID=user_id)
        randomSessionObj.save()
    elif not ActiveSession.objects.filter(member1_ID=user_id) and not ActiveSession.objects.filter(member2_ID=user_id):
        newSession = ActiveSession(member1_ID=WaitingRoom.objects.get(user_that_want_to_join_ID=user_id))
        newSession.save()

    return render(request, 'index.html', {})

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