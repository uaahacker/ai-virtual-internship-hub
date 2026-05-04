"""
Tests for portfolio summary generation logic in PortfolioService.
Run with: python manage.py test apps.portfolios.tests_summary
"""

from unittest.mock import MagicMock, PropertyMock
from django.test import SimpleTestCase as TestCase

from apps.tasks.portfolio_service import (
    PortfolioService,
    _score_grade,
    _extract_key_sentence,
    _DOMAIN_VOCAB,
)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_task(
    title="Test Task",
    domain="Programming",
    difficulty="Medium",
    task_type="Project",
    required_skills=None,
    learning_outcomes=None,
    estimated_duration=60,
):
    task = MagicMock()
    task.title = title
    task.domain = domain
    task.difficulty = difficulty
    task.task_type = task_type
    task.required_skills = required_skills or ["Python", "Django"]
    task.learning_outcomes = learning_outcomes or ["Build REST APIs"]
    task.estimated_duration = estimated_duration
    task.description = "A test task description."
    return task


def make_evaluation(
    final_score=75.0,
    mcq_score=70.0,
    mentor_score=80.0,
    mentor_feedback="",
    strengths=None,
    weaknesses=None,
    suggestions=None,
    evaluated_at=None,
):
    ev = MagicMock()
    ev.final_score = final_score
    ev.mcq_score = mcq_score
    ev.mentor_score = mentor_score
    ev.mentor_feedback = mentor_feedback
    ev.strengths = strengths or []
    ev.weaknesses = weaknesses or []
    ev.suggestions = suggestions or []
    ev.evaluated_at = evaluated_at
    return ev


def make_completion(reflective_text="I learned a lot.", completed_at=None):
    from django.utils import timezone
    c = MagicMock()
    c.reflective_text = reflective_text
    c.completed_at = completed_at or timezone.now()
    return c


def make_portfolio_item(
    task_domain="Programming",
    task_difficulty="Medium",
    task_title="Test Task",
    task_type="Project",
    final_score=75.0,
    skills_demonstrated=None,
    strengths_summary="",
    completion_date=None,
):
    from django.utils import timezone
    item = MagicMock()
    item.task_domain = task_domain
    item.task_difficulty = task_difficulty
    item.task_title = task_title
    item.task_type = task_type
    item.final_score = final_score
    item.skills_demonstrated = skills_demonstrated or ["Python"]
    item.strengths_summary = strengths_summary
    item.completion_date = completion_date or timezone.now()
    return item


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class ScoreGradeTests(TestCase):
    def test_distinction(self):
        label, grade = _score_grade(95)
        self.assertEqual(grade, "Distinction")

    def test_a_grade(self):
        _, grade = _score_grade(80)
        self.assertEqual(grade, "A")

    def test_b_grade(self):
        _, grade = _score_grade(70)
        self.assertEqual(grade, "B")

    def test_c_grade(self):
        _, grade = _score_grade(60)
        self.assertEqual(grade, "C")

    def test_d_grade(self):
        _, grade = _score_grade(55)
        self.assertEqual(grade, "D")

    def test_boundary_80(self):
        _, grade = _score_grade(80)
        self.assertEqual(grade, "A")

    def test_boundary_79(self):
        _, grade = _score_grade(79)
        self.assertEqual(grade, "B")


class ExtractKeySentenceTests(TestCase):
    def test_extracts_first_sentence(self):
        text = "The student demonstrated excellent skills. More detail follows."
        result = _extract_key_sentence(text)
        self.assertEqual(result, "The student demonstrated excellent skills.")

    def test_short_sentence_skipped(self):
        # "Hi. More context here with enough length to qualify as a sentence."
        text = "Hi. More context here with enough length."
        result = _extract_key_sentence(text)
        # "Hi." is only 2 chars before separator, should be skipped
        # Next full sentence boundary comes later
        self.assertIn("More context here", result)

    def test_empty_text(self):
        self.assertEqual(_extract_key_sentence(""), "")

    def test_truncation(self):
        long_text = "a" * 300
        result = _extract_key_sentence(long_text)
        self.assertTrue(result.endswith("..."))
        self.assertLessEqual(len(result), 203)

    def test_no_sentence_boundary(self):
        text = "A single line with no period"
        result = _extract_key_sentence(text)
        self.assertEqual(result, text)


