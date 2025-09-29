from ninja import Router
from django.contrib.auth import get_user_model
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from typing import List
from .schemas import (
    UserRegistrationSchema,
    UserProfileSchema,
    UserProfileUpdateSchema,
    UserSettingsSchema,
    UserSettingsUpdateSchema,
    LLMContextProfileSchema,
    LLMContextProfileCreateSchema,
    LLMContextProfileUpdateSchema,
    PersonalInfoSchema,
    WellbeingContextSchema,
    PreferencesSchema
)
from .models import LLMContextProfile, UserProfile, UserSettings
from django.db import transaction

router = Router()
User = get_user_model()

# Public endpoints (no auth required)
@router.post("/register", response={201: dict}, tags=[" User Profile"])
def register_user(request, payload: UserRegistrationSchema):
    with transaction.atomic():
        user = User.objects.create_user(
            username=payload.username,
            email=payload.username,
            password=payload.password
        )

        llm_context_profile = LLMContextProfile.objects.create(user=user)
        user_profile = UserProfile.objects.create(user=user)
        user_settings = UserSettings.objects.create(user=user)

    return 201, {"success": True,
                    "id": user.id,
                    "profile_id": llm_context_profile.id,
                    "user_profile_id": user_profile.id,
                    "user_settings_id": user_settings.id
                }

@router.get("/profile", auth=JWTAuth(), response=UserProfileSchema, tags=[" User Profile"])
def get_profile(request):
    return get_object_or_404(UserProfile, user=request.user)

@router.patch("/profile", auth=JWTAuth(), response=UserProfileUpdateSchema, tags=[" User Profile"])
def update_profile(request, payload: UserProfileUpdateSchema):
    profile = get_object_or_404(UserProfile, user=request.user)
    data = payload.dict(exclude_unset=True)
    
    for field, value in data.items():
        setattr(profile, field, value)
    profile.save()
    
    return profile

@router.get("/settings", auth=JWTAuth(), response=UserSettingsSchema, tags=[" User Profile"])
def get_settings(request):
    return get_object_or_404(UserSettings, user=request.user)

@router.patch("/settings", auth=JWTAuth(), response=UserSettingsUpdateSchema, tags=[" User Profile"])
def update_settings(request, payload: UserSettingsUpdateSchema):
    settings = get_object_or_404(UserSettings, user=request.user)
    data = payload.dict(exclude_unset=True)
    
    for field, value in data.items():
        setattr(settings, field, value)
    settings.save()
    
    return settings

@router.get("/llm_context_profile", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def get_llm_context_profile(request):
    return get_object_or_404(LLMContextProfile, user=request.user)

@router.patch("/llm_context_profile", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def update_llm_context_profile(request, payload: LLMContextProfileCreateSchema):
    llm_context_profile = get_object_or_404(LLMContextProfile, user=request.user)
    data = payload.dict(exclude_unset=True)
    
    for field, value in data.items():
        setattr(llm_context_profile, field, value)
    llm_context_profile.save()
    
    return llm_context_profile

@router.patch("/profile/personal", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def update_personal_info(request, payload: LLMContextProfileSchema):
    profile = get_object_or_404(LLMContextProfile, user=request.user)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    profile.save()
    return profile

@router.patch("/profile/wellbeing", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def update_wellbeing(request, payload: WellbeingContextSchema):
    """Update only wellbeing information"""
    profile = get_object_or_404(LLMContextProfile, user=request.user)
    
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    profile.save()
    return profile

@router.patch("/profile/preferences", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def update_preferences(request, payload: PreferencesSchema):
    """Update only preferences"""
    profile = get_object_or_404(LLMContextProfile, user=request.user)
    
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    profile.save()
    return profile

@router.post("/account/deactivate", auth=JWTAuth(), tags=[" User Profile"])
def deactivate_account(request):
    """Temporarily deactivate user account"""
    request.user.is_active = False
    request.user.save()
    return {"success": True}

@router.post("/account/reactivate", auth=JWTAuth(), tags=[" User Profile"])
def reactivate_account(request):
    """Reactivate user account"""
    request.user.is_active = True
    request.user.save()
    return {"success": True}