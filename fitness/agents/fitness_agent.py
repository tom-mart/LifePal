"""Fitness agent for handling fitness, nutrition, and health tracking"""
from datetime import datetime, date
from decimal import Decimal
from functools import wraps
from pydantic_ai import RunContext
from agents.base import BaseAgent
from agents import registry
from agents.services.deps import AgentDeps


def require_fitness_profile(func):
    """
    Decorator to ensure user has a fitness profile before executing tool functions.
    Returns error message if profile doesn't exist.
    """
    @wraps(func)
    def wrapper(ctx: RunContext[AgentDeps], *args, **kwargs):
        from fitness.models import UserFitnessProfile
        
        user = ctx.deps.user
        if not UserFitnessProfile.objects.filter(user=user).exists():
            return "❌ Please complete your fitness profile setup first. Would you like to create your profile now?"
        
        return func(ctx, *args, **kwargs)
    
    return wrapper


class FitnessAgent(BaseAgent):
    """
    Main fitness domain agent that handles:
    - Initial user onboarding and profile setup
    - Day-to-day measurement tracking and progress monitoring
    - Fitness goal creation and management
    - Workout logging and recommendations
    - Progress analytics and coaching
    
    This agent intelligently adapts its behavior based on whether the user
    has completed their fitness profile setup.
    """
    
    def process_message_stream(self, message: str, conversation, user=None):
        """Override to handle onboarding before LLM processing"""
        from fitness.models import UserFitnessProfile
        from chat.agents.form_handler import FormHandler
        from agents.models import Agent
        
        # Reload conversation to get latest state
        conversation.refresh_from_db()
        
        print(f"[FITNESS] Checking onboarding state for conversation {conversation.id}")
        print(f"[FITNESS] short_term_memory keys: {list(conversation.short_term_memory.keys())}")
        print(f"[FITNESS] form_active: {conversation.short_term_memory.get('form_active', False)}")
        
        # Check if form is active (we're in form mode)
        if FormHandler.is_active(conversation):
            print(f"[FITNESS] Form is active - conversation is with FormAgent")
            # This shouldn't happen as conversation should be with FormAgent
            # But just in case, let normal processing continue
            return super().process_message_stream(message, conversation, user)
        
        # Check if user needs onboarding (no profile exists)
        try:
            UserFitnessProfile.objects.get(user=user)
            print(f"[FITNESS] Profile exists - proceeding with normal coaching")
        except UserFitnessProfile.DoesNotExist:
            # No profile - trigger form mode
            print(f"[FITNESS] No profile found - triggering onboarding form for {user.username}")
            
            # Get FormAgent
            form_agent = Agent.objects.get(name='FormAgent')
            
            # Store form reference in memory (not the full config - it has functions)
            conversation.short_term_memory['form_type'] = 'fitness_onboarding'
            conversation.short_term_memory['form_module'] = 'fitness.agents.onboarding_form_config'
            conversation.short_term_memory['return_to_agent'] = conversation.agent.id
            conversation.short_term_memory['form_active'] = True
            
            # Switch conversation to FormAgent
            conversation.agent = form_agent
            conversation.save()
            
            print(f"[FITNESS] Switched conversation to FormAgent")
            
            # Let FormAgent handle this message
            from chat.agents.form_agent import FormAgent
            form_agent_instance = FormAgent(agent_model=form_agent)
            return form_agent_instance.process_message_stream(message, conversation, user)
        
        # Normal LLM processing
        return super().process_message_stream(message, conversation, user)
    
    def process_message(self, message: str, conversation, user=None):
        """Override to handle onboarding before LLM processing"""
        from fitness.models import UserFitnessProfile
        from chat.agents.form_handler import FormHandler
        from agents.models import Agent
        
        # Reload conversation to get latest state
        conversation.refresh_from_db()
        
        # Check if form is active (we're in form mode)
        if FormHandler.is_active(conversation):
            # This shouldn't happen as conversation should be with FormAgent
            # But just in case, let normal processing continue
            return super().process_message(message, conversation, user)
        
        # Check if user needs onboarding (no profile exists)
        try:
            UserFitnessProfile.objects.get(user=user)
        except UserFitnessProfile.DoesNotExist:
            # No profile - trigger form mode
            print(f"[FITNESS] No profile found - triggering onboarding form for {user.username}")
            
            # Get FormAgent
            form_agent = Agent.objects.get(name='FormAgent')
            
            # Store form reference in memory (not the full config - it has functions)
            conversation.short_term_memory['form_type'] = 'fitness_onboarding'
            conversation.short_term_memory['form_module'] = 'fitness.agents.onboarding_form_config'
            conversation.short_term_memory['return_to_agent'] = conversation.agent.id
            conversation.short_term_memory['form_active'] = True
            
            # Switch conversation to FormAgent
            conversation.agent = form_agent
            conversation.save()
            
            # Let FormAgent handle this message
            from chat.agents.form_agent import FormAgent
            form_agent_instance = FormAgent(agent_model=form_agent)
            return form_agent_instance.process_message(message, conversation, user)
        
        # Normal LLM processing
        return super().process_message(message, conversation, user)
    
    def get_system_prompt(self) -> str:
        return self.agent_model.system_prompt
    
    def get_tools(self) -> list:
        """Provide all fitness tools for coaching"""
        return [
            get_fitness_profile,
            add_home_equipment,
            create_fitness_goal,
            get_fitness_goals,
            update_fitness_goal_status,
            add_measurement,
            get_measurements,
            get_latest_measurement,
        ]


