from django.contrib import admin
from .models import PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint_preview', 'is_active', 'created_at', 'last_used')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'endpoint')
    readonly_fields = ('id', 'created_at', 'last_used')
    
    def endpoint_preview(self, obj):
        return f"{obj.endpoint[:50]}..." if len(obj.endpoint) > 50 else obj.endpoint
    endpoint_preview.short_description = 'Endpoint'
