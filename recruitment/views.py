
from io import BytesIO

import pymupdf
import pytesseract
from PIL import Image

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Job, Candidate
from .matching import calculate_match
from .insights import build_candidate_insights


# --------------------------------------------------
# Tesseract OCR Configuration
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# --------------------------------------------------
# Private HR Querysets
# --------------------------------------------------

def hr_jobs(request):
    return Job.objects.filter(owner=request.user)


def hr_candidates(request):
    return Candidate.objects.filter(owner=request.user)


# --------------------------------------------------
# Extract Text from Uploaded PDF
# --------------------------------------------------

def extract_resume_text(resume):
    extracted_text = ""

    try:
        resume.seek(0)
        pdf_bytes = resume.read()

        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as pdf:

            for page in pdf:
                page_text = page.get_text().strip()

                # OCR fallback for scanned PDF pages
                if not page_text:
                    try:
                        pix = page.get_pixmap(
                            matrix=pymupdf.Matrix(2, 2),
                            alpha=False
                        )

                        image = Image.open(
                            BytesIO(pix.tobytes("png"))
                        )

                        page_text = pytesseract.image_to_string(
                            image
                        ).strip()

                    except Exception as ocr_error:
                        print("OCR error:", ocr_error)

                extracted_text += page_text + "\n"

        print("Extracted characters:", len(extracted_text))

    except Exception as error:
        print("Resume extraction error:", error)

    finally:
        resume.seek(0)

    return extracted_text.strip()


# --------------------------------------------------
# Create Resume Summary
# --------------------------------------------------

def make_resume_summary(text, max_words=60):
    if not text:
        return "No resume text available."

    words = text.split()
    summary = " ".join(words[:max_words])

    if len(words) > max_words:
        summary += "..."

    return summary


# --------------------------------------------------
# Recruitment Dashboard
# --------------------------------------------------

@login_required
def dashboard(request):

    candidates = hr_candidates(request).select_related(
        "job"
    ).order_by("-match_score", "-uploaded_at")

    search_query = request.GET.get("q", "").strip()
    selected_job = request.GET.get("job", "").strip()
    min_score = request.GET.get("min_score", "").strip()

    # Search candidates
    if search_query:
        candidates = candidates.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(job__title__icontains=search_query)
        )

    # Filter by job
    if selected_job:
        if selected_job.isdigit():
            candidates = candidates.filter(
                job_id=int(selected_job)
            )
        else:
            selected_job = ""

    # Filter by match score
    if min_score:
        try:
            score_value = float(min_score)

            if 0 <= score_value <= 100:
                candidates = candidates.filter(
                    match_score__gte=score_value
                )
            else:
                min_score = ""

        except ValueError:
            min_score = ""

    # Candidate insights and skill gap analysis
    candidates = list(candidates)
    candidate_insights = {}

    for candidate in candidates:
        insights = build_candidate_insights(candidate)

        candidate_insights[str(candidate.pk)] = insights

        candidate.display_matched_skills = insights.get(
            "matched_skills", []
        )

        candidate.display_missing_skills = insights.get(
            "missing_skills", []
        )

    # Statistics limited to logged-in HR
    owned_candidates = hr_candidates(request)
    owned_jobs = hr_jobs(request)

    average_score = owned_candidates.aggregate(
        avg=Avg("match_score")
    )["avg"] or 0

    high_matches = owned_candidates.filter(
        match_score__gte=70
    ).count()

    context = {
        "candidates": candidates,
        "jobs": owned_jobs.order_by("title"),
        "total_candidates": owned_candidates.count(),
        "total_jobs": owned_jobs.count(),
        "average_score": average_score,
        "high_matches": high_matches,
        "search_query": search_query,
        "selected_job": selected_job,
        "min_score": min_score,
        "candidate_insights": candidate_insights,
    }

    return render(
        request,
        "recruitment/dashboard.html",
        context
    )


# --------------------------------------------------
# Upload Resume
# --------------------------------------------------

