import json
from lib2to3.pytree import Base
from urllib import request
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.http import JsonResponse
from api.models import CustomUser, Message, ActiveSession
from django.db.models import Q
from .consumers_methods import check_message_code
# from views import close_session
# import requests_async as requests

# CHAT_API_URL = 'http://127.0.0.1:8000/chat'
class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        penalty = 0;
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.user_ID = self.scope["user"].user_ID
        # session = ActiveSession.objects.get(member1_ID = self.scope["user".user_ID])
        try:
            if database_sync_to_async(ActiveSession.objects.filter)(member1_ID=self.user_ID) != None:
                session = await database_sync_to_async(ActiveSession.objects.get)(member1_ID=self.user_ID)
        except BaseException as err:
            penalty += 1;
        
        try:
            if database_sync_to_async(ActiveSession.objects.filter)(member2_ID=self.user_ID) != None:
                session = await database_sync_to_async(ActiveSession.objects.get)(member2_ID=self.user_ID)
                #kontynuacja tego
        except BaseException as err:
            penalty += 1;
        
            if penalty > 1:
                session = None
                print(f'ERROR: {err} ')
                print(f'user {self.user_ID} has no active session')
                await self.close()
                penalty = 0
                return
        else: 
            penalty = 0
        # else:
        # except BaseException as err:
        #     session = None
        #     print(f'ERROR: {err} ')
        #     print(f'user {self.user_ID} has no active session')
        #     await self.close()
        #     return
        
        print(f'self.room_name: {self.room_name} | session_ID: {session.session_ID}')
        if int(session.session_ID) == int(self.room_name):
            print(f'session ID: {session}')
            print(f'user ID: {self.scope["user"].user_ID}')
            await self.accept()
            return 

        else:
            print(f'user {self.user_ID} is not in session {self.room_name}')
            await self.close()
            return


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        code = check_message_code(message)

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
        # print(f'msglink: {msgLink}')
        await database_sync_to_async(msgLink.messages_IDs.add)(msg)

        session = await database_sync_to_async(ActiveSession.objects.get)(pk=self.room_name)
        # Użytkownik chce się ujawnić
        if code == '#001':
            user = self.scope['user']
            await database_sync_to_async(msgLink.reveals.add)(user)
            # room.reveals.add(user)
            #checking if everyone in session want to reveal
            # set_user_reveal_status()
            # check_if_reveal()
            

            @database_sync_to_async
            def get_reveals(session):
                return list(session.reveals.all())

            # @database_sync_to_async
            # def get_users(session):
            #     return list(session..all())

            res = await get_reveals(session)
            print(len(res))
            if len(res) > 1:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chatroom_message',
                        'message': f'#002 users reveal themselves. user1: {res[0].username} user2: {res[1].username}',
                        'username': 'server',
                    }
                    )
                @database_sync_to_async
                def get_users(session):
                    return list(CustomUser.objects.filter(pk = session.member1_ID | session.member2_ID))
                
                
                await database_sync_to_async(session.delete)()
                

                # messages = await get_messages(session)
                # for msg in messages:
                #     await database_sync_to_async(msg.delete)()
                
                

                # def close_session_from_channels(session):
                #     messages = await Message.objects.
                    

                # close_session_from_channels(room)
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chatroom_message',
                        'message': f'#007 User {user.user_ID} wants to reveal.',
                        'username': 'server',
                    }
                    )
            print(f'reveals: {res}')

        elif code == '#003':
            #trzeba będzie dopisać o zmienianiu statusu ujawnienia się
            user = self.scope['user']
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chatroom_message',
                        'message': f'#006 User {user.user_ID} rejects conversation.',
                        'username': 'server',
                    }
                    )
            await database_sync_to_async(session.delete)()

        # Użytkownik rezygnuje z ujawnienia się
        elif code == '#005':
            #trzeba będzie dopisać o zmienianiu statusu ujawnienia się
            user = self.scope['user']
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chatroom_message',
                        'message': f'#007 User {user.user_ID} doesn\'t want to reveal.',
                        'username': 'server',
                    }
                    )
            await database_sync_to_async(msgLink.reveals.remove)(user)

        elif code == '#000':
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