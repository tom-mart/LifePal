from django.contrib import admin

from .models import UserProfile, UserSettings, LLMContextProfile

admin.site.register(UserProfile)
admin.site.register(UserSettings)
admin.site.register(LLMContextProfile)
