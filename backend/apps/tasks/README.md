# tasks — Task Management, ML Recommendation Engine & Portfolio Service

The `tasks` app is the core of the platform. It manages task lifecycle (creation → assignment → completion → evaluation), runs the hybrid AI recommendation engine, provides analytics for all three user roles, and auto-generates student portfolio items.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Task Lifecycle](#task-lifecycle)
4. [ML Recommendation Engine](#ml-recommendation-engine)
5. [Student Clustering](#student-clustering)
6. [Domain Predictor (RandomForest)](#domain-predictor-randomforest)
7. [Collaborative Filtering](#collaborative-filtering)
8. [Portfolio Service](#portfolio-service)
9. [Analytics Services](#analytics-services)
10. [Completion Service](#completion-service)
11. [Recommendation Service](#recommendation-service)
12. [Serializers](#serializers)
13. [Management Commands](#management-commands)

---

## Models

### `Task`
A simulated freelancing project task.

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | |
| `description` | TextField | Full task brief |
| `domain` | CharField | One of 10 supported domains |
| `difficulty` | CharField | beginner / intermediate / advanced |
| `estimated_duration` | IntegerField | Minutes (not hours) |
| `skills_required` | JSONField | List of skill strings |
| `learning_outcomes` | JSONField | List of outcome strings |
| `prerequisites` | JSONField | List of prerequisite skill strings |
| `created_by` | ForeignKey → User | Mentor or Admin who created |
| `is_active` | BooleanField | Inactive tasks hidden from recommendations |
| `created_at` | DateTimeField | |

---

### `TaskAssignment`
Links a student to a task they are working on. Created when student accepts a recommended task.

| Field | Type | Notes |
|-------|------|-------|
| `student` | ForeignKey → User | |
| `task` | ForeignKey → Task | |
| `status` | CharField | `accepted` / `in_progress` / `submitted` / `completed` |
| `progress_percentage` | IntegerField | 0–100 |
| `mentor_review_status` | CharField | `pending` / `reviewed` |
| `mentor_feedback` | TextField | Text feedback from mentor (legacy field) |
| `assigned_at` | DateTimeField | |
| `started_at` | DateTimeField (nullable) | |
| `submitted_at` | DateTimeField (nullable) | |
| `completed_at` | DateTimeField (nullable) | |

---

### `TaskCompletion`
Created when a student submits a task for review.

| Field | Type | Notes |
|-------|------|-------|
| `assignment` | OneToOneField → TaskAssignment | `related_name='completion'` |
| `student` | ForeignKey → User | |
| `task` | ForeignKey → Task | |
| `reflective_text` | TextField | Student's written reflection / work notes |
| `submission_notes` | TextField | Optional submission notes |
| `submitted_at` | DateTimeField | |

---

### `TaskMCQAttempt`
Per-task MCQ quiz answered after task submission.

| Field | Type | Notes |
|-------|------|-------|
| `completion` | ForeignKey → TaskCompletion | |
| `student` | ForeignKey → User | |
| `task` | ForeignKey → Task | |
| `answers` | JSONField | `{question_id: chosen_option}` |
| `score` | FloatField | 0–100 |
| `detailed_results` | JSONField | Per-question breakdown |
| `attempted_at` | DateTimeField | |

---

### `TaskMCQQuestion`
MCQ questions attached to a specific task (different from assessment questions).

| Field | Type | Notes |
|-------|------|-------|
| `task` | ForeignKey → Task | `related_name='mcq_questions'` |
| `question_text` | TextField | |
| `option_a` – `option_d` | CharField | |
| `correct_answer` | CharField | `a`/`b`/`c`/`d` |
| `concept` | CharField | |
| `difficulty_weight` | FloatField | |

---

### `TaskEvaluation`
The complete evaluation record for a task assignment.

| Field | Type | Notes |
|-------|------|-------|
| `assignment` | OneToOneField → TaskAssignment | |
| `student` | ForeignKey → User | |
| `task` | ForeignKey → Task | |
| `mcq_score` | FloatField | Score from TaskMCQAttempt |
| `reflective_text` | TextField | Copied from TaskCompletion |
| `mentor_score` | FloatField (nullable) | 0–100, set by mentor |
| `mentor_feedback` | TextField | |
| `final_score` | FloatField (nullable) | `(mcq_score + mentor_score) / 2` |
| `strengths` | JSONField | List of strings |
| `weaknesses` | JSONField | List of strings |
| `suggestions` | JSONField | List of strings |
| `status` | CharField | `pending` / `evaluated` |
| `evaluated_by` | ForeignKey → User (nullable) | Mentor who evaluated; `related_name='task_evaluations_given'` |
| `evaluated_at` | DateTimeField (nullable) | |

---

## URL Reference

All URLs prefixed with `/api/tasks/`.

### Student — Recommended & My Tasks

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `recommended/` | Student | Get top-10 ML-recommended tasks |
| GET | `my-tasks/` | Student | All of student's task assignments |
| POST | `accept/:id/` | Student | Accept a recommended task |
| PUT | `assignments/:id/update/` | Student | Update progress % or status |

### Task Completion Workflow

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| POST | `assignments/:id/complete/` | Student | Submit completion + reflective text |
| GET | `completions/:id/mcq/` | Student | Get MCQ questions for completed task |
| POST | `completions/:id/submit-mcq/` | Student | Submit MCQ answers → score |
| GET | `evaluations/:id/` | Student | Get evaluation result |

### Mentor — Task Management

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `mentor/` | Mentor | All tasks (created by all mentors) |
| POST | `mentor/create/` | Mentor | Create new task |
| PUT | `mentor/:id/update/` | Mentor | Update task |
| DELETE | `mentor/:id/delete/` | Mentor | Delete task |
| GET | `mentor/:id/mcq/` | Mentor | Get MCQ questions for a task |
| POST | `mentor/:id/mcq/add/` | Mentor | Add MCQ question to task |
| DELETE | `mentor/mcq/:id/delete/` | Mentor | Delete an MCQ question |
| POST | `evaluations/:id/evaluate/` | Mentor | Submit mentor evaluation (score + feedback) |

### Admin — Task Management

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `admin/` | Admin | List all tasks |
| PUT | `admin/:id/toggle-active/` | Admin | Toggle task active/inactive |

### Analytics

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `analytics/student/` | Student | Personal analytics dashboard data |
| GET | `analytics/mentor/` | Mentor | Mentor analytics dashboard data |
| GET | `analytics/admin/` | Admin | System-wide analytics data |
| GET | `analytics/domain-prediction/` | Student | ML domain prediction for student |

### Portfolio

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `portfolios/me/` | Student | Own portfolio with items |
| GET | `portfolios/:id/` | Any | View a student's portfolio |
| GET | `portfolios/:id/stats/` | Any | Portfolio statistics |

---

## Task Lifecycle

```
Task created (by mentor/admin)
        ↓
Student views recommended tasks (GET /tasks/recommended/)
        ↓
Student accepts (POST /tasks/accept/:id/)
   → TaskAssignment created (status: accepted)
        ↓
Student updates progress (PUT /tasks/assignments/:id/update/)
   → status → in_progress
        ↓
Student submits task (POST /tasks/assignments/:id/complete/)
   → TaskCompletion created with reflective_text
   → assignment.status → submitted
        ↓
Student takes MCQ quiz (POST /tasks/completions/:id/submit-mcq/)
   → TaskMCQAttempt scored
   → TaskEvaluation created (status: pending, mcq_score set)
   → assignment.mentor_review_status → pending
        ↓
Mentor sees in pending reviews (GET /api/auth/mentor/pending-reviews/)
        ↓
Mentor evaluates (POST /tasks/evaluations/:id/evaluate/)
   → TaskEvaluation updated:
         mentor_score, final_score = avg(mcq, mentor),
         strengths/weaknesses/suggestions
         status → evaluated
         evaluated_by → mentor
   → assignment.mentor_review_status → reviewed
   → PortfolioItem auto-created/updated via PortfolioService
        ↓
Student views result (GET /tasks/evaluations/:id/)
Student views portfolio (GET /tasks/portfolios/me/)
```

---

## ML Recommendation Engine

`apps/tasks/ml_engine.py`

### Content-Based Recommender

- Builds a **30-dimensional feature vector** for each task:
  - 10 dimensions: domain one-hot encoding
  - 10 dimensions: required skills (TF-IDF style)
  - 10 dimensions: learning outcomes keywords
- Builds a matching **student vector** from `StudentProfile.skill_scores_by_domain` + accepted task history
- Scores tasks via **cosine similarity** between student vector and task vector
- Returns similarity score in [0, 1]

### Collaborative Filter (KNN)

- Builds a **Student × Task matrix** from `TaskMCQAttempt` scores
- Uses `sklearn.neighbors.NearestNeighbors` (K=5, cosine metric) to find similar students
- Predicts score for unseen tasks based on neighbour ratings
- Fallback: returns 0 when insufficient data (< 5 students or new student)

### Hybrid Scoring

```python
final_score = 0.6 * content_score + 0.4 * collaborative_score
```

Tasks already accepted by the student are excluded. The top-10 by `final_score` are returned.

---

## Student Clustering

`apps/tasks/ml_engine.py` — `StudentClusterer`

- **Algorithm**: KMeans (4 clusters) from `sklearn.cluster`
- **Input**: 10-dim domain score vector (one score per domain, from `StudentProfile.skill_scores_by_domain`)
- **Cluster Labels** (assigned by centroid distance and sorted by mean score):

  | Cluster | Label |
  |---------|-------|
  | Lowest centroid | Explorer |
  | 2nd | Developing |
  | 3rd | Competent |
  | Highest centroid | Expert |

- **Trigger**: Called by assessment app after each `AssessmentAttempt`
- **Persistence**: Cluster parameters are derived from all student data in the DB at each call — no model file saved for clustering

---

## Domain Predictor (RandomForest)

`apps/tasks/domain_predictor.py`

A `RandomForestClassifier` that predicts the **most suitable domain** for a student.

### Feature Vector (13 dimensions)

| Index | Feature |
|-------|---------|
| 0–9 | MCQ score per domain (latest assessment attempt per domain) |
| 10 | Task completion rate (0–1) |
| 11 | Improvement trend (normalized slope of last 5 scores) |
| 12 | Average task MCQ score across all completed tasks |

### Training

```bash
python manage.py train_domain_model          # Uses real data + synthetic seed
python manage.py train_domain_model --no-seed # Real data only
python manage.py train_domain_model --info    # Show saved model metadata
```

### Storage

Saved to `backend/ml_models/domain_predictor.pkl` + `domain_predictor_meta.json`.

### Inference

`GET /api/tasks/analytics/domain-prediction/` calls `DomainPredictor.predict(student)` and returns predicted domain + confidence score.

---

## Collaborative Filtering

`apps/tasks/collaborative_filtering.py`

Standalone module providing user-based KNN collaborative filtering:
- Constructs the student × task score matrix from `TaskMCQAttempt` records
- Fills missing scores with 0 (implicit negative signal)
- Uses `sklearn.neighbors.NearestNeighbors` with cosine distance
- Returns estimated scores for tasks the target student has not yet attempted

---

## Portfolio Service

`apps/tasks/portfolio_service.py` — `PortfolioService`

Called automatically by `MentorEvaluateTaskView` after each successful evaluation.

```python
PortfolioService.create_portfolio_item(task_evaluation)
```

### What it does

1. Looks up the `Portfolio` for the student — creates one if it doesn't exist
2. `update_or_create` a `PortfolioItem` keyed on `task_evaluation`:
   - `task_title`, `task_domain`, `task_description`
   - `skills_demonstrated` (from task)
   - `mcq_score`, `mentor_score`, `final_score`
   - `mentor_feedback`, `strengths`, `suggestions`
   - `completion_date`
3. Recalculates portfolio aggregate stats:
   - `total_items`
   - `average_score`
   - `highest_score`
   - `domains_covered` (set of distinct domains)

`update_or_create` prevents the `portfolio_items_task_evaluation_id_key` unique constraint violation on re-evaluation.

---

## Analytics Services

`apps/tasks/analytics.py`

Three service classes — one per role.

### `StudentAnalyticsService`

`GET /api/tasks/analytics/student/`

Returns:
- Domain scores breakdown with bar chart data
- Cluster info + cluster distribution among all students
- Task completion history (last 10) with scores
- Score trend over time
- Skills heatmap
- Assessment attempt history

### `MentorAnalyticsService`

`GET /api/tasks/analytics/mentor/`

Returns:
- List of assigned students with cluster labels, avg score, completion rate
- Cluster distribution of mentored students
- Domain distribution data
- AI insights (top-performing domain, students needing attention)
- Attention list (students with avg score < 50 or 0 completed tasks)

### `AdminAnalyticsService`

`GET /api/tasks/analytics/admin/`

Returns:
- System-wide stats (total students/mentors/tasks/assessments)
- Task completion rates by domain
- Mentor workload (evaluations per mentor)
- Assessment performance by domain
- Cluster distribution across all students
- Active user counts
- Recent activity feed

`apps/tasks/analytics_views.py` — View classes that call the above services.

---

## Completion Service

`apps/tasks/completion_service.py` — `TaskCompletionService`

Handles the multi-step completion process:
1. Validates the assignment belongs to the student and status is `in_progress`
2. Creates `TaskCompletion` record
3. Updates `TaskAssignment.status → submitted`
4. Returns the completion ID for the MCQ step

---

## Recommendation Service

`apps/tasks/recommendation_service.py` — `TaskRecommendationService`

High-level orchestrator:
1. Loads student's profile and score vectors
2. Calls `ContentBasedRecommender.score_tasks(student, active_tasks)`
3. Calls `CollaborativeFilter.predict_scores(student_id, task_ids)`
4. Merges scores: `0.6×content + 0.4×collaborative`
5. Filters out tasks already accepted
6. Returns top-10 sorted tasks with `recommendation_score` and `match_reason`

---

## Serializers

| Serializer | Purpose |
|-----------|---------|
| `TaskSerializer` | Task CRUD |
| `TaskAssignmentSerializer` | Assignment detail |
| `TaskCompletionSerializer` | Completion + reflective text |
| `TaskMCQQuestionSerializer` | MCQ questions (correct answer hidden for students) |
| `TaskMCQAttemptSerializer` | MCQ submission + results |
| `TaskEvaluationSerializer` | Evaluation result (all fields) |
| `RecommendedTaskSerializer` | Task + recommendation_score + match_reason |

---

## Management Commands

```bash
# Train the domain prediction RandomForest model
python manage.py train_domain_model

# No synthetic training data
python manage.py train_domain_model --no-seed

# Show saved model info
python manage.py train_domain_model --info
```
