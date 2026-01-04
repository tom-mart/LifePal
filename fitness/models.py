from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from pgvector.django import VectorField


class BodyPart(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class BodyArea(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    # Comprehensive exercise database combining ExerciseDB dataset 
    # with custom tracking capabilities for fitness coaching.

    name = models.CharField(
        max_length=200, 
        db_index=True,
        help_text="Exercise name (e.g., 'stationary bike run')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Additional description or notes about the exercise"
    )

    instructions = models.JSONField(
        default=list,
        help_text="Step-by-step instructions as array of strings"
    )
    
    # === ANATOMICAL TARGETING ===
    target_body_parts = models.ManyToManyField(
        BodyPart,
        related_name='exercises_as_primary',
        blank=True,
        help_text="Primary body part targeted"
    )
    secondary_body_parts = models.ManyToManyField(
        BodyPart,
        related_name='exercises_as_secondary',
        blank=True,
        help_text="Secondary body part engaged"
    )
    body_areas = models.ManyToManyField(
        BodyArea,
        related_name='exercises',
        blank=True,
        help_text="Body areas/regions targeted"
    )
    
    # === EQUIPMENT & REQUIREMENTS ===
    equipment_required = models.ManyToManyField(
        Equipment,
        related_name='exercises',
        blank=True,
        help_text="Equipment needed for this exercise"
    )
    
    # === TRACKING METRICS (Boolean Flags) ===
    tracks_reps = models.BooleanField(
        default=False,
        help_text="Can track repetitions (e.g., push-ups, squats)"
    )
    tracks_weight = models.BooleanField(
        default=False,
        help_text="Can track weight/resistance (e.g., barbell exercises)"
    )
    tracks_duration = models.BooleanField(
        default=False,
        help_text="Can track duration (e.g., planks, cardio)"
    )
    tracks_distance = models.BooleanField(
        default=False,
        help_text="Can track distance (e.g., running, cycling)"
    )
    tracks_pace = models.BooleanField(
        default=False,
        help_text="Can track pace/speed (e.g., running, cycling)"
    )

    # === EMBEDDING FOR SEMANTIC SEARCH ===
    embedding = VectorField(
        dimensions=768,
        null=True,
        blank=True,
        help_text="Semantic embedding for the exercise (pgvector)"
    )

    embedding_model = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Name of the model used to generate the embedding"
    )

    embedding_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the embedding was generated"
    )

    # === CUSTOMIZATION & OWNERSHIP ===
    is_custom = models.BooleanField(
        default=False,
        help_text="True if created by user, False if from dataset"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_exercises',
        help_text="User who created this custom exercise"
    )
    
    # === TIMESTAMPS ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
    
    def __str__(self):
        return self.name
    
    def get_tracking_metrics(self):
        #Returns list of metrics this exercise can track.
        #Only includes metrics for fields that exist on the model.

        metrics = []
        if self.tracks_reps:
            metrics.append('reps')
        if self.tracks_weight:
            metrics.append('weight')
        if self.tracks_duration:
            metrics.append('duration')
        if self.tracks_distance:
            metrics.append('distance')
        if self.tracks_pace:
            metrics.append('pace')
        return metrics
    
    def is_equipment_free(self):
        #Check if exercise requires no equipment.
        # Treat an exercise as equipment-free when it has no related equipment
        # OR when the only equipment is 'body weight' (case-insensitive).

        qs = self.equipment_required.all()
        if not qs.exists():
            return True
        names = list(qs.values_list('name', flat=True))
        # consider equipment-free only when the sole entry is 'body weight'
        return len(names) == 1 and names[0].strip().lower() == 'body weight'

    def build_embedding_text(self) -> str:
        """Build a deterministic text blob representing this exercise for embedding.

        Combines name, description, instructions, equipment and body part/area names.
        """
        parts = []
        parts.append(self.name or "")
        if self.description:
            parts.append(self.description)

        # instructions may be stored as list or string
        instr = self.instructions or []
        if isinstance(instr, list):
            parts.append("\n".join([str(x) for x in instr if x]))
        else:
            parts.append(str(instr))

        # equipment
        try:
            equipments = list(self.equipment_required.values_list('name', flat=True))
        except Exception:
            equipments = []
        if equipments:
            parts.append(", ".join(equipments))

        # target body parts and body areas
        try:
            tbp = list(self.target_body_parts.values_list('name', flat=True))
        except Exception:
            tbp = []
        if tbp:
            parts.append(", ".join(tbp))

        try:
            areas = list(self.body_areas.values_list('name', flat=True))
        except Exception:
            areas = []
        if areas:
            parts.append(", ".join(areas))

        # final canonical tag
        parts.append("exercise")

        # join with clear separators to keep deterministic ordering
        return "\n\n".join([p.strip() for p in parts if p is not None and str(p).strip() != ""])

