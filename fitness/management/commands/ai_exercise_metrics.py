import os
import json
import re
import time
from django.core.management.base import BaseCommand
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from fitness.models import Exercise


class Command(BaseCommand):
    help = 'Analyze exercises and set tracking flags (reps, weight, duration, distance, pace) using an AI agent.'

    def handle(self, *args, **options):
        # Configure model/provider (uses OLLAMA_BASE_URL env variable if present)
        ollama_model = OpenAIChatModel(
            model_name="llama3.2:latest",
            provider=OllamaProvider(base_url=os.environ.get("OLLAMA_BASE_URL")),
        )

        agent = Agent(
            ollama_model,
            system_prompt=(
                "You are an exercise tracking classifier.\n"
                "Given an exercise name, description and step-by-step instructions, decide which of the following metrics the exercise should track: "
                "tracks_reps, tracks_weight, tracks_duration, tracks_distance, tracks_pace.\n"
                "Return ONLY a single JSON object with these five keys and boolean values. NO additional text.\n"
                "Be conservative when unsure, but if the exercise name or equipment indicates bars/dumbbells/kettlebells/plates/machines, prefer `tracks_weight`: true.\n"
                "Examples (exact JSON only):\n"
                "{\"tracks_reps\": true, \"tracks_weight\": true, \"tracks_duration\": false, \"tracks_distance\": false, \"tracks_pace\": false}\n"
                "{\"tracks_reps\": false, \"tracks_weight\": false, \"tracks_duration\": true, \"tracks_distance\": false, \"tracks_pace\": false}\n"
                "{\"tracks_reps\": false, \"tracks_weight\": false, \"tracks_duration\": false, \"tracks_distance\": true, \"tracks_pace\": true}\n"
            ),
        )

        qs = Exercise.objects.all()
        total = qs.count()
        print(f'🔎 Found {total} exercises to analyze')

        updated = 0

        for idx, ex in enumerate(qs.iterator(), start=1):
            start_ts = time.time()
            print(f'\n[{idx}/{total}] Processing: {ex.name} (id={ex.id})')
            # Build analyzed text
            instructions = ex.instructions
            if isinstance(instructions, list):
                instructions_text = "\n".join([str(x) for x in instructions])
            else:
                instructions_text = str(instructions or "")

            # Gather equipment and simple heuristics to guide the agent and post-processing
            equipment_names = list(ex.equipment_required.values_list('name', flat=True)) if hasattr(ex, 'equipment_required') else []
            equip_text = ", ".join(equipment_names)

            prompt = (
                f"Exercise name: {ex.name}\n"
                f"Description: {ex.description or ''}\n"
                f"Equipment: {equip_text}\n"
                f"Instructions:\n{instructions_text}\n\n"
                f"Return only JSON with the five boolean fields: tracks_reps, tracks_weight, tracks_duration, tracks_distance, tracks_pace."
            )

            try:
                # Show prompt summary length for debugging
                print(f'   Prompt length: {len(prompt)} chars')
                resp = agent.run_sync(prompt)
                out = (resp.output or "").strip()
                out_preview = out if len(out) < 800 else out[:800] + '...'
                print('   AI raw output (truncated):', out_preview)

                # Try to parse JSON directly; if it fails, extract JSON substring
                parsed = None
                try:
                    parsed = json.loads(out)
                except Exception:
                    m = re.search(r"(\{.*\})", out, re.S)
                    if m:
                        try:
                            parsed = json.loads(m.group(1))
                        except Exception:
                            parsed = None

                # Fallback heuristic if AI output isn't parseable
                if not isinstance(parsed, dict):
                    text = f"{ex.name} {ex.description} {instructions_text} {equip_text}".lower()
                    parsed = {
                        "tracks_reps": any(w in text for w in ["rep", "reps", "repetition", "repetitions", "sets", "curl", "press", "squat", "deadlift", "row"]),
                        "tracks_weight": any(w in text for w in ["kg", "g", "lb", "lbs", "weight", "dumbbell", "barbell", "kettlebell", "plate", "plates", "machine", "smith", "olympic"]) or any(k in (n or "").lower() for n in equipment_names for k in ["dumbbell", "barbell", "kettlebell", "plate", "machine", "smith", "olympic"]),
                        "tracks_duration": any(w in text for w in ["hold", "sec", "second", "seconds", "minute", "minutes", "duration", "timed", "plank", "tabata", "interval"]),
                        "tracks_distance": any(w in text for w in ["km", "miles", "mile", "distance", "meter", "metre", "run", "cycle", "bike", "swim", "rower"]),
                        "tracks_pace": any(w in text for w in ["pace", "speed", "mph", "kph", "km/h", "min/km", "min/mile"]) or ("run" in text and any(w in text for w in ["pace", "speed"])),
                    }

                # If equipment clearly indicates weights, prefer tracks_weight True
                weight_equipment_keywords = ["dumbbell", "barbell", "kettlebell", "plate", "plates", "machine", "smith", "olympic"]
                equipment_has_weight = any(k in (n or "").lower() for n in equipment_names for k in weight_equipment_keywords)
                name_has_weight = any(k in ex.name.lower() for k in weight_equipment_keywords)
                cable_in_equipment = any("cable" in (n or "").lower() for n in equipment_names)
                if equipment_has_weight or name_has_weight or cable_in_equipment:
                    parsed = parsed if isinstance(parsed, dict) else {}
                    parsed['tracks_weight'] = True
                    if cable_in_equipment:
                        print('   Enforced: tracks_weight=True due to cable equipment')
                    else:
                        print('   Heuristic: forced tracks_weight=True due to equipment/name')

                # Show parsed JSON for debugging
                print('   Parsed JSON:', json.dumps(parsed))

                # Ensure booleans
                final = {
                    'tracks_reps': bool(parsed.get('tracks_reps')),
                    'tracks_weight': bool(parsed.get('tracks_weight')),
                    'tracks_duration': bool(parsed.get('tracks_duration')),
                    'tracks_distance': bool(parsed.get('tracks_distance')),
                    'tracks_pace': bool(parsed.get('tracks_pace')),
                }

                changed = False
                for k, v in final.items():
                    if getattr(ex, k) != v:
                        setattr(ex, k, v)
                        changed = True

                if changed:
                    ex.save()
                    updated += 1
                    elapsed = time.time() - start_ts
                    msg = f'✅ Updated: {ex.name} -> {final} (elapsed: {elapsed:.2f}s)'
                    print(msg)
                else:
                    elapsed = time.time() - start_ts
                    msg = f'— Skipped (no change): {ex.name}  Elapsed: {elapsed:.2f}s'
                    print(msg)

            except Exception as e:
                # Dump some debugging info on error
                print(f'❌ Error processing {ex.name}: {e}')
                try:
                    print(f'   Prompt was: {prompt[:1000]}')
                except Exception:
                    pass
        print(f'✨ Done. Updated {updated} exercise(s) out of {total}.')
