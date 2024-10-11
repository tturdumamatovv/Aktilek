from django.contrib import admin
from unfold.admin import TabularInline, ModelAdmin

from .models import ChatRoom, ChatMessage


class ChatMessageInline(TabularInline):
    model = ChatMessage
    extra = 0


@admin.register(ChatRoom)
class ChatRoomAdmin(ModelAdmin):
    inlines = [ChatMessageInline]
