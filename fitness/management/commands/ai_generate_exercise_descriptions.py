import os
import time
from django.core.management.base import BaseCommand
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from fitness.models import Exercise


class Command(BaseCommand):
    help = 'Generate user-facing exercise descriptions using an AI agent (overwrites existing descriptions).'

    def handle(self, *args, **options):
        # Configure model/provider
        ollama_model = OpenAIChatModel(
            model_name=os.environ.get('AI_MODEL_NAME', 'llama3.2:latest'),
            provider=OllamaProvider(base_url=os.environ.get('OLLAMA_BASE_URL')),
        )

        agent = Agent(
            ollama_model,
            system_prompt=(
                "You are a helpful content generator that converts exercise data into a concise, user-facing description.\n"
                "Input will include name, equipment, target muscles/body areas and step-by-step instructions.\n"
                "Produce 1–2 short sentences (20–50 words) describing the exercise for an end user.\n"
                "do not explain how to do the exercise; focus on what it is and which muscles it targets, if it needs equipment.\n"
                "Return ONLY the description text. Do not add labels, JSON, or commentary. Keep it factual and concise."
            ),
        )

        qs = Exercise.objects.all().order_by('id')
        total = qs.count()
        print(f'🔎 Found {total} exercises to generate descriptions for')

        updated = 0
        errors = 0

        for idx, ex in enumerate(qs.iterator(), start=1):
            start_ts = time.time()
            try:
                # Build deterministic context from exercise fields
                context = ex.build_embedding_text()

                prompt = (
                    f"Exercise name: {ex.name}\n"
                    f"Context: {context}\n\n"
                    "Write a short (1-2 sentence) user-facing description for this exercise."
                )

                print(f'[{idx}/{total}] Generating description for: {ex.name} (id={ex.id})')
                resp = agent.run_sync(prompt)
                desc = (resp.output or '').strip()
                # sanitize single-line and trim
                desc = ' '.join(desc.split())
                if len(desc) > 300:
                    desc = desc[:300].rsplit(' ', 1)[0] + '...'

                if not desc:
                    print(f'   ⚠️ AI returned empty description for {ex.name}; skipping')
                    errors += 1
                    continue

                # Save description if changed
                if ex.description != desc:
                    ex.description = desc
                    ex.save(update_fields=['description'])
                    elapsed = time.time() - start_ts
                    print(f'   ✅ Saved ({elapsed:.2f}s): {desc[:120]}')
                    updated += 1
                else:
                    print('   — No change')

            except Exception as e:
                errors += 1
                print(f'   ❌ Error for {ex.name}: {e}')

        print(f'✨ Done. Updated {updated} descriptions, {errors} errors.')
