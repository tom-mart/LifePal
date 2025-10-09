from django.db import models
from django.contrib.auth.models import User
import uuid


class ToolCategory(models.Model):
    """
    Dynamic tool categories - user can add new categories as needed.
    """
    # Keep BigAutoField to match existing database
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Category identifier (lowercase, no spaces, e.g., 'wellbeing')"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Human-readable name (e.g., 'Wellbeing & Check-ins')"
    )
    description = models.TextField(
        blank=True,
        help_text="What types of tools belong in this category"
    )
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tool Categories'
    
    def __str__(self):
        return f"{self.display_name} ({self.name})"


class ToolDefinition(models.Model):
    """
    Fully dynamic tool definition.
    No hardcoded tools - everything configured in database.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tool identity
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique tool name (e.g., 'create_task')"
    )
    display_name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Category name (must match a ToolCategory.name)"
    )
    
    # LLM-facing description
    description = models.TextField(
        help_text="Detailed description for LLM (when to use this tool)"
    )
    usage_examples = models.JSONField(
        default=list,
        blank=True,
        help_text='["Example 1", "Example 2"]'
    )
    
    # Execution configuration
    execution_type = models.CharField(
        max_length=20,
        choices=[
            ('script', 'Python Script'),
            ('lambda', 'AWS Lambda'),
            ('webhook', 'External Webhook'),
        ],
        help_text="How this tool is executed"
    )
    
    # Script execution
    script_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Absolute path to Python script (for script type)"
    )
    script_timeout = models.IntegerField(
        default=30,
        help_text="Script timeout in seconds"
    )
    
    # Lambda execution
    lambda_function_arn = models.CharField(
        max_length=500,
        blank=True,
        help_text="AWS Lambda ARN (for lambda type)"
    )
    lambda_region = models.CharField(
        max_length=50,
        default='us-east-1',
        blank=True
    )
    
    # Webhook execution
    webhook_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="External webhook URL (for webhook type)"
    )
    webhook_method = models.CharField(
        max_length=10,
        choices=[('GET', 'GET'), ('POST', 'POST')],
        default='POST',
        blank=True
    )
    webhook_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"Authorization": "Bearer token"}'
    )
    webhook_timeout = models.IntegerField(
        default=30,
        help_text="Webhook timeout in seconds"
    )
    
    # Parameters schema (JSON Schema format)
    parameters_schema = models.JSONField(
        default=dict,
        help_text="JSON Schema defining tool parameters"
    )
    
    # Response schema
    response_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Expected response format"
    )
    
    # Access control
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this tool is available"
    )
    requires_auth = models.BooleanField(default=True)
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text='["admin", "premium_user"]'
    )
    
    # Metadata
    version = models.CharField(max_length=20, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tools'
    )
    
    # Statistics
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    avg_execution_time_ms = models.FloatField(default=0)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['execution_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_execution_type_display()})"
    
    def to_ollama_tool(self):
        """Convert to Ollama Tool format"""
        from ollama import Tool
        
        return Tool(
            type='function',
            function=Tool.Function(
                name=self.name,
                description=self.description,
                parameters=Tool.Function.Parameters(**self.parameters_schema) if self.parameters_schema else Tool.Function.Parameters()
            )
        )
    
    def update_stats(self, success: bool, execution_time_ms: int):
        """Update execution statistics"""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        # Update average execution time
        total_time = self.avg_execution_time_ms * (self.execution_count - 1)
        self.avg_execution_time_ms = (total_time + execution_time_ms) / self.execution_count
        self.save(update_fields=[
            'execution_count', 'success_count', 'error_count', 'avg_execution_time_ms'
        ])


class ToolExecution(models.Model):
    """Audit log for all tool executions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    tool = models.ForeignKey(
        ToolDefinition,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tool_executions'
    )
    
    # Execution details
    parameters = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('error', 'Error'),
            ('timeout', 'Timeout'),
        ]
    )
    error_message = models.TextField(blank=True)
    
    # Performance
    execution_time_ms = models.IntegerField(null=True)
    
    # Context
    conversation_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tool', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.tool.name} by {self.user.username} - {self.status}"
