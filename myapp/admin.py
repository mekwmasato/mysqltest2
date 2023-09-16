from django.contrib import admin
from .models import Message, ChatSession

# Register your models here.
admin.site.register(Message)
admin.site.register(ChatSession)