def get_fitness_profile(ctx: RunContext[AgentDeps]) -> str:
    """
    Get the user's current fitness profile information.
    Use this FIRST when interacting with a user to check if they have completed their profile.
    
    Returns:
        User's fitness profile details or a message indicating no profile exists
    """
    from fitness.models import UserFitnessProfile
    
    user = ctx.deps.user
    print(f"[FITNESS] get_fitness_profile called for user: {user.username}")
    
    try:
        profile = UserFitnessProfile.objects.get(user=user)
        print(f"[FITNESS] Profile found for {user.username}")
        
        # Format equipment list
        equipment_names = list(profile.available_equipment.values_list('name', flat=True))
        equipment_str = ', '.join(equipment_names) if equipment_names else 'None specified'
        
        # Format days
        exercise_days_str = ', '.join(profile.exercise_days) if profile.exercise_days else 'Not set'
        run_days_str = ', '.join(profile.run_days) if profile.run_days else 'Not set'
        
        return f"""Fitness Profile:
• Fitness Level: {profile.get_fitness_level_display()}
• Exercises per week: {profile.exercises_per_week}
• Runs per week: {profile.runs_per_week}
• Exercise days: {exercise_days_str}
• Run days: {run_days_str}
• Exercise location: {profile.get_exercise_location_display()}
• Available equipment: {equipment_str}
• Injuries: {profile.injuries or 'None'}
• Restrictions: {profile.restrictions or 'None'}
• Profile created: {profile.created_at.strftime('%Y-%m-%d')}
• Last updated: {profile.updated_at.strftime('%Y-%m-%d')}"""
    
    except UserFitnessProfile.DoesNotExist:
        print(f"[FITNESS] No profile found for {user.username}")
        return "No fitness profile found. User needs to complete onboarding to create their fitness profile."


