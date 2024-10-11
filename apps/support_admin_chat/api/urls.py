# urls.py
from django.urls import path
from .views import admin_chat_list, admin_chat, user_chat

urlpatterns = [
    path('api/admin/chats/', admin_chat_list, name='admin_chat_list'),
    path('api/admin/chats/<int:pk>/', admin_chat, name='admin_chat'),
    path('api/user/chat/', user_chat, name='user_chat'),
]
