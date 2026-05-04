"""
Portfolio Service - handles portfolio generation and management.

Functions:
- Auto-generate portfolio items when tasks are completed
- Create/update portfolio summaries using local NLP logic
- Calculate portfolio statistics and improvement trends
"""

from django.utils import timezone
from apps.portfolios.models import Portfolio, PortfolioItem

# ---------------------------------------------------------------------------
# Domain-specific vocabulary for local NLP summary generation
# ---------------------------------------------------------------------------

_DOMAIN_VOCAB = {
    "Graphic Design":    {"verb": "designed",   "action": "creating visual deliverables",               "skill_context": "applying visual design principles"},
    "Content Writing":   {"verb": "produced",   "action": "writing and editing content",                "skill_context": "applying writing and communication skills"},
    "Programming":       {"verb": "developed",  "action": "building functional software",               "skill_context": "implementing programming logic and best practices"},
    "Freelancing":       {"verb": "delivered",  "action": "completing a client-facing project",         "skill_context": "managing scope, communication, and delivery"},
    "E-Commerce":        {"verb": "executed",   "action": "setting up an e-commerce workflow",          "skill_context": "applying product listing and store management skills"},
    "QuickBooks":        {"verb": "applied",    "action": "managing accounting and bookkeeping tasks",  "skill_context": "using QuickBooks for financial record-keeping"},
    "AutoCAD":           {"verb": "drafted",    "action": "creating technical drawings and models",     "skill_context": "using CAD tools to produce precise technical outputs"},
    "Data Analytics":    {"verb": "analyzed",   "action": "extracting insights from data",             "skill_context": "applying data analysis and visualization techniques"},
    "Digital Marketing": {"verb": "planned",    "action": "executing a digital marketing campaign",    "skill_context": "applying SEO, content strategy, and audience targeting"},
    "WordPress":         {"verb": "built",      "action": "developing a WordPress-based web solution", "skill_context": "using themes, plugins, and page builders"},
}

_SCORE_TIER = [
    (90, "outstanding results",  "Distinction"),
    (80, "strong performance",   "A"),
    (70, "solid competence",     "B"),
    (60, "satisfactory work",    "C"),
    (0,  "foundational effort",  "D"),
]

_DIFFICULTY_LABEL = {"Easy": "introductory", "Medium": "intermediate", "Hard": "advanced"}


def _score_grade(score):
    """Return (tier_label, grade_letter) for a 0-100 score."""
    for threshold, label, grade in _SCORE_TIER:
        if score >= threshold:
            return label, grade
    return "foundational effort", "D"


def _extract_key_sentence(text):
    """Pull the first meaningful sentence (>=20 chars) from a text block."""
    if not text:
        return ""
    text = text.strip()
    for sep in (". ", "! ", "? "):
        idx = text.find(sep)
        if idx != -1 and idx >= 20:
            return text[: idx + 1].strip()
    return text[:200].rstrip(" ,;") + ("..." if len(text) > 200 else "")


# ---------------------------------------------------------------------------