def create_or_update_fitness_profile(
    ctx: RunContext[AgentDeps],
    fitness_level: str,
    exercises_per_week: int,
    runs_per_week: int,
    exercise_days: list,
    run_days: list,
    exercise_location: str,
    injuries: str,
    restrictions: str,
    equipment_names: list = None
) -> str:
    """
    Create or update the user's fitness profile. ALL fields are REQUIRED for initial profile creation.
    Do NOT call this tool until you have collected ALL information from the user.
    
    REQUIRED fields - ask the user for each one:
        fitness_level: User's fitness level - REQUIRED, must be one of: 'inactive', 'light', 'moderate', 'active', 'very_active'
        exercises_per_week: Number of exercise sessions per week - REQUIRED (can be 0)
        runs_per_week: Number of running sessions per week - REQUIRED (can be 0)
        exercise_days: Days for exercise - REQUIRED (e.g., ['Monday', 'Wednesday', 'Friday'], can be empty list [])
        run_days: Days for running - REQUIRED (e.g., ['Tuesday', 'Thursday'], can be empty list [])
        exercise_location: Where user exercises - REQUIRED, must be one of: 'home', 'gym', 'both'
        injuries: Any injuries - REQUIRED (use empty string "" if none)
        restrictions: Any exercise restrictions - REQUIRED (use empty string "" if none)
    
    OPTIONAL field:
        equipment_names: List of equipment (optional - will auto-assign based on location if not provided)
    
    DO NOT make assumptions. DO NOT hallucinate values. ASK the user for each field.
    
    Returns:
        Confirmation message about profile creation/update
    """
    from fitness.models import UserFitnessProfile, Equipment
    
    user = ctx.deps.user
    print(f"[FITNESS] create_or_update_fitness_profile called for user: {user.username}")
    print(f"[FITNESS] Parameters: level={fitness_level}, ex_per_week={exercises_per_week}, runs_per_week={runs_per_week}")
    print(f"[FITNESS] Days: exercise={exercise_days}, run={run_days}")
    print(f"[FITNESS] Location: {exercise_location}, injuries: {injuries}, restrictions: {restrictions}")
    
    # Valid choices
    valid_fitness_levels = ['inactive', 'light', 'moderate', 'active', 'very_active']
    valid_locations = ['home', 'gym', 'both']
    
    # Validate fitness_level
    if fitness_level not in valid_fitness_levels:
        return f"Invalid fitness level '{fitness_level}'. Must be one of: {', '.join(valid_fitness_levels)}"
    
    # Validate exercise_location
    if exercise_location not in valid_locations:
        return f"Invalid exercise location '{exercise_location}'. Must be one of: {', '.join(valid_locations)}"
    
    # Get or create profile
    profile, created = UserFitnessProfile.objects.get_or_create(
        user=user,
        defaults={
            'fitness_level': fitness_level,
            'exercises_per_week': exercises_per_week,
            'runs_per_week': runs_per_week,
            'exercise_days': exercise_days,
            'run_days': run_days,
            'exercise_location': exercise_location,
            'injuries': injuries,
            'restrictions': restrictions,
        }
    )
    
    updates = []
    
    # Update all fields if profile already existed
    if not created:
        profile.fitness_level = fitness_level
        updates.append(f"fitness level to '{fitness_level}'")
        
        profile.exercises_per_week = exercises_per_week
        updates.append(f"exercises per week to {exercises_per_week}")
        
        profile.runs_per_week = runs_per_week
        updates.append(f"runs per week to {runs_per_week}")
        
        profile.exercise_days = exercise_days
        updates.append(f"exercise days to {', '.join(exercise_days) if exercise_days else 'none'}")
        
        profile.run_days = run_days
        updates.append(f"run days to {', '.join(run_days) if run_days else 'none'}")
        
        profile.exercise_location = exercise_location
        updates.append(f"exercise location to '{exercise_location}'")
        
        profile.injuries = injuries
        updates.append("injuries information")
        
        profile.restrictions = restrictions
        updates.append("restrictions information")
        
        profile.save()
    
    # Handle equipment - auto-assign based on location or use provided list
    if equipment_names is not None:
        # Explicitly provided equipment list
        profile.available_equipment.clear()
        added_equipment = []
        
        for eq_name in equipment_names:
            equipment, _ = Equipment.objects.get_or_create(name=eq_name.strip())
            profile.available_equipment.add(equipment)
            added_equipment.append(eq_name)
        
        if added_equipment:
            updates.append(f"equipment to {', '.join(added_equipment)}")
        else:
            updates.append("equipment (cleared)")
    else:
        # Auto-assign equipment based on location
        location = profile.exercise_location
        
        if location == 'gym' or location == 'both':
            # Gym access = all equipment available
            all_equipment = Equipment.objects.all()
            profile.available_equipment.set(all_equipment)
            if not created:
                updates.append("equipment (all equipment - gym access)")
        elif location == 'home':
            # Home = bodyweight only by default
            bodyweight, _ = Equipment.objects.get_or_create(name='body weight')
            profile.available_equipment.set([bodyweight])
            if not created:
                updates.append("equipment (bodyweight - home)")
    
    if created:
        result = f"✓ Fitness profile created successfully! You can now start your fitness journey."
        print(f"[FITNESS] ✓ Profile creation completed successfully for {user.username}")
        print(f"[FITNESS] Returning result to LLM: {result}")
        return result
    elif updates:
        result = f"✓ Fitness profile updated: {', '.join(updates)}"
        print(f"[FITNESS] ✓ Profile update completed for {user.username}")
        print(f"[FITNESS] Returning result to LLM: {result}")
        return result
    else:
        result = "No changes made to fitness profile."
        print(f"[FITNESS] No changes made for {user.username}")
        return result