@login_required
def upload_resume(request):

    jobs = hr_jobs(request).order_by("title")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        job_id = request.POST.get("job", "").strip()
        resume = request.FILES.get("resume")

        if not name or not email or not job_id or not resume:
            messages.error(
                request,
                "Please fill in all fields and select a resume."
            )

            return render(
                request,
                "recruitment/upload_resume.html",
                {"jobs": jobs}
            )

        if not resume.name.lower().endswith(".pdf"):
            messages.error(
                request,
                "Please upload a PDF resume."
            )

            return render(
                request,
                "recruitment/upload_resume.html",
                {"jobs": jobs}
            )

        if resume.size > 5 * 1024 * 1024:
            messages.error(
                request,
                "Resume file must be smaller than 5 MB."
            )

            return render(
                request,
                "recruitment/upload_resume.html",
                {"jobs": jobs}
            )

        try:
            job = jobs.get(pk=int(job_id))

        except (Job.DoesNotExist, ValueError):
            messages.error(
                request,
                "Please select a valid job opening."
            )

            return render(
                request,
                "recruitment/upload_resume.html",
                {"jobs": jobs}
            )

        extracted_text = extract_resume_text(resume)

        if not extracted_text:
            messages.error(
                request,
                "Could not extract text from this PDF. "
                "Please try a text-based PDF resume."
            )

            return render(
                request,
                "recruitment/upload_resume.html",
                {"jobs": jobs}
            )

        result = calculate_match(
            extracted_text,
            job.description
        )

        Candidate.objects.create(
            owner=request.user,
            job=job,
            name=name,
            email=email,
            resume=resume,
            extracted_text=extracted_text,
            match_score=result["score"],
            matched_skills=", ".join(
                result["matched_skills"]
            ),
            missing_skills=", ".join(
                result["missing_skills"]
            ),
        )

        messages.success(
            request,
            "Resume uploaded and evaluated successfully!"
        )

        return redirect("dashboard")

    return render(
        request,
        "recruitment/upload_resume.html",
        {"jobs": jobs}
    )


# --------------------------------------------------
# Secure Resume PDF Viewer
# --------------------------------------------------

@login_required
def candidate_resume(request, candidate_id):

    candidate = get_object_or_404(
        hr_candidates(request),
        pk=candidate_id
    )

    if not candidate.resume:
        raise Http404("Resume not found.")

    try:
        candidate.resume.open("rb")

        return FileResponse(
            candidate.resume,
            content_type="application/pdf",
            as_attachment=False,
            filename=f"candidate_{candidate.pk}_resume.pdf",
        )

    except (FileNotFoundError, OSError, ValueError):
        raise Http404("Resume file not available.")


# --------------------------------------------------
# Compare Candidates
# --------------------------------------------------

@login_required
def compare_candidates(request):

    all_candidates = hr_candidates(request).select_related(
        "job"
    ).order_by("name")

    candidate1 = None
    candidate2 = None
    summary1 = ""
    summary2 = ""
    recommendation = ""

    id1 = request.GET.get("candidate1", "").strip()
    id2 = request.GET.get("candidate2", "").strip()

    if id1 and id2:
        try:
            candidate1 = all_candidates.get(pk=int(id1))
            candidate2 = all_candidates.get(pk=int(id2))

            if candidate1.pk == candidate2.pk:
                messages.error(
                    request,
                    "Please select two different candidates."
                )

                candidate1 = None
                candidate2 = None

            else:
                summary1 = make_resume_summary(
                    candidate1.extracted_text
                )

                summary2 = make_resume_summary(
                    candidate2.extracted_text
                )

                if candidate1.match_score > candidate2.match_score:
                    recommendation = (
                        f"{candidate1.name} has the higher calculated "
                        f"skill match ({candidate1.match_score:.0f}% "
                        f"compared with {candidate2.match_score:.0f}%). "
                        "Review both resumes before making a decision."
                    )

                elif candidate2.match_score > candidate1.match_score:
                    recommendation = (
                        f"{candidate2.name} has the higher calculated "
                        f"skill match ({candidate2.match_score:.0f}% "
                        f"compared with {candidate1.match_score:.0f}%). "
                        "Review both resumes before making a decision."
                    )

                else:
                    recommendation = (
                        "Both candidates have the same calculated "
                        "skill match score. Review their skills and "
                        "experience before making a decision."
                    )

        except (Candidate.DoesNotExist, ValueError):
            messages.error(
                request,
                "One or both selected candidates could not be found."
            )

    context = {
        "all_candidates": all_candidates,
        "candidate1": candidate1,
        "candidate2": candidate2,
        "summary1": summary1,
        "summary2": summary2,
        "recommendation": recommendation,
    }

    return render(
        request,
        "recruitment/compare_candidates.html",
        context
    )


