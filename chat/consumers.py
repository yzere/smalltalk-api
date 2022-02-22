import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models import Message, ActiveSession
from django.db.models import Q

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.user_ID = self.scope["user"].user_ID
        # session = ActiveSession.objects.get(member1_ID = self.scope["user".user_ID])
        if database_sync_to_async(ActiveSession.objects.filter)(member1_ID=2) != None:
            session = await database_sync_to_async(ActiveSession.objects.get)(session_ID=1)
            print(session)
        print(self.scope['user'].user_ID)
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        print(text_data_json)
        self.user_ID = self.scope['user'].user_ID
        print(self.scope['user'].user_ID)

        # Znajdowanie sesji
        room = await database_sync_to_async(ActiveSession.objects.get)(session_ID=self.room_name)

        # Tworzenie nowej wiadomości
        msg = Message(
			content=message,
			sender_ID=self.scope['user'],
			active_session_ID=room
		)
        await database_sync_to_async(msg.save)()

        # Dodawanie wiadomości do sesji

        msgLink = await database_sync_to_async(ActiveSession.objects.get)(pk=self.room_name)
        await database_sync_to_async(msgLink.messages_IDs.add)(msg)


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username,
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

    pass