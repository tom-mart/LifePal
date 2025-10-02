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
@router.post("/register", response={201: dict, 403: dict}, tags=[" User Profile"])
def register_user(request, payload: UserRegistrationSchema):
    # Check if registration is enabled (default: disabled in production)
    from django.conf import settings
    import os
    
    registration_enabled = os.environ.get('ALLOW_REGISTRATION', 'False') == 'True'
    
    if not registration_enabled:
        return 403, {"success": False, "message": "Registration is currently disabled"}
    
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
    profile = get_object_or_404(LLMContextProfile, user=request.user)
    # Convert date_of_birth to string format and include computed age
    response_data = {
        'id': profile.id,
        'user_id': profile.user.id,
        'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        'age': profile.age,  # Computed property
        'gender': profile.gender,
        'ethnic_background': profile.ethnic_background,
        'occupation': profile.occupation,
        'relationship_status': profile.relationship_status,
        'living_situation': profile.living_situation,
        'has_children': profile.has_children,
        'children_info': profile.children_info,
        'health_conditions': profile.health_conditions,
        'mental_health_history': profile.mental_health_history,
        'current_challenges': profile.current_challenges,
        'stress_factors': profile.stress_factors,
        'coping_mechanisms': profile.coping_mechanisms,
        'communication_style': profile.communication_style,
        'learning_style': profile.learning_style,
        'response_preferences': profile.response_preferences,
        'personal_goals': profile.personal_goals,
        'professional_goals': profile.professional_goals,
        'core_values': profile.core_values,
        'interests': profile.interests,
        'typical_schedule': profile.typical_schedule,
        'sleep_pattern': profile.sleep_pattern,
        'support_network': profile.support_network,
        'professional_support': profile.professional_support,
        'lifepal_usage_goals': profile.lifepal_usage_goals,
        'topics_of_interest': profile.topics_of_interest,
        'topics_to_avoid': profile.topics_to_avoid,
    }
    return response_data

@router.patch("/llm_context_profile", auth=JWTAuth(), response=LLMContextProfileSchema, tags=[" User Profile"])
def update_llm_context_profile(request, payload: LLMContextProfileCreateSchema):
    from datetime import datetime
    
    llm_context_profile = get_object_or_404(LLMContextProfile, user=request.user)
    data = payload.dict(exclude_unset=True)
    
    # Handle date_of_birth conversion from string to date
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth']).date()
        except (ValueError, AttributeError):
            pass  # Keep as is if conversion fails
    
    for field, value in data.items():
        setattr(llm_context_profile, field, value)
    llm_context_profile.save()
    
    # Return with computed age
    response_data = {
        'id': llm_context_profile.id,
        'user_id': llm_context_profile.user.id,
        'date_of_birth': llm_context_profile.date_of_birth.isoformat() if llm_context_profile.date_of_birth else None,
        'age': llm_context_profile.age,
        'gender': llm_context_profile.gender,
        'ethnic_background': llm_context_profile.ethnic_background,
        'occupation': llm_context_profile.occupation,
        'relationship_status': llm_context_profile.relationship_status,
        'living_situation': llm_context_profile.living_situation,
        'has_children': llm_context_profile.has_children,
        'children_info': llm_context_profile.children_info,
        'health_conditions': llm_context_profile.health_conditions,
        'mental_health_history': llm_context_profile.mental_health_history,
        'current_challenges': llm_context_profile.current_challenges,
        'stress_factors': llm_context_profile.stress_factors,
        'coping_mechanisms': llm_context_profile.coping_mechanisms,
        'communication_style': llm_context_profile.communication_style,
        'learning_style': llm_context_profile.learning_style,
        'response_preferences': llm_context_profile.response_preferences,
        'personal_goals': llm_context_profile.personal_goals,
        'professional_goals': llm_context_profile.professional_goals,
        'core_values': llm_context_profile.core_values,
        'interests': llm_context_profile.interests,
        'typical_schedule': llm_context_profile.typical_schedule,
        'sleep_pattern': llm_context_profile.sleep_pattern,
        'support_network': llm_context_profile.support_network,
        'professional_support': llm_context_profile.professional_support,
        'lifepal_usage_goals': llm_context_profile.lifepal_usage_goals,
        'topics_of_interest': llm_context_profile.topics_of_interest,
        'topics_to_avoid': llm_context_profile.topics_to_avoid,
    }
    return response_data

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