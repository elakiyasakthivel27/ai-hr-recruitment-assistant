"""Vision Orbit skill-coverage matching (rule-based, not a hiring prediction).

Drop-in replacement for recruitment/matching.py. Public functions and return
keys remain compatible with recruitment/views.py and recruitment/insights.py.
"""
import re

SKILL_KEYWORDS = {
    "python": ["python", "python3", "python programming"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql"],
    "machine learning": ["machine learning", "machine-learning", "ml algorithms"],
    "deep learning": ["deep learning", "deep-learning", "neural networks"],
    "tensorflow": ["tensorflow", "tf keras"],
    "keras": ["keras", "tf.keras"],
    "django": ["django", "django framework"],
    "excel": ["excel", "microsoft excel", "ms excel"],
    "data analysis": ["data analysis", "data analytics", "data analyst"],
    "pandas": ["pandas", "python pandas"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "nlp": ["nlp", "natural language processing"],
    "communication": ["communication", "communication skills", "verbal communication"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "javascript": ["javascript", "java script", "js", "node.js", "nodejs"],
    "java": ["java", "java programming"],
    "c++": ["c++", "cpp"],
    "opencv": ["opencv", "open cv"],
    "computer vision": ["computer vision"],
    "streamlit": ["streamlit"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "data visualization": ["data visualization", "data visualisation"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "aws": ["aws", "amazon web services"],
    "git": ["git", "git version control"],
    "github": ["github"],
    "rest api": ["rest api", "rest apis", "restful api", "restful apis"],
    "machine learning model": ["machine learning model"],
}

# Negation is a conservative heuristic, not full language understanding.
_NEGATION_BEFORE = re.compile(
    r"(?:\bno\b|\bwithout\b|\black(?:ing|s)?\b|\bnever\b|"
    r"\bnot\s+(?:familiar|proficient|experienced|skilled|trained)\s+(?:in|with)\b|"
    r"\bno\s+(?:hands[- ]on\s+)?(?:experience|knowledge|skills?|exposure)\s+(?:in|with|of)\b)"
    r"(?:[\w\s-]{0,35})$",
    re.IGNORECASE,
)
_NEGATION_AFTER = re.compile(
    r"^\s*(?:[-:–]\s*)?(?:not\s+(?:known|used|learned)|"
    r"(?:experience|knowledge|skills?|proficiency)\s*:\s*(?:none|no|nil)\b)",
    re.IGNORECASE,
)


def _pattern(keyword):
    # Keep exact term boundaries: 'java' must not match 'javascript'.
    return re.compile(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", re.IGNORECASE)


def contains_keyword(text, keyword):
    """Backward-compatible exact-term check (no context filtering)."""
    return bool(_pattern(keyword).search(text or ""))


def _is_negated(text, match):
    # Limit context to the current line/sentence to avoid negating other skills.
    prefix = text[max(0, match.start() - 85):match.start()]
    prefix = re.split(r"[\n.!?;]", prefix)[-1]
    suffix = text[match.end():match.end() + 55]
    suffix = re.split(r"[\n.!?;]", suffix)[0]
    return bool(_NEGATION_BEFORE.search(prefix) or _NEGATION_AFTER.search(suffix))


def _has_positive_mention(text, skill):
    aliases = SKILL_KEYWORDS.get(skill, [skill])
    for alias in aliases:
        for match in _pattern(alias).finditer(text):
            if not _is_negated(text, match):
                return True
    return False


def find_skill_matches(text, skills_to_check):
    """Return unique recognized skills in the requested order.

    Negated mentions such as 'no Python experience' are excluded when
    no positive mention of that skill appears elsewhere in the text.
    """
    text = text or ""
    found = []
    seen = set()
    for skill in skills_to_check:
        if skill not in seen and _has_positive_mention(text, skill):
            found.append(skill)
            seen.add(skill)
    return found


def calculate_match(resume_text, job_description):
    """Compute recognized JD skill coverage, not candidate suitability.

    The score is the percentage of recognized JD skills with a positive
    mention in the resume. Unrecognized requirements are not assessed.
    """
    required = find_skill_matches(job_description, list(SKILL_KEYWORDS))
    if not required:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "required_skills": [],
            "message": "No supported skills were detected in the job description.",
        }

    matched = find_skill_matches(resume_text, required)
    matched_set = set(matched)
    missing = [skill for skill in required if skill not in matched_set]
    score = round(100 * len(matched) / len(required))
    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skills": required,
        "message": "Recognized JD skill coverage calculated successfully.",
    }
