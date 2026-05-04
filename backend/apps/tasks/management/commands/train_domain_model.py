"""
Management command: train_domain_model

Train or retrain the RandomForest domain predictor from available
AssessmentAttempt data (+ synthetic seed data).

Usage:
    python manage.py train_domain_model              # train with seed data
    python manage.py train_domain_model --no-seed   # real data only
    python manage.py train_domain_model --info       # show current model info
"""
import json
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Train or retrain the ML domain predictor model."

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-seed',
            action='store_true',
            dest='no_seed',
            help='Train on real student data only (skip synthetic seed data).',
        )
        parser.add_argument(
            '--info',
            action='store_true',
            dest='info',
            help='Display current model metadata without training.',
        )

    def handle(self, *args, **options):
        from apps.tasks.domain_predictor import (
            DomainPredictorML,
            MODEL_PATH,
            META_PATH,
        )

        # ── Info mode ─────────────────────────────────────────────────────
        if options['info']:
            if not MODEL_PATH.exists():
                self.stdout.write(self.style.WARNING("No trained model found."))
                self.stdout.write(
                    "Run 'python manage.py train_domain_model' to train one."
                )
                return

            try:
                with open(META_PATH) as f:
                    meta = json.load(f)
                self.stdout.write(
                    f"  Trained at  : {meta.get('trained_at', 'unknown')}\n"
                    f"  Accuracy    : {meta.get('accuracy', 0) * 100:.1f}%\n"
                    f"  Samples     : {meta.get('n_samples', '?')}\n"
                    f"  Model path  : {MODEL_PATH}\n"
                    f"  Features    : {', '.join(meta.get('feature_names', []))}"
                )
            except Exception as exc:
                self.stderr.write(f"Could not read model metadata: {exc}")
            return

        # ── Training mode ──────────────────────────────────────────────────
        include_seed = not options['no_seed']
        seed_note    = "with synthetic seed data" if include_seed else "on real data only"
        self.stdout.write(f"Training domain predictor {seed_note}…\n")

        try:
            result = DomainPredictorML.train(include_seed=include_seed)
        except RuntimeError as exc:
            raise CommandError(str(exc))
        except Exception as exc:
            raise CommandError(f"Unexpected error during training: {exc}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n  Model trained successfully!\n"
                f"  Accuracy  : {result['accuracy'] * 100:.1f}%\n"
                f"  Samples   : {result['n_samples']}\n"
                f"  Saved to  : {result['model_path']}"
            )
        )
        self.stdout.write(
            "\nRun 'python manage.py train_domain_model --info' any time to check model status."
        )
