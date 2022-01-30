import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# this was a synchronous chat consumer that we had to use async_to_sync to make it async
from chat.models import SingleChat, Messages, Profile
from chat.utils import get_users_chat

'''
The async_to_sync(. . . ) wrapper is required because ChatConsumer is a synchronous Websocket-
Consumer but it is calling an asynchronous channel layer method. (All channel layer methods are
asynchronous.)
'''

'''
The ChatConsumer that we have written is currently synchronous. Synchronous consumers are convenient because
they can call regular synchronous I/O functions such as those that access Django models without writing special code.
However asynchronous consumers can provide a higher level of performance since they don’t need to create additional
threads when handling requests.
ChatConsumer only uses async-native libraries (Channels and the channel layer) and in particular it does not access
synchronous Django models. Therefore it can be rewritten to be asynchronous without complications.

'''


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         self.accept()
#
#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard) (
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # receive message from Websocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # receive message form room group
#     def chat_message(self, event):
#         message = event['message']
#
#         # send message to websocket
#         self.send(text_data=json.dumps({'message': message}))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['id']
        self.chat = await self.get_chat()
        self.room_group_name = 'chat_%s' % str(self.chat.id)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # save the message to db
        message = await self.save_sent_message(message)
        # send webpush notification to the other user
        await self.send_webpush_notifications(message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message})

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # get the chat the participants are in
    @database_sync_to_async
    def get_chat(self):
        participant = Profile.objects.get(id=self.chat_id)
        user = self.scope['user'].profile
        chat = get_users_chat(user=user, participant=participant)
        return chat

    # save the message and return it back
    @database_sync_to_async
    def save_sent_message(self, message):
        user = self.scope['user'].profile
        chat = self.chat
        message = Messages.objects.create(chat=chat, by=user, message=message)
        message = {'by': message.by.name, 'to': self.chat_id, 'message': message.message,
                   'time': message.timestamp.strftime("%d %b %Y %H:%M:%S")}
        return message

