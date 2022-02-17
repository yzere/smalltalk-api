from django.shortcuts import render
from api.models import ActiveSession, Message

# Create your views here.
def index(request):
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