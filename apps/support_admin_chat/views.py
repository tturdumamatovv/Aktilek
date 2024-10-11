from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .api.serializers import ChatMessageSerializer
from .models import ChatRoom, ChatMessage
# Create your views here.
from django.db.models import Q

# views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from ..orders.api.serializers import OrderChatSerializer
from django.http import JsonResponse
from django.core.serializers import serialize
from ..orders.api.serializers import OrderChatSerializer
from ..orders.models import Order


@staff_member_required
def admin_chat_list(request):
    chats = ChatRoom.objects.all()

    # Получаем информацию для каждого чата
    chat_data = []
    for chat in chats:
        last_message = chat.messages.order_by('-timestamp').first()  # Последнее сообщение в чате
        unread_messages_count = chat.messages.filter(is_read=False).count()  # Количество непрочитанных сообщений

        chat_data.append({
            'chat': chat,
            'last_message': last_message,
            'unread_messages_count': unread_messages_count
        })

    context = {
        'chat_data': chat_data
    }

    return render(request, 'admin_chat_list.html', context)

@staff_member_required
def admin_chat(request, pk):
    chat_room = ChatRoom.objects.get(id=pk)
    chat_room.messages.filter(is_read=False).update(is_read=True)

    context = {
        'chat_room': chat_room,
        'chat_messages': chat_room.messages.all().order_by('timestamp'),
        'users': request.user
    }

    return render(request, 'admin_chat.html', context)


def user_chat(request):
    if request.user.is_anonymous:
        print('User is anonymous')
        return render(request, 'user_chat.html')
    chat_room, created = ChatRoom.objects.get_or_create(user=request.user)

    context = {
        'chat_room': chat_room,  # Передаем комнату в шаблон
        'chat_messages': chat_room.messages.all().order_by('timestamp'),  # Передаем список сообщений в шаблон
    }

    return render(request, 'user_chat.html', context)


class UserOrdersView(APIView):
    def get(self, request, user_id):
        orders = Order.objects.filter(user_id=user_id).order_by('-id')
        serializer = OrderChatSerializer(orders, many=True)
        for i in serializer.data:
            print(i)
        return Response({'orders': serializer.data})


class ChatRoomMessagesView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        print(serializer.data)
        return Response({'messages': serializer.data})