class UserFitnessProfile(models.Model):

    FITNESS_LEVEL_CHOICES = [
        ('inactive', 'Inactive'),
        ('light', 'Lightly Active'),
        ('moderate', 'Moderately Active'),
        ('active', 'Active'),
        ('very_active', 'Very Active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVEL_CHOICES)
    exercises_per_week = models.PositiveIntegerField(default=0)
    runs_per_week = models.PositiveIntegerField(default=0)
    exercise_days = models.JSONField(default=list)  # e.g., ['Monday', 'Wednesday', 'Friday']
    run_days = models.JSONField(default=list)  # e.g., ['Tuesday', 'Thursday']
    exercise_location = models.CharField(max_length=20, choices=[('home', 'Home'), ('gym', 'Gym'), ('both', 'Both')])
    available_equipment = models.ManyToManyField(Equipment, blank=True)
    injuries = models.TextField(blank=True, null=True)
    restrictions = models.TextField(blank=True, null=True)
    # Add more fields as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class FitnessGoal(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.CharField(max_length=255)
    target_date = models.DateField()
    success_metrics = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.goal}"

class FavouriteExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'exercise')

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} (Favourite)"

class ExcludedExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'exercise')

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} (Excluded)"

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    number_of_workouts = models.PositiveIntegerField()
    number_of_runs = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Workout(models.Model):
    STATUS_CHOICES = [  
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('attempted', 'Attempted'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='workouts')
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workout {self.id} for {self.user.username} on {self.date}"

class ExerciseSet(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('attempted', 'Attempted'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercise_sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, help_text="Order of this set in the workout")
    notes = models.TextField(blank=True, null=True)
    reps = models.PositiveIntegerField(null=True, blank=True, help_text="Number of repetitions (if applicable)")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kilograms (if applicable)")
    duration = models.FloatField(null=True, blank=True, help_text="Duration in seconds (if applicable)")
    distance = models.FloatField(null=True, blank=True, help_text="Distance in meters (if applicable)")
    pace = models.FloatField(null=True, blank=True, help_text="Pace (e.g., min/km, if applicable)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    user_feedback = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} (Set {self.order+1}) in Workout {self.workout.id}"

class FitnessTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Test name or type (e.g., 'Strength Assessment Jan 2026')")
    date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} for {self.user.username} on {self.date}"

class FitnessTestExercise(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('attempted', 'Attempted'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    fitness_test = models.ForeignKey(FitnessTest, on_delete=models.CASCADE, related_name='test_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, help_text="Order of this test exercise in the test")
    instructions = models.TextField(blank=True, null=True, help_text="Custom instructions for this test exercise")
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True, help_text="Duration in seconds (if applicable)")
    distance = models.FloatField(null=True, blank=True, help_text="Distance in meters (if applicable)")
    pace = models.FloatField(null=True, blank=True, help_text="Pace (e.g., min/km, if applicable)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    user_feedback = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, help_text="Unit of measurement (kg, reps, sec, m, etc)")
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} (Test {self.order+1}) in {self.fitness_test.name}"

class UserMeasurement(models.Model):
    MEASUREMENT_TYPE_CHOICES = [
        ('weight', 'Weight (kg)'),
        ('body_fat', 'Body Fat Percentage (%)'),
        ('bmi', 'Body Mass Index (BMI)'),
        ('muscle_mass', 'Muscle Mass (kg)'),
        ('waist_circumference', 'Waist Circumference (cm)'),
        ('hip_circumference', 'Hip Circumference (cm)'),
        ('bicep_circumference', 'Bicep Circumference (cm)'),
        ('chest_circumference', 'Chest Circumference (cm)'),
        ('thigh_circumference', 'Thigh Circumference (cm)'),
        # Add more measurement types as needed
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    measurement_type = models.CharField(max_length=50, choices=MEASUREMENT_TYPE_CHOICES)
    value = models.FloatField()
    date_recorded = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.user.username} - {self.measurement_type} on {self.date_recorded}: {self.value}"