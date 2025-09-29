from typing import List
from datetime import timedelta
from ninja import Router, Query
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth.models import User
from . import models, schemas

router = Router(tags=["Tasks"], auth=JWTAuth())

# Helper functions
def get_user_from_token(request):
    return request.auth

# Category endpoints
@router.post("/categories/", response={201: schemas.CategoryOut, 400: schemas.MessageOut})
def create_category(request, payload: schemas.CategoryIn):
    user = get_user_from_token(request)
    if models.Category.objects.filter(user=user, name=payload.name).exists():
        return 400, {"detail": "Category with this name already exists"}
    
    category = models.Category.objects.create(user=user, **payload.dict())
    return 201, category

@router.get("/categories/", response=List[schemas.CategoryOut])
def list_categories(request):
    user = get_user_from_token(request)
    return models.Category.objects.filter(user=user)

# Task endpoints
@router.post("/tasks/", response={201: schemas.TaskOut, 400: schemas.MessageOut})
def create_task(request, payload: schemas.TaskCreate):
    user = get_user_from_token(request)
    data = payload.dict()
    
    # Handle related fields
    category_id = data.pop('category_id', None)
    tag_ids = data.pop('tag_ids', [])
    assigned_to_ids = data.pop('assigned_to_ids', [])
    parent_task_id = data.pop('parent_task_id', None)
    template_id = data.pop('template_id', None)
    
    # Create task - no need for duration conversion now
    task = models.Task.objects.create(
        user=user,
        category_id=category_id,
        parent_task_id=parent_task_id,
        template_id=template_id,
        **{k: v for k, v in data.items() if v is not None}
    )
    
    # Set many-to-many relationships
    if tag_ids:
        task.tags.set(tag_ids)
    if assigned_to_ids:
        task.assigned_to.set(assigned_to_ids)
    
    return 201, task

@router.get("/tasks/", response=List[schemas.TaskOut])
@paginate(PageNumberPagination, page_size=20)
def list_tasks(
    request,
    status: str = None,
    category: int = None,
    tag: str = None,
    priority: int = None,
    assigned_to_me: bool = False,
    search: str = None
):
    user = get_user_from_token(request)
    queryset = models.Task.objects.filter(user=user)
    
    # Apply filters
    if status:
        queryset = queryset.filter(status=status)
    if category:
        queryset = queryset.filter(category_id=category)
    if tag:
        queryset = queryset.filter(tags__name=tag)
    if priority:
        queryset = queryset.filter(priority=priority)
    if assigned_to_me:
        queryset = queryset.filter(assigned_to=user)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    return queryset.distinct()

@router.get("/tasks/{task_id}/", response={200: schemas.TaskOut, 404: schemas.MessageOut})
def get_task(request, task_id: int):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    return 200, task

@router.patch("/tasks/{task_id}/", response={200: schemas.TaskOut, 404: schemas.MessageOut})
def update_task(request, task_id: int, payload: schemas.TaskUpdate):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    
    data = payload.dict(exclude_unset=True)
    
    # Update fields
    for field, value in data.items():
        if field == 'tag_ids' and value is not None:
            task.tags.set(value)
        elif field == 'assigned_to_ids' and value is not None:
            task.assigned_to.set(value)
        elif hasattr(task, field) and value is not None:
            setattr(task, field, value)
    
    task.save()
    return 200, task

@router.delete("/tasks/{task_id}/", response={204: None, 404: schemas.MessageOut})
def delete_task(request, task_id: int):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    task.delete()
    return 204, None

# Comment endpoints
@router.post("/tasks/{task_id}/comments/", response={201: schemas.CommentOut})
def add_comment(request, task_id: int, payload: schemas.CommentIn):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    comment = models.TaskComment.objects.create(
        task=task,
        user=user,
        **payload.dict()
    )
    return 201, comment

@router.get("/tasks/{task_id}/comments/", response=List[schemas.CommentOut])
def list_comments(request, task_id: int):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    return models.TaskComment.objects.filter(task=task)

# Reminder endpoints
@router.post("/tasks/{task_id}/reminders/", response={201: schemas.ReminderOut})
def create_reminder(request, task_id: int, payload: schemas.ReminderIn):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    reminder = models.Reminder.objects.create(task=task, **payload.dict())
    return 201, reminder

@router.get("/tasks/{task_id}/reminders/", response=List[schemas.ReminderOut])
def list_reminders(request, task_id: int):
    user = get_user_from_token(request)
    task = get_object_or_404(models.Task, id=task_id, user=user)
    return models.Reminder.objects.filter(task=task)