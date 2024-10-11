import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from apps.authentication.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.is_admin = self.scope["user"].is_staff
        self.room_id = self.scope["url_route"]["kwargs"].get("room_id", self.user_id)
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.is_admin:
            await self.mark_messages_as_read(self.room_id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")
            sender_id = text_data_json.get("sender_id")
            sender_username = text_data_json.get("sender_username")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        if text_data_json.get("type") == "chat_opened":
            await self.mark_messages_as_read(self.room_id)
        elif message:
            await self.save_message(sender_id, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": sender_id,
                    "sender_username": sender_username,
                },
            )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_username": event["sender_username"],
                }
            )
        )

        if self.is_admin:
            await self.mark_messages_as_read(self.room_id)

    @database_sync_to_async
    def save_message(self, user_id, message):
        print(user_id, message)
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=self.room_id)
        ChatMessage.objects.create(
            room=room, sender=user, message=message, is_read=self.is_admin
        )

    @database_sync_to_async
    def mark_messages_as_read(self, room_id):
        ChatRoom.objects.get(id=room_id).messages.filter(is_read=False).update(
            is_read=True
        )
