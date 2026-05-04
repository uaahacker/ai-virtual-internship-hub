"""
Management command: recompute_clusters

Recomputes student cluster assignments and summaries using the enhanced
23-dim KMeans-based StudentClusterer.

Usage:
    python manage.py recompute_clusters              # all students (batch sklearn)
    python manage.py recompute_clusters --all        # same as above (explicit)
    python manage.py recompute_clusters --student-id 42
    python manage.py recompute_clusters --dry-run    # report without saving
"""
import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Recompute cluster labels and summaries for students."

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all_students',
            help='Recompute clusters for every student (default if no other flag given).',
        )
        parser.add_argument(
            '--student-id',
            type=int,
            dest='student_id',
            help='Recompute cluster for a single student by user ID.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Print what would be saved without writing to the database.',
        )
        parser.add_argument(
            '--batch',
            action='store_true',
            dest='batch',
            help=(
                'Use sklearn KMeans batch method when processing all students '
                '(default). Ignored when --student-id is given.'
            ),
        )

    def handle(self, *args, **options):
        from apps.accounts.models import User, StudentProfile
        from apps.tasks.ml_engine import (
            StudentClusterer,
            _build_cluster_summary,
            CLUSTER_LABELS,
        )

        dry_run    = options['dry_run']
        student_id = options.get('student_id')

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be saved.\n"))

        # ── Single student ──────────────────────────────────────────────────
        if student_id:
            try:
                student = User.objects.get(id=student_id, role='Student')
            except User.DoesNotExist:
                raise CommandError(f"No student with id={student_id} found.")

            feat, raw_data = StudentClusterer._build_cluster_feature_vector(student)
            cluster_id, label = StudentClusterer.compute_cluster(student)
            summary = _build_cluster_summary(cluster_id, label, raw_data)

            self.stdout.write(
                f"Student {student.name} ({student.id}): "
                f"{label} — {summary['display_name']}"
            )
            if not dry_run:
                profile, _ = StudentProfile.objects.get_or_create(user=student)
                profile.cluster_id      = cluster_id
                profile.cluster_label   = label
                profile.cluster_summary = summary
                profile.save(update_fields=['cluster_id', 'cluster_label', 'cluster_summary'])
                self.stdout.write(self.style.SUCCESS("  ✓ Saved."))
            return

        # ── All students ────────────────────────────────────────────────────
        students = User.objects.filter(role='Student')
        total    = students.count()
        if total == 0:
            self.stdout.write("No students found.")
            return

        self.stdout.write(f"Processing {total} student(s)…\n")

        # Use per-student update (which internally builds the feature vector)
        # rather than the batch sklearn method so that cluster_summary is
        # computed and stored for every student.
        updated = 0
        errors  = 0
        for student in students.iterator():
            try:
                feat, raw_data = StudentClusterer._build_cluster_feature_vector(student)
                cluster_id, label = StudentClusterer.compute_cluster(student)
                summary = _build_cluster_summary(cluster_id, label, raw_data)

                display = summary.get('display_name', label)
                self.stdout.write(f"  {student.name:40s} → {label:12s} ({display})")

                if not dry_run:
                    profile, _ = StudentProfile.objects.get_or_create(user=student)
                    profile.cluster_id      = cluster_id
                    profile.cluster_label   = label
                    profile.cluster_summary = summary
                    profile.save(update_fields=['cluster_id', 'cluster_label', 'cluster_summary'])

                updated += 1
            except Exception as exc:
                self.stderr.write(f"  ERROR for student {student.id}: {exc}")
                logger.exception("recompute_clusters error for student %s", student.id)
                errors += 1

        verb = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"\n{verb} {updated} student(s). Errors: {errors}.")
        )
