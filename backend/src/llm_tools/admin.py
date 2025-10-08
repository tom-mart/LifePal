from django.contrib import admin
from .models import ToolDefinition, ToolExecution, ToolCategory


@admin.register(ToolDefinition)
class ToolDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'category', 'execution_type', 'is_active', 'execution_count', 'success_rate_display']
    list_filter = ['category', 'execution_type', 'is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'execution_count', 'success_count', 'error_count', 'avg_execution_time_ms']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'display_name', 'category', 'description', 'usage_examples']
        }),
        ('Execution Configuration', {
            'fields': ['execution_type', 'script_path', 'script_timeout', 'lambda_function_arn', 'lambda_region', 'webhook_url', 'webhook_method', 'webhook_headers', 'webhook_timeout']
        }),
        ('Parameters & Response', {
            'fields': ['parameters_schema', 'response_schema']
        }),
        ('Access Control', {
            'fields': ['is_active', 'requires_auth', 'allowed_roles']
        }),
        ('Metadata', {
            'fields': ['version', 'created_by', 'created_at', 'updated_at']
        }),
        ('Statistics', {
            'fields': ['execution_count', 'success_count', 'error_count', 'avg_execution_time_ms'],
            'classes': ['collapse']
        }),
    ]
    
    def success_rate_display(self, obj):
        if obj.execution_count > 0:
            rate = (obj.success_count / obj.execution_count) * 100
            return f"{rate:.1f}%"
        return "N/A"
    success_rate_display.short_description = 'Success Rate'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ToolExecution)
class ToolExecutionAdmin(admin.ModelAdmin):
    list_display = ['tool', 'user', 'status', 'execution_time_ms', 'created_at']
    list_filter = ['status', 'tool', 'created_at']
    search_fields = ['tool__name', 'user__username']
    readonly_fields = ['tool', 'user', 'parameters', 'result', 'status', 'error_message', 'execution_time_ms', 'conversation_id', 'created_at']
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Read-only


@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'display_name']
