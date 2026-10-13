
from django.core.management.base import BaseCommand
from django.db import transaction

from recruitment.models import Candidate
from recruitment.matching import calculate_match


class Command(BaseCommand):
    help = "Recalculate existing candidate match scores"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Save recalculated scores to the database",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        candidates = Candidate.objects.select_related(
            "job"
        ).order_by("id")

        total = 0
        changed = 0
        skipped = 0

        if not apply_changes:
            self.stdout.write(
                self.style.WARNING(
                    "PREVIEW MODE - No database changes"
                )
            )

        with transaction.atomic():

            for candidate in candidates:
                total += 1

                # Check HR ownership
                if candidate.owner_id != candidate.job.owner_id:
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIPPED #{candidate.id}: "
                            "HR ownership mismatch"
                        )
                    )
                    continue

                # Check extracted resume text
                if not candidate.extracted_text.strip():
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIPPED #{candidate.id}: "
                            "No resume text"
                        )
                    )
                    continue

                # Recalculate using Matching Engine V2
                result = calculate_match(
                    candidate.extracted_text,
                    candidate.job.description,
                )

                if not result["required_skills"]:
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIPPED #{candidate.id}: "
                            "No recognized JD skills"
                        )
                    )
                    continue

                new_score = result["score"]
                new_matched = ", ".join(
                    result["matched_skills"]
                )
                new_missing = ", ".join(
                    result["missing_skills"]
                )

                is_changed = (
                    candidate.match_score != new_score
                    or candidate.matched_skills != new_matched
                    or candidate.missing_skills != new_missing
                )

                if not is_changed:
                    continue

                changed += 1

                self.stdout.write(
                    f"Candidate #{candidate.id} | "
                    f"{candidate.name} | "
                    f"Old: {candidate.match_score:.0f}% | "
                    f"New: {new_score}%"
                )

                if apply_changes:
                    candidate.match_score = new_score
                    candidate.matched_skills = new_matched
                    candidate.missing_skills = new_missing

                    candidate.save(
                        update_fields=[
                            "match_score",
                            "matched_skills",
                            "missing_skills",
                        ]
                    )

        self.stdout.write("")
        self.stdout.write(
            f"Total Candidates: {total}"
        )
        self.stdout.write(
            f"Changed Candidates: {changed}"
        )
        self.stdout.write(
            f"Skipped Candidates: {skipped}"
        )

        if apply_changes:
            self.stdout.write(
                self.style.SUCCESS(
                    "Candidate scores updated successfully!"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Preview complete. "
                    "Use --apply to save changes."
                )
            )
