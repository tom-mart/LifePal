from django.core.management.base import BaseCommand
from fitness.models import BodyPart, BodyArea, Equipment, Exercise
import json
import os
from django.conf import settings

DATA_DIR = os.path.join(settings.BASE_DIR, 'fitness', 'exercise_data')

class Command(BaseCommand):
    help = 'Import fitness datasets (bodyareas, bodyparts, equipment, exercises) into the database.'

    def handle(self, *args, **options):
        self.import_bodyareas()
        self.import_bodyparts()
        self.import_equipment()
        self.import_exercises()
        self.stdout.write(self.style.SUCCESS('All fitness data imported successfully.'))

    def import_bodyareas(self):
        path = os.path.join(DATA_DIR, 'bodyareas.json')
        with open(path) as f:
            data = json.load(f)
        for entry in data:
            obj, created = BodyArea.objects.get_or_create(name=entry['name'])
            if created:
                self.stdout.write(f'Created BodyArea: {obj.name}')

    def import_bodyparts(self):
        path = os.path.join(DATA_DIR, 'bodyparts.json')
        with open(path) as f:
            data = json.load(f)
        for entry in data:
            obj, created = BodyPart.objects.get_or_create(name=entry['name'])
            if created:
                self.stdout.write(f'Created BodyPart: {obj.name}')

    def import_equipment(self):
        path = os.path.join(DATA_DIR, 'equipments.json')
        with open(path) as f:
            data = json.load(f)
        for entry in data:
            obj, created = Equipment.objects.get_or_create(name=entry['name'])
            if created:
                self.stdout.write(f'Created Equipment: {obj.name}')

    def import_exercises(self):
        path = os.path.join(DATA_DIR, 'exercises.json')
        with open(path) as f:
            data = json.load(f)
        for entry in data:
            name = entry.get('name')
            description = entry.get('description', '')
            instructions = entry.get('instructions', [])
            exercise, created = Exercise.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'instructions': instructions,
                    'is_custom': False
                }
            )
            # Map targetMuscles to BodyParts (target_body_parts)
            for muscle in entry.get('targetMuscles', []):
                bp = BodyPart.objects.filter(name=muscle).first()
                if bp:
                    exercise.target_body_parts.add(bp)
            # Map bodyParts to BodyAreas (body_areas)
            for area in entry.get('bodyParts', []):
                ba = BodyArea.objects.filter(name=area).first()
                if ba:
                    exercise.body_areas.add(ba)
            # Map equipment (fix: use 'equipments' key from dataset)
            for eq in entry.get('equipments', []):
                eq_obj = Equipment.objects.filter(name=eq).first()
                if eq_obj:
                    exercise.equipment_required.add(eq_obj)
            exercise.save()
            if created:
                self.stdout.write(f'Created Exercise: {exercise.name}')