@require_fitness_profile
def add_home_equipment(
    ctx: RunContext[AgentDeps],
    equipment_names: list
) -> str:
    """
    Add equipment available at home for users who exercise at home.
    Use this after profile creation when home users want to specify what equipment they have.
    
    Args:
        equipment_names: List of equipment names (e.g., ['dumbbells', 'resistance bands', 'pull-up bar'])
    
    Returns:
        Confirmation message about equipment added
    
    Common home equipment:
    - dumbbells, resistance bands, pull-up bar, kettlebell, yoga mat, 
    - bench, jump rope, foam roller, exercise ball, barbell, weight plates
    
    Examples:
        - add_home_equipment(equipment_names=['dumbbells', 'resistance bands'])
        - add_home_equipment(equipment_names=['kettlebell', 'yoga mat', 'pull-up bar'])
    """
    from fitness.models import UserFitnessProfile, Equipment
    
    user = ctx.deps.user
    profile = UserFitnessProfile.objects.get(user=user)
    
    # Check if user exercises at home
    if profile.exercise_location not in ['home', 'both']:
        return "Equipment management is primarily for home workouts. Your profile shows you exercise at the gym where all equipment is available."
    
    if not equipment_names:
        return "No equipment specified. Please provide equipment names."
    
    # Add equipment to existing equipment (don't replace)
    added_equipment = []
    for eq_name in equipment_names:
        equipment, created = Equipment.objects.get_or_create(name=eq_name.strip().lower())
        profile.available_equipment.add(equipment)
        added_equipment.append(eq_name)
    
    # Get current equipment list
    current_equipment = list(profile.available_equipment.values_list('name', flat=True))
    
    return f"✓ Added equipment: {', '.join(added_equipment)}\n\nYour current equipment: {', '.join(current_equipment)}"


