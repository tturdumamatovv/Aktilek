# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([IsAuthenticated, staff_member_required])
def admin_chat_list(request):
    """
    API для получения списка всех чатов с последним сообщением и количеством непрочитанных сообщений.
    """
    chats = ChatRoom.objects.all()
    chat_data = []

    for chat in chats:
        last_message = chat.messages.order_by('-timestamp').first()
        unread_messages_count = chat.messages.filter(is_read=False).count()

        chat_data.append({
            'chat': ChatRoomSerializer(chat).data,
            'last_message': ChatMessageSerializer(last_message).data if last_message else None,
            'unread_messages_count': unread_messages_count
        })

    return Response(chat_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, staff_member_required])
def admin_chat(request, pk):
    """
    API для получения сообщений в конкретной комнате чата администратором.
    """
    chat_room = get_object_or_404(ChatRoom, id=pk)
    # Помечаем все сообщения как прочитанные
    chat_room.messages.filter(is_read=False).update(is_read=True)

    context = {
        'chat_room': ChatRoomSerializer(chat_room).data,
        'chat_messages': ChatMessageSerializer(chat_room.messages.all().order_by('timestamp'), many=True).data
    }

    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_chat(request):
    """
    API для получения чата текущего пользователя. Если чат отсутствует, он будет создан.
    """
    chat_room, created = ChatRoom.objects.get_or_create(user=request.user)

    context = {
        'chat_room': ChatRoomSerializer(chat_room).data,
        'chat_messages': ChatMessageSerializer(chat_room.messages.all().order_by('timestamp'), many=True).data
    }

    return Response(context, status=status.HTTP_200_OK)
