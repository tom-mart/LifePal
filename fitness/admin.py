from django.contrib import admin

from .models import (
    BodyPart,
    BodyArea,
    Equipment,
    Exercise,
    UserFitnessProfile,
    FitnessGoal,
    FavouriteExercise,
    ExcludedExercise,
    WorkoutPlan,
    Workout,
    ExerciseSet,
    FitnessTest,
    FitnessTestExercise,
    UserMeasurement
)
                    

admin.site.register(BodyPart)
admin.site.register(BodyArea)
admin.site.register(Equipment)
admin.site.register(Exercise)
admin.site.register(UserFitnessProfile)
admin.site.register(FitnessGoal)
admin.site.register(FavouriteExercise)
admin.site.register(ExcludedExercise)
admin.site.register(WorkoutPlan)
admin.site.register(Workout)
admin.site.register(ExerciseSet)
admin.site.register(FitnessTest)
admin.site.register(FitnessTestExercise)
admin.site.register(UserMeasurement)