@require_fitness_profile
def create_fitness_goal(
    ctx: RunContext[AgentDeps],
    goal: str,
    target_date: str,
    success_metrics: str
) -> str:
    """
    Create a new fitness goal for the user.
    Use this when the user wants to set a fitness goal during onboarding or anytime.
    
    Args:
        goal: Description of the fitness goal (e.g., "Lose 10 kg", "Run a 5K")
        target_date: Target completion date in YYYY-MM-DD format
        success_metrics: How success will be measured (e.g., "Weight under 70kg", "Complete 5K in under 30 minutes")
    
    Returns:
        Confirmation message about goal creation
    
    Examples:
        - create_fitness_goal(goal="Lose 10 kg", target_date="2026-06-01", success_metrics="Weight under 70kg")
        - create_fitness_goal(goal="Build muscle", target_date="2026-12-31", success_metrics="Increase bench press by 20kg")
    """
    from fitness.models import FitnessGoal
    
    user = ctx.deps.user
    
    # Validate and parse target_date
    try:
        parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    except ValueError:
        return f"Invalid date format '{target_date}'. Please use YYYY-MM-DD format (e.g., '2026-06-01')."
    
    # Check if date is in the future
    if parsed_date <= date.today():
        return f"Target date must be in the future. Today is {date.today().strftime('%Y-%m-%d')}."
    
    # Create the goal
    fitness_goal = FitnessGoal.objects.create(
        user=user,
        goal=goal,
        target_date=parsed_date,
        success_metrics=success_metrics,
        status='in_progress'
    )
    
    return f"✓ Fitness goal created: '{goal}' with target date {target_date}. Success will be measured by: {success_metrics}"


@require_fitness_profile
def get_fitness_goals(ctx: RunContext[AgentDeps], status: str = None) -> str:
    """
    Get the user's fitness goals.
    Use this to check what goals the user has set.
    
    Args:
        status: Optional filter by status - 'in_progress', 'completed', or 'abandoned'. If not provided, returns all goals.
    
    Returns:
        List of user's fitness goals
    """
    from fitness.models import FitnessGoal
    
    user = ctx.deps.user
    
    # Build query
    query = FitnessGoal.objects.filter(user=user)
    
    if status:
        valid_statuses = ['in_progress', 'completed', 'abandoned']
        if status not in valid_statuses:
            return f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
        query = query.filter(status=status)
    
    goals = query.order_by('-created_at')
    
    if not goals.exists():
        if status:
            return f"No {status.replace('_', ' ')} fitness goals found."
        return "No fitness goals found. User hasn't set any goals yet."
    
    # Format results
    results = []
    for g in goals:
        status_emoji = {
            'in_progress': '🔄',
            'completed': '✅',
            'abandoned': '❌'
        }.get(g.status, '•')
        
        results.append(
            f"{status_emoji} {g.goal}\n"
            f"   Target: {g.target_date.strftime('%Y-%m-%d')}\n"
            f"   Success metrics: {g.success_metrics}\n"
            f"   Status: {g.get_status_display()}\n"
            f"   Created: {g.created_at.strftime('%Y-%m-%d')}"
        )
    
    return "Fitness Goals:\n\n" + "\n\n".join(results)


@require_fitness_profile
def update_fitness_goal_status(
    ctx: RunContext[AgentDeps],
    goal_description: str,
    new_status: str
) -> str:
    """
    Update the status of a fitness goal.
    Use this when the user completes a goal or wants to abandon it.
    
    Args:
        goal_description: Description of the goal to update (should match or be similar to the goal text)
        new_status: New status - must be one of: 'in_progress', 'completed', 'abandoned'
    
    Returns:
        Confirmation message about status update
    
    Examples:
        - update_fitness_goal_status(goal_description="Lose 10 kg", new_status="completed")
        - update_fitness_goal_status(goal_description="Run a 5K", new_status="abandoned")
    """
    from fitness.models import FitnessGoal
    
    user = ctx.deps.user
    
    valid_statuses = ['in_progress', 'completed', 'abandoned']
    if new_status not in valid_statuses:
        return f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
    
    # Find goal by description (case-insensitive partial match)
    goals = FitnessGoal.objects.filter(
        user=user,
        goal__icontains=goal_description
    )
    
    if not goals.exists():
        return f"No fitness goal found matching '{goal_description}'. Please check the goal description."
    
    if goals.count() > 1:
        goal_list = "\n".join([f"- {g.goal}" for g in goals])
        return f"Multiple goals match '{goal_description}':\n{goal_list}\n\nPlease be more specific."
    
    # Update the goal
    goal = goals.first()
    old_status = goal.get_status_display()
    goal.status = new_status
    goal.save()
    
    status_messages = {
        'completed': f"🎉 Congratulations! Goal '{goal.goal}' marked as completed!",
        'abandoned': f"Goal '{goal.goal}' has been abandoned.",
        'in_progress': f"Goal '{goal.goal}' is now back in progress."
    }
    
    return status_messages.get(new_status, f"✓ Goal status updated from {old_status} to {goal.get_status_display()}.")


