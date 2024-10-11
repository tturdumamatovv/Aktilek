# serializers.py
from rest_framework import serializers
from ..models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source='sender.phone_number', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_phone', 'message', 'timestamp', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)


    class Meta:
        model = ChatRoom
        fields = ['id', 'user', 'user_phone', 'active', 'messages', 'user_id']
