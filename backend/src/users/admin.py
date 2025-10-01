from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserProfile, UserSettings, LLMContextProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_email', 'get_user_username', 'preferred_name')
    search_fields = ('user__email', 'user__username', 'preferred_name')
    list_filter = ('user__is_active',)
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.short_description = 'Username'
    get_user_username.admin_order_field = 'user__username'


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_email', 'get_user_username', 'theme', 'last_active')
    search_fields = ('user__email', 'user__username')
    list_filter = ('theme', 'email_notifications', 'push_notifications')
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.short_description = 'Username'
    get_user_username.admin_order_field = 'user__username'


@admin.register(LLMContextProfile)
class LLMContextProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_email', 'get_user_username', 'get_age', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    list_filter = ('created_at', 'updated_at', 'has_children')
    readonly_fields = ('id', 'created_at', 'updated_at', 'get_age')
    
    # WARNING: Encrypted fields will be decrypted for superusers viewing this admin
    # This is by design for administrative purposes, but access should be restricted
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'user', 'created_at', 'updated_at')
        }),
        ('Demographics', {
            'fields': ('date_of_birth', 'get_age', 'gender', 'ethnic_background')
        }),
        ('Life Context', {
            'fields': ('occupation', 'relationship_status', 'living_situation', 'has_children', 'children_info')
        }),
        ('Wellbeing', {
            'fields': ('health_conditions', 'mental_health_history', 'current_challenges', 'stress_factors', 'coping_mechanisms'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('communication_style', 'learning_style', 'response_preferences')
        }),
        ('Goals & Values', {
            'fields': ('personal_goals', 'professional_goals', 'core_values', 'interests'),
            'classes': ('collapse',)
        }),
        ('Daily Routine', {
            'fields': ('typical_schedule', 'sleep_pattern'),
            'classes': ('collapse',)
        }),
        ('Support System', {
            'fields': ('support_network', 'professional_support'),
            'classes': ('collapse',)
        }),
        ('LifePal Usage', {
            'fields': ('lifepal_usage_goals', 'topics_of_interest', 'topics_to_avoid'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'N/A'
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_user_username(self, obj):
        return obj.user.username if obj.user else 'N/A'
    get_user_username.short_description = 'Username'
    get_user_username.admin_order_field = 'user__username'
    
    def get_age(self, obj):
        return obj.age if obj.age else 'N/A'
    get_age.short_description = 'Age'
    
    def get_queryset(self, request):
        """Override to ensure all records are shown."""
        qs = super().get_queryset(request)
        # Use select_related to optimize queries
        return qs.select_related('user')