@require_fitness_profile
def add_measurement(
    ctx: RunContext[AgentDeps],
    measurement_type: str,
    value: float,
    date_recorded: str = None,
    notes: str = None
) -> str:
    """
    Record a new user measurement (weight, body fat, circumferences, etc.).
    Use this when the user reports a new measurement.
    
    Args:
        measurement_type: Type of measurement - must be one of: 'weight', 'body_fat', 'bmi', 'muscle_mass', 
                         'waist_circumference', 'hip_circumference', 'bicep_circumference', 
                         'chest_circumference', 'thigh_circumference'
        value: Measurement value (in kg for weight/mass, % for body_fat/bmi, cm for circumferences)
        date_recorded: Date of measurement in YYYY-MM-DD format (defaults to today if not provided)
        notes: Optional notes about the measurement
    
    Returns:
        Confirmation message about recorded measurement
    
    Examples:
        - add_measurement(measurement_type='weight', value=75.5)
        - add_measurement(measurement_type='body_fat', value=18.5, notes='Morning measurement after workout')
        - add_measurement(measurement_type='waist_circumference', value=85.0, date_recorded='2026-01-01')
    """
    from fitness.models import UserMeasurement
    
    user = ctx.deps.user
    
    # Valid measurement types
    valid_types = [
        'weight', 'body_fat', 'bmi', 'muscle_mass', 'waist_circumference',
        'hip_circumference', 'bicep_circumference', 'chest_circumference', 'thigh_circumference'
    ]
    
    if measurement_type not in valid_types:
        return f"Invalid measurement type '{measurement_type}'. Must be one of: {', '.join(valid_types)}"
    
    # Parse date if provided, otherwise use today
    if date_recorded:
        try:
            parsed_date = datetime.strptime(date_recorded, '%Y-%m-%d').date()
        except ValueError:
            return f"Invalid date format '{date_recorded}'. Please use YYYY-MM-DD format (e.g., '2026-01-01')."
    else:
        parsed_date = date.today()
    
    # Validate value is positive
    if value <= 0:
        return f"Measurement value must be greater than 0. Received: {value}"
    
    # Create the measurement
    measurement = UserMeasurement.objects.create(
        user=user,
        measurement_type=measurement_type,
        value=value,
        date_recorded=parsed_date,
        notes=notes or ''
    )
    
    # Get display name
    type_display = measurement.get_measurement_type_display()
    
    return f"✓ Recorded {type_display}: {value} on {parsed_date.strftime('%Y-%m-%d')}"


