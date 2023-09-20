from django.contrib import admin
from .models import Message, ChatSession, Summary

# Register your models here.
admin.site.register(Message)
admin.site.register(ChatSession)
admin.site.register(Summary)