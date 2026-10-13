
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "recruitment_project.settings"
)
django.setup()

from recruitment.models import Candidate
from recruitment.views import extract_resume_text
from recruitment.matching import calculate_match

candidates = Candidate.objects.filter(extracted_text="")

print("Candidates needing repair:", candidates.count())

for candidate in candidates:
    print("\nProcessing:", candidate.name)

    try:
        if not candidate.resume:
            print("Skipped: No resume file")
            continue

        with candidate.resume.open("rb") as resume_file:
            extracted_text = extract_resume_text(resume_file)

        if not extracted_text:
            print("FAILED: No text extracted")
            continue

        result = calculate_match(
            extracted_text,
            candidate.job.description
        )

        candidate.extracted_text = extracted_text
        candidate.match_score = result["score"]
        candidate.matched_skills = ", ".join(
            result["matched_skills"]
        )
        candidate.missing_skills = ", ".join(
            result["missing_skills"]
        )

        candidate.save(
            update_fields=[
                "extracted_text",
                "match_score",
                "matched_skills",
                "missing_skills",
            ]
        )

        print("SUCCESS: Text extracted")
        print("Characters:", len(extracted_text))
        print("Match score:", candidate.match_score)

    except Exception as e:
        print("ERROR:", repr(e))

print("\nRepair process completed.")