@require_fitness_profile
def get_measurements(
    ctx: RunContext[AgentDeps],
    measurement_type: str = None,
    limit: int = 10
) -> str:
    """
    Get the user's measurement history.
    Use this to track progress over time or check past measurements.
    
    Args:
        measurement_type: Type of measurement to filter by. If not provided, returns all measurement types.
        limit: Maximum number of measurements to return (default 10)
    
    Returns:
        List of user's measurements with dates and values
    
    Examples:
        - get_measurements(measurement_type='weight', limit=5)
        - get_measurements(limit=20)  # Get last 20 measurements of all types
    """
    from fitness.models import UserMeasurement
    
    user = ctx.deps.user
    
    # Build query
    query = UserMeasurement.objects.filter(user=user)
    
    if measurement_type:
        valid_types = [
            'weight', 'body_fat', 'bmi', 'muscle_mass', 'waist_circumference',
            'hip_circumference', 'bicep_circumference', 'chest_circumference', 'thigh_circumference'
        ]
        if measurement_type not in valid_types:
            return f"Invalid measurement type '{measurement_type}'. Must be one of: {', '.join(valid_types)}"
        query = query.filter(measurement_type=measurement_type)
    
    measurements = query.order_by('-date_recorded')[:limit]
    
    if not measurements.exists():
        if measurement_type:
            return f"No {measurement_type} measurements found."
        return "No measurements recorded yet."
    
    # Format results
    results = []
    for m in measurements:
        type_display = m.get_measurement_type_display()
        result_line = f"📊 {m.date_recorded.strftime('%Y-%m-%d')}: {type_display} = {m.value}"
        if m.notes:
            result_line += f"\n   Note: {m.notes}"
        results.append(result_line)
    
    header = f"Measurement History (last {len(measurements)}):"
    if measurement_type:
        type_obj = UserMeasurement()
        type_obj.measurement_type = measurement_type
        header = f"{type_obj.get_measurement_type_display()} History (last {len(measurements)}):"
    
    return header + "\n\n" + "\n\n".join(results)


@require_fitness_profile
def get_latest_measurement(
    ctx: RunContext[AgentDeps],
    measurement_type: str
) -> str:
    """
    Get the user's most recent measurement of a specific type.
    Use this when you need to know the current/latest value.
    
    Args:
        measurement_type: Type of measurement - must be one of: 'weight', 'body_fat', 'bmi', 'muscle_mass',
                         'waist_circumference', 'hip_circumference', 'bicep_circumference',
                         'chest_circumference', 'thigh_circumference'
    
    Returns:
        Most recent measurement of the specified type
    
    Examples:
        - get_latest_measurement(measurement_type='weight')
        - get_latest_measurement(measurement_type='body_fat')
    """
    from fitness.models import UserMeasurement
    
    user = ctx.deps.user
    
    valid_types = [
        'weight', 'body_fat', 'bmi', 'muscle_mass', 'waist_circumference',
        'hip_circumference', 'bicep_circumference', 'chest_circumference', 'thigh_circumference'
    ]
    
    if measurement_type not in valid_types:
        return f"Invalid measurement type '{measurement_type}'. Must be one of: {', '.join(valid_types)}"
    
    # Get latest measurement
    measurement = UserMeasurement.objects.filter(
        user=user,
        measurement_type=measurement_type
    ).order_by('-date_recorded').first()
    
    if not measurement:
        type_obj = UserMeasurement()
        type_obj.measurement_type = measurement_type
        return f"No {type_obj.get_measurement_type_display()} measurements recorded yet."
    
    type_display = measurement.get_measurement_type_display()
    result = f"Latest {type_display}: {measurement.value} (recorded on {measurement.date_recorded.strftime('%Y-%m-%d')})"
    
    if measurement.notes:
        result += f"\nNote: {measurement.notes}"
    
    # Check if there are previous measurements to show trend
    previous = UserMeasurement.objects.filter(
        user=user,
        measurement_type=measurement_type,
        date_recorded__lt=measurement.date_recorded
    ).order_by('-date_recorded').first()
    
    if previous:
        change = measurement.value - previous.value
        days_diff = (measurement.date_recorded - previous.date_recorded).days
        
        if change > 0:
            result += f"\n📈 +{change:.1f} from previous measurement ({days_diff} days ago)"
        elif change < 0:
            result += f"\n📉 {change:.1f} from previous measurement ({days_diff} days ago)"
        else:
            result += f"\n➡️ No change from previous measurement ({days_diff} days ago)"
    
    return result

# Register the agent
registry.register('fitness_agent', FitnessAgent)
