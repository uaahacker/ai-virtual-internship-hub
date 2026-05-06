# portfolios — Student Portfolio

The `portfolios` app stores auto-generated portfolio data for each student. Portfolio items are created and updated automatically by the tasks app's `PortfolioService` whenever a mentor completes an evaluation.

Students do not manually manage portfolio items — the system builds the portfolio from completed and evaluated tasks.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Auto-Generation Flow](#auto-generation-flow)
4. [Portfolio Stats](#portfolio-stats)

---

## Models

### `Portfolio`

One per student. Created automatically on first portfolio item save.

| Field | Type | Notes |
|-------|------|-------|
| `student` | OneToOneField → User | `related_name='portfolio'` |
| `total_items` | IntegerField | Count of evaluated portfolio items |
| `average_score` | FloatField | Mean of all `final_score` values |
| `highest_score` | FloatField | Best `final_score` in portfolio |
| `domains_covered` | JSONField | List of distinct domains in portfolio |
| `created_at` | DateTimeField | |
| `updated_at` | DateTimeField | Auto-updated |

---

### `PortfolioItem`

One item per evaluated task. Unique on `task_evaluation`.

| Field | Type | Notes |
|-------|------|-------|
| `portfolio` | ForeignKey → Portfolio | `related_name='items'` |
| `task_evaluation` | OneToOneField → TaskEvaluation | Unique constraint: `portfolio_items_task_evaluation_id_key` |
| `task_title` | CharField | Denormalized from task |
| `task_domain` | CharField | Denormalized from task |
| `task_description` | TextField | Denormalized from task |
| `skills_demonstrated` | JSONField | From task.skills_required |
| `mcq_score` | FloatField | From evaluation |
| `mentor_score` | FloatField | From evaluation |
| `final_score` | FloatField | `(mcq_score + mentor_score) / 2` |
| `mentor_feedback` | TextField | Mentor's text feedback |
| `strengths` | JSONField | Strengths identified by mentor |
| `suggestions` | JSONField | Mentor suggestions for improvement |
| `completion_date` | DateTimeField | When the task was evaluated |

---

## URL Reference

Portfolio has two access points:

**Via the tasks namespace** (`/api/tasks/`):

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/tasks/portfolios/me/` | Student | Own portfolio with all items |
| GET | `/tasks/portfolios/:id/` | Authenticated | View another student's portfolio |
| GET | `/tasks/portfolios/:id/stats/` | Authenticated | Portfolio statistics only |

**Via the portfolios namespace** (`/api/portfolios/`):

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/portfolios/me/` | Student | Own portfolio (same response, separate URL prefix) |
| GET | `/portfolios/:id/` | Authenticated | View another student's portfolio |

---

## Auto-Generation Flow

```
Mentor submits evaluation
    ↓
tasks/views.py → MentorEvaluateTaskView
    ↓
calls PortfolioService.create_portfolio_item(task_evaluation)
    ↓
PortfolioService:
  1. get_or_create Portfolio for student
  2. update_or_create PortfolioItem (keyed on task_evaluation)
       - Copies task title, domain, description, skills from Task
       - Copies scores and feedback from TaskEvaluation
  3. Recalculates Portfolio aggregates:
       - total_items = count of items
       - average_score = mean of final_scores
       - highest_score = max of final_scores
       - domains_covered = distinct list of item domains
    ↓
Student sees updated portfolio immediately
```

`update_or_create` is used (not `create`) to safely handle re-evaluations without hitting the `task_evaluation_id` unique constraint.

---

## Portfolio Stats

`GET /api/tasks/portfolios/:id/stats/` returns a lightweight summary:

```json
{
  "success": true,
  "data": {
    "total_items": 7,
    "average_score": 82.4,
    "highest_score": 97.5,
    "domains_covered": ["Web Development", "Data Analysis", "UI/UX Design"],
    "completion_rate": 0.78
  }
}
```

This is used on the public-facing portfolio page and mentor student detail view.
