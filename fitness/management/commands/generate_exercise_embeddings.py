from django.core.management.base import BaseCommand
from django.utils import timezone
from fitness.models import Exercise
from agents.services.embedding_service import EmbeddingService


class Command(BaseCommand):
    help = 'Generate semantic embeddings for all exercises and store them in the Exercise.embedding field.'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, default='nomic-embed-text:v1.5', help='Embedding model to use')
        parser.add_argument('--limit', type=int, default=0, help='Limit to first N exercises (0 = all)')

    def handle(self, *args, **options):
        model = options.get('model')
        limit = options.get('limit')

        svc = EmbeddingService()

        qs = Exercise.objects.all().order_by('id')
        total = qs.count()
        if limit and limit > 0:
            qs = qs[:limit]
            total = min(total, limit)

        print(f'🔎 Found {total} exercise(s) to embed using model {model}')

        generated = 0
        errors = 0

        for idx, ex in enumerate(qs, start=1):
            try:
                text = ex.build_embedding_text()
                if not text.strip():
                    print(f'[{idx}/{total}] Skipping {ex.name} (empty text)')
                    continue

                print(f'[{idx}/{total}] Generating embedding for: {ex.name} (id={ex.id})')
                emb = svc.generate_embedding(text=text, model=model)

                # store embedding and metadata
                ex.embedding = emb
                ex.embedding_model = model
                ex.embedding_generated_at = timezone.now()
                ex.save(update_fields=['embedding', 'embedding_model', 'embedding_generated_at'])

                generated += 1
                print(f'   ✅ Saved embedding for {ex.name} (len={len(emb)})')

            except Exception as e:
                errors += 1
                print(f'   ❌ Error embedding {ex.name}: {e}')

        print(f'✨ Done. Generated {generated} embeddings, {errors} errors')
