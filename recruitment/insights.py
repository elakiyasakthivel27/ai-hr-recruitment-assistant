
import re

from .matching import calculate_match, SKILL_KEYWORDS, find_skill_matches


QUESTION_BANK = {
    "python": "Explain a Python project you developed and how you handled errors.",
    "django": "How would you design a Django application with models, views and URLs?",
    "sql": "How would you optimize a slow SQL query and verify its correctness?",
    "rest api": "Explain how you would build, validate and test a REST API.",
    "git": "Describe how you use Git branches and resolve merge conflicts.",
    "javascript": "How do you handle asynchronous operations in JavaScript?",
    "java": "Explain object-oriented programming concepts using Java.",
    "machine learning": "How would you train and evaluate a machine learning model?",
    "deep learning": "How do you detect and reduce overfitting in neural networks?",
    "tensorflow": "How would you train and evaluate a model using TensorFlow?",
    "pandas": "How would you clean missing and duplicate data using Pandas?",
    "excel": "How would you analyze a large dataset using Excel?",
    "data analysis": "Explain your approach to exploring and validating a dataset.",
    "aws": "How would you deploy and monitor an application on AWS?",
    "html": "How do you create accessible and semantic HTML pages?",
    "css": "How would you build a responsive layout using CSS?",
    "nlp": "How would you preprocess text for an NLP application?",
    "scikit-learn": "How would you prevent data leakage in a scikit-learn pipeline?",
    "communication": "Describe how you would explain a technical issue to a nontechnical stakeholder.",
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def readable_skills(skills):
    return ", ".join(skill.upper() if skill in {"sql", "nlp", "aws", "html", "css"} else skill.title() for skill in skills)


def build_candidate_insights(candidate):
    resume_text = candidate.extracted_text or ""
    job = candidate.job
    job_title = job.title if job else "the selected role"
    job_description = job.description if job else ""

    result = calculate_match(resume_text, job_description)

    matched = result["matched_skills"]
    missing = result["missing_skills"]
    required = result["required_skills"]
    score = result["score"]

    detected = find_skill_matches(
        resume_text.lower(),
        list(SKILL_KEYWORDS.keys())
    )

    if not clean_text(resume_text):
        summary = (
            "Resume text is unavailable. Candidate-specific "
            "analysis cannot be completed."
        )
    elif required:
        summary = (
            f"The resume was evaluated for {job_title}. "
            f"{len(matched)} of {len(required)} supported JD skills "
            f"were detected in the resume."
        )

        if matched:
            summary += f" Matched skills include {readable_skills(matched[:6])}."

        if missing:
            summary += (
                f" The following requirements were not identified: "
                f"{readable_skills(missing[:6])}."
            )

        if detected:
            additional = [
                skill for skill in detected
                if skill not in required
            ][:4]

            if additional:
                summary += (
                    f" Other detected resume skills include "
                    f"{readable_skills(additional)}."
                )
    else:
        summary = (
            f"The resume was processed for {job_title}, but no "
            "supported technical skills were detected in the JD. "
            "The skill match cannot be assessed reliably."
        )

    questions = []

    for skill in matched:
        question = QUESTION_BANK.get(skill)
        if question and question not in questions:
            questions.append(question)
        if len(questions) >= 2:
            break

    for skill in missing:
        questions.append(
            f"The resume does not clearly mention {skill}. "
            f"Can you explain your familiarity with this requirement?"
        )
        if len(questions) >= 3:
            break

    fallback = [
        f"Describe a project relevant to {job_title} and your specific contribution.",
        "What technical challenge did you encounter and how did you resolve it?",
        "How would you test and improve the reliability of your solution?",
    ]

    for question in fallback:
        if len(questions) >= 3:
            break
        if question not in questions:
            questions.append(question)

    if not required:
        assessment = (
            "Insufficient recognized JD requirements to calculate "
            "a meaningful skill coverage score."
        )
    elif score >= 80:
        assessment = (
            "High detected skill coverage. Review project depth, "
            "hands-on proficiency and experience during interview."
        )
    elif score >= 50:
        assessment = (
            "Partial skill coverage. Verify missing requirements "
            "and practical technical proficiency."
        )
    else:
        assessment = (
            "Limited detected skill coverage. Review the resume "
            "manually and assess transferable skills."
        )

    return {
        "summary": summary,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skills": required,
        "score": score,
        "questions": questions,
        "assessment": assessment,
        "score_explanation": (
            f"{len(matched)} of {len(required)} recognized JD skills found."
            if required else
            "No supported JD skills detected."
        ),
    }