class GenerateItemDescriptionTests(TestCase):
    def test_known_domain_uses_correct_verb(self):
        task = make_task(domain="Programming", difficulty="Medium", task_type="Project")
        ev = make_evaluation(final_score=82.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        self.assertIn("Developed", result)
        self.assertIn("intermediate-level", result)
        self.assertIn("Programming", result)
        self.assertIn("strong performance", result)

    def test_unknown_domain_fallback(self):
        task = make_task(domain="UnknownDomain", difficulty="Easy", task_type="Practice")
        ev = make_evaluation(final_score=65.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        self.assertIn("Completed", result)
        self.assertIn("introductory-level", result)

    def test_hard_difficulty_label(self):
        task = make_task(difficulty="Hard")
        ev = make_evaluation(final_score=75.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        self.assertIn("advanced-level", result)

    def test_skills_included(self):
        task = make_task(required_skills=["SQL", "Power BI", "Excel"])
        ev = make_evaluation(final_score=70.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        self.assertIn("SQL", result)
        self.assertIn("Power BI", result)

    def test_max_three_skills(self):
        task = make_task(required_skills=["A", "B", "C", "D", "E"])
        ev = make_evaluation(final_score=70.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        # Should not include the 4th and 5th skills
        self.assertNotIn(", D", result)
        self.assertNotIn(", E", result)

    def test_learning_outcome_appended(self):
        task = make_task(learning_outcomes=["Understand REST API design"])
        ev = make_evaluation(final_score=78.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        self.assertIn("Understand REST API design", result)

    def test_no_learning_outcome(self):
        task = make_task(learning_outcomes=[])
        ev = make_evaluation(final_score=78.0)
        comp = make_completion()
        result = PortfolioService.generate_item_description(task, ev, comp)
        # Should not crash
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_all_ten_domains_produce_output(self):
        domains = list(_DOMAIN_VOCAB.keys())
        for domain in domains:
            task = make_task(domain=domain)
            ev = make_evaluation(final_score=75.0)
            comp = make_completion()
            result = PortfolioService.generate_item_description(task, ev, comp)
            self.assertIn(domain, result, f"Domain '{domain}' not in output")
            self.assertGreater(len(result), 20)


class GenerateMentorFeedbackSummaryTests(TestCase):
    def test_extracts_first_sentence_from_feedback(self):
        feedback = "Great work on the project. Minor issues in documentation."
        result = PortfolioService.generate_mentor_feedback_summary(
            feedback, [], [], []
        )
        self.assertEqual(result, "Great work on the project.")

    def test_fallback_to_strength(self):
        result = PortfolioService.generate_mentor_feedback_summary(
            "", ["Excellent analytical thinking"], [], []
        )
        self.assertIn("Excellent analytical thinking", result)
        self.assertIn("Mentor highlighted", result)

    def test_empty_returns_empty(self):
        result = PortfolioService.generate_mentor_feedback_summary("", [], [], [])
        self.assertEqual(result, "")

    def test_long_feedback_truncated(self):
        long_feedback = "w" * 300
        result = PortfolioService.generate_mentor_feedback_summary(
            long_feedback, [], [], []
        )
        self.assertLessEqual(len(result), 203)


class GenerateStrengthsSummaryTests(TestCase):
    def test_formats_as_bullets(self):
        result = PortfolioService.generate_strengths_summary(
            ["Good communication", "Analytical thinking"]
        )
        self.assertIn("• Good communication", result)
        self.assertIn("• Analytical thinking", result)

    def test_max_five_items(self):
        strengths = [f"Strength {i}" for i in range(10)]
        result = PortfolioService.generate_strengths_summary(strengths)
        bullets = [line for line in result.split("\n") if line.strip()]
        self.assertEqual(len(bullets), 5)

    def test_empty_returns_empty(self):
        result = PortfolioService.generate_strengths_summary([])
        self.assertEqual(result, "")


class GeneratePortfolioOverviewTests(TestCase):
    def _make_portfolio(self, items):
        portfolio = MagicMock()
        portfolio.user.name = "Ali Hassan"
        # items.order_by returns the list directly
        portfolio.items.order_by.return_value = items
        return portfolio

    def test_empty_portfolio(self):
        portfolio = self._make_portfolio([])
        result = PortfolioService.generate_portfolio_overview(portfolio)
        self.assertEqual(result["total_items"], 0)
        self.assertEqual(result["average_score"], 0.0)
        self.assertIn("Ali Hassan", result["summary_sentence"])
        self.assertEqual(result["top_domains"], [])

    def test_single_item(self):
        item = make_portfolio_item(
            task_domain="Programming",
            final_score=80.0,
            skills_demonstrated=["Python", "Django"],
        )
        portfolio = self._make_portfolio([item])
        result = PortfolioService.generate_portfolio_overview(portfolio)
        self.assertEqual(result["total_items"], 1)
        self.assertEqual(result["average_score"], 80.0)
        self.assertEqual(result["top_domains"][0]["domain"], "Programming")
        skills = [s["skill"] for s in result["all_skills"]]
        self.assertIn("Python", skills)

    def test_multiple_domains(self):
        items = [
            make_portfolio_item(task_domain="Programming", final_score=85.0),
            make_portfolio_item(task_domain="Programming", final_score=75.0),
            make_portfolio_item(task_domain="Data Analytics", final_score=90.0),
        ]
        portfolio = self._make_portfolio(items)
        result = PortfolioService.generate_portfolio_overview(portfolio)
        # Programming (count=2) should rank above Data Analytics (count=1)
        self.assertEqual(result["top_domains"][0]["domain"], "Programming")
        self.assertEqual(len(result["improvement_trend"]), 3)

    def test_improvement_trend_order(self):
        from django.utils import timezone
        import datetime
        base = timezone.now()
        items = [
            make_portfolio_item(final_score=60.0,
                                completion_date=base - datetime.timedelta(days=10)),
            make_portfolio_item(final_score=75.0,
                                completion_date=base - datetime.timedelta(days=5)),
            make_portfolio_item(final_score=85.0, completion_date=base),
        ]
        portfolio = self._make_portfolio(items)
        result = PortfolioService.generate_portfolio_overview(portfolio)
        scores = [p["score"] for p in result["improvement_trend"]]
        self.assertEqual(scores, [60.0, 75.0, 85.0])

    def test_strengths_aggregated_from_items(self):
        item1 = make_portfolio_item(strengths_summary="• Problem solving\n• Communication")
        item2 = make_portfolio_item(strengths_summary="• Attention to detail")
        portfolio = self._make_portfolio([item1, item2])
        result = PortfolioService.generate_portfolio_overview(portfolio)
        self.assertIn("Problem solving", result["strengths_list"])
        self.assertIn("Attention to detail", result["strengths_list"])

    def test_top_10_skills_maximum(self):
        skills = [f"Skill{i}" for i in range(15)]
        item = make_portfolio_item(skills_demonstrated=skills)
        portfolio = self._make_portfolio([item])
        result = PortfolioService.generate_portfolio_overview(portfolio)
        self.assertLessEqual(len(result["all_skills"]), 10)

    def test_summary_sentence_correct_grammar(self):
        item = make_portfolio_item()
        portfolio = self._make_portfolio([item])
        result = PortfolioService.generate_portfolio_overview(portfolio)
        # Single task → "task" (not "tasks")
        self.assertIn("1 task ", result["summary_sentence"])
        self.assertNotIn("1 tasks", result["summary_sentence"])


class GetPortfolioStatsTests(TestCase):
    def _make_portfolio(self, items):
        portfolio = MagicMock()
        portfolio.items.order_by.return_value = items
        return portfolio

    def test_empty_portfolio(self):
        portfolio = self._make_portfolio([])
        stats = PortfolioService.get_portfolio_stats(portfolio)
        self.assertEqual(stats["total_items"], 0)
        self.assertEqual(stats["average_score"], 0)
        self.assertEqual(stats["improvement_trend"], [])

    def test_grade_distribution(self):
        items = [
            make_portfolio_item(final_score=92.0),  # Distinction
            make_portfolio_item(final_score=85.0),  # A
            make_portfolio_item(final_score=72.0),  # B
            make_portfolio_item(final_score=55.0),  # D
        ]
        portfolio = self._make_portfolio(items)
        stats = PortfolioService.get_portfolio_stats(portfolio)
        grade_dist = stats["grade_distribution"]
        self.assertEqual(grade_dist["Distinction"], 1)
        self.assertEqual(grade_dist["A"], 1)
        self.assertEqual(grade_dist["B"], 1)
        self.assertEqual(grade_dist["D"], 1)

    def test_top_skills_sorted_by_frequency(self):
        items = [
            make_portfolio_item(skills_demonstrated=["Python", "SQL", "Python"]),
            make_portfolio_item(skills_demonstrated=["Python", "Django"]),
        ]
        portfolio = self._make_portfolio(items)
        stats = PortfolioService.get_portfolio_stats(portfolio)
        # Python appears 3 times, should be first
        self.assertEqual(stats["top_skills"][0]["skill"], "Python")
