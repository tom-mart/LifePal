from django.contrib import admin

from .models import Agent, Conversation, Message, UserAgentPreference

# Register your models here.
admin.site.register(Agent)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(UserAgentPreference)