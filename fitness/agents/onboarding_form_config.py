"""
Fitness Onboarding Form Configuration
Defines the user onboarding flow for fitness profiles
"""


def save_fitness_profile(data, user, conversation):
    """
    Callback to save fitness profile after form completion.
    
    Args:
        data: Dict with all collected form answers
        user: The Django User instance
        conversation: The Conversation instance
        
    Returns:
        (success: bool, message: str)
    """
    try:
        from fitness.models import UserFitnessProfile, Equipment
        
        # Parse exercise and run days
        exercise_days = []
        if data.get('exercise_days'):
            exercise_days = [day.strip() for day in data['exercise_days'].split(',')]
        
        run_days = []
        if data.get('run_days'):
            run_days = [day.strip() for day in data['run_days'].split(',')]
        
        # Create profile
        profile = UserFitnessProfile.objects.create(
            user=user,
            fitness_level=data.get('fitness_level', 'inactive'),
            exercises_per_week=int(data.get('exercises_per_week', 0)),
            runs_per_week=int(data.get('runs_per_week', 0)),
            exercise_days=exercise_days,
            run_days=run_days,
            exercise_location=data.get('exercise_location', 'home'),
            injuries=data.get('injuries', ''),
            restrictions=data.get('restrictions', ''),
        )
        
        # Auto-assign equipment based on location
        location = data.get('exercise_location', 'home')
        if location == 'gym':
            # Assign all gym equipment
            gym_equipment = Equipment.objects.all()
            profile.available_equipment.set(gym_equipment)
        elif location == 'home':
            # Assign only bodyweight
            bodyweight = Equipment.objects.filter(name__iexact='body weight').first()
            if bodyweight:
                profile.available_equipment.set([bodyweight])
        elif location == 'both':
            # Assign all equipment
            all_equipment = Equipment.objects.all()
            profile.available_equipment.set(all_equipment)
        
        profile.save()
        
        return True, f"""✅ **Your fitness profile is complete!**

I'm now your fitness coach ready to help you with your fitness journey.

You can ask me to:
- Create personalized workout plans
- Track your progress
- Give exercise advice
- Adjust your schedule

What would you like to work on first?"""
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Failed to save profile: {str(e)}"


# Form configuration for fitness onboarding
ONBOARDING_FORM = {
    'form_type': 'fitness_onboarding',
    'welcome_message': """👋 **Welcome to Lifepal Fitness!**

I'm your AI fitness coach. To get started, I need to learn a bit about you and your fitness routine.""",
    'completion_message': None,  # Will be set by callback
    'completion_callback': 'fitness.agents.onboarding_form_config.save_fitness_profile',
    'questions': [
        {
            'key': 'fitness_level',
            'question': 'How would you describe your current fitness level? (inactive, lightly active, moderately active, active, or very active)',
            'valid_values': ['inactive', 'light', 'moderate', 'active', 'very_active'],
            'error_msg': 'Please choose one: inactive, lightly active, moderately active, active, or very active.'
        },
        {
            'key': 'exercises_per_week',
            'question': 'How many structured exercise sessions would you like to do per week?',
            'validator': lambda x: x.isdigit() and 0 <= int(x) <= 7,
            'parser': lambda x: int(x),
            'error_msg': 'Please enter a number between 0 and 7.'
        },
        {
            'key': 'runs_per_week',
            'question': 'How many running sessions would you like to do per week?',
            'validator': lambda x: x.isdigit() and 0 <= int(x) <= 7,
            'parser': lambda x: int(x),
            'error_msg': 'Please enter a number between 0 and 7.'
        },
        {
            'key': 'exercise_days',
            'question': 'Which days would you like to exercise? (e.g., Monday, Wednesday, Friday)',
            'validator': lambda x: len(x.strip()) > 0,
            'error_msg': 'Please tell me which days you want to exercise.',
            'skip_if': lambda answers: int(answers.get('exercises_per_week', 0)) == 0,
            'default_value': ''
        },
        {
            'key': 'run_days',
            'question': 'Which days would you like to run?',
            'validator': lambda x: len(x.strip()) > 0,
            'error_msg': 'Please tell me which days you want to run.',
            'skip_if': lambda answers: int(answers.get('runs_per_week', 0)) == 0,
            'default_value': ''
        },
        {
            'key': 'exercise_location',
            'question': 'Where do you prefer to exercise? (home, gym, or both)',
            'valid_values': ['home', 'gym', 'both'],
            'error_msg': 'Please choose: home, gym, or both.'
        },
        {
            'key': 'injuries',
            'question': 'Do you have any injuries I should know about? (Say "none" if you don\'t have any)',
            'validator': lambda x: len(x.strip()) > 0,
            'error_msg': 'Please let me know about any injuries, or say "none".'
        },
        {
            'key': 'restrictions',
            'question': 'Do you have any physical restrictions or limitations? (Say "none" if you don\'t have any)',
            'validator': lambda x: len(x.strip()) > 0,
            'error_msg': 'Please let me know about any restrictions, or say "none".'
        },
    ]
}
