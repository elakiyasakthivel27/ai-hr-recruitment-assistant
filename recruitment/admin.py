
from django.contrib import admin
from django.utils.html import format_html
from .models import Job, Candidate


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "job",
        "match_score_display",
        "uploaded_at",
    )

    search_fields = ("name", "email", "extracted_text")
    list_filter = ("job", "uploaded_at")

    readonly_fields = (
        "show_extracted_text",
        "match_score",
        "matched_skills",
        "missing_skills",
    )

    fieldsets = (
        ("Candidate Details", {
            "fields": ("name", "email", "job", "resume")
        }),
        ("Resume Matching Results", {
            "fields": (
                "match_score",
                "matched_skills",
                "missing_skills",
            )
        }),
        ("Extracted Resume Text", {
            "fields": ("show_extracted_text",)
        }),
    )

    @admin.display(description="Match Score")
    def match_score_display(self, obj):
        return f"{obj.match_score:.0f}%"

    @admin.display(description="Extracted Resume Text")
    def show_extracted_text(self, obj):
        if not obj.extracted_text:
            return "No text extracted"

        return format_html(
            '<pre style="white-space: pre-wrap; overflow-wrap: anywhere;">{}</pre>',
            obj.extracted_text,
        )