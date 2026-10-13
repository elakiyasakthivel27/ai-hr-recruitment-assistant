
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "recruitment_project.settings"
)
django.setup()

from recruitment.models import Candidate
from recruitment.matching import calculate_match

for c in Candidate.objects.all():
    result = calculate_match(
        c.extracted_text,
        c.job.description
    )

    c.match_score = result["score"]
    c.matched_skills = ", ".join(result["matched_skills"])
    c.missing_skills = ", ".join(result["missing_skills"])
    c.save()

    print(
        c.name,
        c.match_score,
        c.matched_skills,
        c.missing_skills
    )

print("All candidate scores updated!")