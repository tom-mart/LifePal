from django.contrib import admin
from .models import Category, Tag, Task, Reminder, Attachment, TaskComment, TaskTemplate, TaskDependency    
# Register your models here.
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Task)
admin.site.register(Reminder)
admin.site.register(Attachment)
admin.site.register(TaskComment)
admin.site.register(TaskTemplate)
admin.site.register(TaskDependency)