# --------------------------------------------------
# Admin Dashboard
# --------------------------------------------------

@staff_member_required
def admin_dashboard(request):

    context = {
        "total_candidates": Candidate.objects.count(),
        "total_jobs": Job.objects.count(),
        "average_score": (
            Candidate.objects.aggregate(
                avg=Avg("match_score")
            )["avg"] or 0
        ),
    }

    return render(
        request,
        "recruitment/admin_dashboard.html",
        context
    )


# --------------------------------------------------
# Home Page
# --------------------------------------------------

def home(request):
    return render(
        request,
        "recruitment/home.html"
    )


# --------------------------------------------------
# Manage Jobs
# --------------------------------------------------

@login_required
def manage_jobs(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get(
            "description", ""
        ).strip()

        if not title or not description:
            messages.error(
                request,
                "Please enter both job title and description."
            )

        else:
            Job.objects.create(
                owner=request.user,
                title=title,
                description=description
            )

            messages.success(
                request,
                "Job opening created successfully!"
            )

            return redirect("manage_jobs")

    jobs = hr_jobs(request).order_by("-created_at")

    return render(
        request,
        "recruitment/manage_jobs.html",
        {"jobs": jobs}
    )


# --------------------------------------------------
# Edit Job
# --------------------------------------------------

@login_required
def edit_job(request, job_id):

    job = get_object_or_404(
        hr_jobs(request),
        pk=job_id
    )

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get(
            "description", ""
        ).strip()

        if not title or not description:
            messages.error(
                request,
                "Please enter both job title and description."
            )

        else:
            job.title = title
            job.description = description
            job.save()

            messages.success(
                request,
                "Job opening updated successfully!"
            )

            return redirect("manage_jobs")

    return render(
        request,
        "recruitment/edit_job.html",
        {"job": job}
    )


# --------------------------------------------------
# Delete Job
# --------------------------------------------------

@login_required
@require_POST
def delete_job(request, job_id):

    job = get_object_or_404(
        hr_jobs(request),
        pk=job_id
    )

    job.delete()

    messages.success(
        request,
        "Job opening deleted successfully!"
    )

    return redirect("manage_jobs")


# --------------------------------------------------
# Candidate Management
# --------------------------------------------------

@login_required
def candidate_list(request):

    candidates = hr_candidates(request).select_related(
        "job"
    ).order_by("-uploaded_at")

    search_query = request.GET.get("q", "").strip()
    selected_job = request.GET.get("job", "").strip()
    min_score = request.GET.get("min_score", "").strip()

    if search_query:
        candidates = candidates.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(job__title__icontains=search_query)
        )

    if selected_job.isdigit():
        candidates = candidates.filter(
            job_id=int(selected_job)
        )
    else:
        selected_job = ""

    if min_score:
        try:
            score = float(min_score)

            if 0 <= score <= 100:
                candidates = candidates.filter(
                    match_score__gte=score
                )
            else:
                min_score = ""

        except ValueError:
            min_score = ""

    context = {
        "candidates": candidates,
        "jobs": hr_jobs(request).order_by("title"),
        "search_query": search_query,
        "selected_job": selected_job,
        "min_score": min_score,
        "total_candidates": hr_candidates(request).count(),
    }

    return render(
        request,
        "recruitment/candidate_list.html",
        context
    )