class PortfolioService:
    """Service for managing portfolio generation and updates."""

    @staticmethod
    def get_or_create_portfolio(student):
        portfolio, _ = Portfolio.objects.get_or_create(
            user=student,
            defaults={"title": f"{student.name}'s Portfolio"},
        )
        return portfolio

    # -- Item-level NLP helpers -----------------------------------------------

    @staticmethod
    def generate_item_description(task, task_evaluation, completion):
        """
        Build a concise 1-2 sentence professional summary for a portfolio item.
        Uses task domain, type, difficulty, required skills (up to 3),
        score tier, and first learning outcome. Purely template-driven from
        real task metadata - no hallucinated content.
        """
        domain = task.domain
        difficulty_label = _DIFFICULTY_LABEL.get(task.difficulty, task.difficulty.lower())
        vocab = _DOMAIN_VOCAB.get(domain, {
            "verb": "completed", "action": "fulfilling project requirements",
            "skill_context": "applying relevant domain knowledge",
        })
        score = task_evaluation.final_score
        tier_label, _ = _score_grade(score)
        skills = (task.required_skills or [])[:3]
        skill_text = f", with skills in {', '.join(skills)}" if skills else ""
        outcomes = task.learning_outcomes or []
        outcome_text = f" Key learning: {outcomes[0].rstrip('.').strip()}." if outcomes else ""
        return (
            f"{vocab['verb'].capitalize()} an {difficulty_label}-level "
            f"{task.task_type} task in {domain}{skill_text}, "
            f"{vocab['action']}, achieving {tier_label}.{outcome_text}"
        )

    @staticmethod
    def generate_mentor_feedback_summary(mentor_feedback, strengths, weaknesses, suggestions):
        """
        Distil mentor feedback into a concise 1-sentence portfolio blurb.
        Priority: first meaningful sentence from mentor_feedback.
        Fallback: lead with top strength.
        """
        if mentor_feedback:
            sentence = _extract_key_sentence(mentor_feedback)
            if sentence:
                return sentence
        if strengths:
            return f"Mentor highlighted: {strengths[0]}."
        return ""

    @staticmethod
    def generate_strengths_summary(strengths):
        """Convert a strengths list to a bullet-point string (max 5)."""
        if not strengths:
            return ""
        return "\n".join(f"• {s}" for s in strengths[:5])

    # -- Portfolio-level overview ---------------------------------------------

    @staticmethod
    def generate_portfolio_overview(portfolio):
        """
        Build a structured overview dict from all portfolio items.

        Returns:
            {
              top_domains:       [{domain, count, avg_score}, ...],
              all_skills:        [{skill, count}, ...],   (top 10)
              improvement_trend: [{date, score, title, domain}, ...],
              strengths_list:    [str, ...],
              summary_sentence:  str,
              total_items:       int,
              average_score:     float,
            }
        """
        items = list(portfolio.items.order_by("completion_date"))

        if not items:
            student_name = getattr(portfolio.user, "name", portfolio.user.email)
            return {
                "top_domains": [], "all_skills": [], "improvement_trend": [],
                "strengths_list": [],
                "summary_sentence": f"{student_name} has not completed any tasks yet.",
                "total_items": 0, "average_score": 0.0,
            }

        domain_data = {}
        skill_counts = {}

        for item in items:
            d = item.task_domain or "Unknown"
            if d not in domain_data:
                domain_data[d] = {"count": 0, "total": 0.0}
            domain_data[d]["count"] += 1
            domain_data[d]["total"] += item.final_score
            for skill in (item.skills_demonstrated or []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        top_domains = sorted(
            [
                {"domain": d, "count": v["count"],
                 "avg_score": round(v["total"] / v["count"], 1)}
                for d, v in domain_data.items()
            ],
            key=lambda x: (-x["count"], -x["avg_score"]),
        )[:5]

        all_skills = [
            {"skill": s, "count": c}
            for s, c in sorted(skill_counts.items(), key=lambda x: -x[1])
        ][:10]

        improvement_trend = [
            {
                "date": item.completion_date.strftime("%Y-%m-%d") if item.completion_date else "",
                "score": round(item.final_score, 1),
                "title": item.task_title,
                "domain": item.task_domain,
            }
            for item in items
        ]

        seen = set()
        strengths_list = []
        for item in items:
            if item.strengths_summary:
                for line in item.strengths_summary.split("\n"):
                    clean = line.strip().lstrip("•").strip()
                    if clean and clean not in seen:
                        seen.add(clean)
                        strengths_list.append(clean)
                        if len(strengths_list) == 5:
                            break
            if len(strengths_list) == 5:
                break

        total = len(items)
        avg = round(sum(i.final_score for i in items) / total, 1)
        top_d = top_domains[0]["domain"] if top_domains else "multiple domains"
        num_domains = len(domain_data)
        summary_sentence = (
            f"Completed {total} task{'s' if total != 1 else ''} across "
            f"{num_domains} domain{'s' if num_domains != 1 else ''} "
            f"with an average score of {avg}%. "
            f"Strongest focus in {top_d}."
        )
        return {
            "top_domains": top_domains, "all_skills": all_skills,
            "improvement_trend": improvement_trend,
            "strengths_list": strengths_list,
            "summary_sentence": summary_sentence,
            "total_items": total, "average_score": avg,
        }

    # -- Core create / update -------------------------------------------------

    @staticmethod
    def create_portfolio_item(task_evaluation):
        """Create a PortfolioItem from a completed TaskEvaluation."""
        student = task_evaluation.task_completion.task_assignment.student
        task = task_evaluation.task_completion.task_assignment.task
        completion = task_evaluation.task_completion

        portfolio = PortfolioService.get_or_create_portfolio(student)

        project_summary = PortfolioService.generate_item_description(
            task, task_evaluation, completion
        )
        mentor_feedback_summary = PortfolioService.generate_mentor_feedback_summary(
            task_evaluation.mentor_feedback,
            task_evaluation.strengths,
            task_evaluation.weaknesses,
            task_evaluation.suggestions,
        )
        strengths_summary = PortfolioService.generate_strengths_summary(
            task_evaluation.strengths
        )
        skills_demonstrated = list(task.required_skills or [])

        portfolio_item, _ = PortfolioItem.objects.update_or_create(
            task_evaluation=task_evaluation,
            defaults=dict(
                portfolio=portfolio,
                task_title=task.title,
                task_domain=task.domain,
                task_difficulty=task.difficulty,
                task_type=task.task_type,
                completion_date=completion.completed_at,
                evaluation_date=task_evaluation.evaluated_at or timezone.now(),
                mcq_score=task_evaluation.mcq_score,
                mentor_score=task_evaluation.mentor_score,
                final_score=task_evaluation.final_score,
                skills_demonstrated=skills_demonstrated,
                student_reflection=completion.reflective_text,
                project_summary=project_summary,
                mentor_feedback_summary=mentor_feedback_summary,
                strengths_summary=strengths_summary,
                display_order=portfolio.total_items,
            ),
        )
        PortfolioService.update_portfolio_stats(portfolio)
        return portfolio_item

    @staticmethod
    def update_portfolio_stats(portfolio):
        """Recalculate and save portfolio aggregate stats."""
        items = list(portfolio.items.all())
        total = len(items)
        portfolio.total_items = total
        portfolio.average_score = (
            round(sum(i.final_score for i in items) / total, 2) if total > 0 else 0.0
        )
        portfolio.save()

    @staticmethod
    def get_portfolio_stats(portfolio):
        """Return comprehensive portfolio statistics including improvement trend."""
        items = list(portfolio.items.order_by("completion_date"))

        domain_counts = {}
        difficulty_counts = {}
        skill_counts = {}

        for item in items:
            domain_counts[item.task_domain] = domain_counts.get(item.task_domain, 0) + 1
            difficulty_counts[item.task_difficulty] = difficulty_counts.get(item.task_difficulty, 0) + 1
            for skill in (item.skills_demonstrated or []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        scores = [item.final_score for item in items]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0

        improvement_trend = [
            {
                "date": item.completion_date.strftime("%Y-%m-%d") if item.completion_date else "",
                "score": round(item.final_score, 1),
                "title": item.task_title,
                "domain": item.task_domain,
            }
            for item in items
        ]

        grade_dist = {"Distinction": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for item in items:
            _, grade = _score_grade(item.final_score)
            grade_dist[grade] = grade_dist.get(grade, 0) + 1

        return {
            "total_items": len(items),
            "average_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "by_domain": domain_counts,
            "by_difficulty": difficulty_counts,
            "top_skills": [
                {"skill": s, "count": c}
                for s, c in sorted(skill_counts.items(), key=lambda x: -x[1])[:10]
            ],
            "improvement_trend": improvement_trend,
            "grade_distribution": grade_dist,
        }

    @staticmethod
    def export_portfolio_as_json(portfolio):
        """Export portfolio data as JSON for sharing/archiving."""
        items = list(portfolio.items.order_by("completion_date"))
        return {
            "portfolio": {
                "title": portfolio.title,
                "student": getattr(portfolio.user, "name", portfolio.user.email),
                "bio": portfolio.bio,
                "created_at": portfolio.created_at.isoformat(),
                "total_items": portfolio.total_items,
                "average_score": portfolio.average_score,
            },
            "items": [
                {
                    "task_title": item.task_title,
                    "domain": item.task_domain,
                    "difficulty": item.task_difficulty,
                    "task_type": item.task_type,
                    "completion_date": item.completion_date.isoformat() if item.completion_date else "",
                    "mcq_score": item.mcq_score,
                    "mentor_score": item.mentor_score,
                    "final_score": item.final_score,
                    "grade": _score_grade(item.final_score)[1],
                    "project_summary": item.project_summary,
                    "skills": item.skills_demonstrated,
                    "mentor_feedback_summary": item.mentor_feedback_summary,
                    "strengths_summary": item.strengths_summary,
                }
                for item in items
            ],
            "statistics": PortfolioService.get_portfolio_stats(portfolio),
            "overview": PortfolioService.generate_portfolio_overview(portfolio),
        }
