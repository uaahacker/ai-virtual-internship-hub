# Backend — Django REST API

Full Django 4.2 + Django REST Framework backend for the **AI-Supported Virtual Internship Hub**.  
All business logic, ML algorithms, NLP evaluation, and data persistence live here.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [App Summary](#app-summary)
3. [Project Configuration](#project-configuration)
4. [URL Routing](#url-routing)
5. [Authentication & Permissions](#authentication--permissions)
6. [App Deep-Dives](#app-deep-dives)
7. [ML Algorithms](#ml-algorithms)
8. [NLP Pipeline](#nlp-pipeline)
9. [Plagiarism / Originality Detection](#plagiarism--originality-detection)
10. [Datasets](#datasets)
11. [ML Model Storage](#ml-model-storage)
12. [Database & Migrations](#database--migrations)
13. [Management Commands](#management-commands)
14. [Response Format Convention](#response-format-convention)
15. [Setup & Running](#setup--running)
16. [Docker / Production](#docker--production)

---

## Architecture Overview

```
backend/
├── config/             ← Django settings, URL root, WSGI/ASGI
├── apps/
│   ├── accounts/       ← Auth, JWT, Google OAuth, user profiles, mentor assignment
│   ├── assessments/    ← Domain skill assessments, MCQ engine, adaptive testing, NLP feedback
│   ├── tasks/          ← Task CRUD, ML recommendation, evaluation, portfolio service, analytics
│   ├── chatbot/        ← AI chat sessions (OpenRouter LLM backend)
│   ├── notifications/  ← In-app notifications, broadcast announcements, direct messages
│   ├── portfolios/     ← Portfolio model (items auto-created by tasks app)
│   ├── submissions/    ← Text submissions, NLP evaluation, plagiarism detection
│   └── core/           ← Shared permissions, custom exception handler
├── ml_models/          ← Serialized .pkl / .json models (git-ignored)
├── datasets/           ← Training CSVs
├── manage.py
└── requirements.txt
```

Django speaks to a **PostgreSQL 16** database.  
In production, the server runs inside Docker behind **Nginx** (reverse proxy + SSL termination).

---

## App Summary

| App | URL Prefix | Key Responsibility |
|-----|-----------|-------------------|
| `accounts` | `/api/auth/` | Registration, JWT login/refresh/logout, Google OAuth, email verification, password reset, student & mentor profiles, admin user management, mentor-student assignment |
| `assessments` | `/api/assessments/` | 10-domain MCQ assessments, multi-dimensional evaluation engine, adaptive Q-Learning ordering, NLP feedback generation, attempt history |
| `tasks` | `/api/tasks/` | Task CRUD, hybrid ML recommendation (Content-Based + Collaborative), task assignment lifecycle, per-task MCQ, mentor evaluation, auto portfolio generation, analytics |
| `chatbot` | `/api/chatbot/` | Chat sessions, message history, AI career guidance (OpenRouter LLM) |
| `notifications` | `/api/notifications/` | In-app notifications, broadcast announcements, 1-to-1 direct messages |
| `portfolios` | `/api/portfolios/` | Portfolio and PortfolioItem models; items created/updated automatically by tasks app |
| `submissions` | `/api/submissions/` | Student text submissions, NLP auto-evaluation, mentor evaluation of written work |
| `core` | — | `IsStudent`, `IsMentor`, `IsAdmin` permission classes; custom DRF exception handler |

---

## Project Configuration

`config/settings.py` key settings:

| Setting | Value |
|---------|-------|
| `AUTH_USER_MODEL` | `accounts.User` |
| `DEFAULT_AUTHENTICATION_CLASSES` | `JWTAuthentication` |
| `ACCESS_TOKEN_LIFETIME` | 60 minutes |
| `REFRESH_TOKEN_LIFETIME` | 7 days |
| `ROTATE_REFRESH_TOKENS` | True |
| `BLACKLIST_AFTER_ROTATION` | True |
| `MEDIA_URL` | `/media/` |
| `MEDIA_ROOT` | `BASE_DIR / "media"` |
| `CORS_ALLOWED_ORIGINS` | Configurable via `.env` |

Database and secret configuration is driven by `.env` variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

---

## URL Routing

`config/urls.py`:

```
/api/auth/           → apps.accounts.urls
/api/assessments/    → apps.assessments.urls
/api/tasks/          → apps.tasks.urls
/api/chatbot/        → apps.chatbot.urls
/api/notifications/  → apps.notifications.urls
/api/submissions/    → apps.submissions.urls
/api/portfolios/     → apps.portfolios.urls
/api/token/          → JWT obtain pair (login alias)
/api/token/refresh/  → JWT refresh
/media/<path>        → served by Nginx in production; Django dev server in development
```

---

## Authentication & Permissions

### JWT Flow
1. `POST /api/auth/login/` → returns `{ access, refresh }`
2. All protected endpoints: `Authorization: Bearer <access_token>`
3. `POST /api/token/refresh/` → new access token (refresh token rotated automatically)
4. `POST /api/auth/logout/` → blacklists the refresh token

### Google OAuth Flow
1. Frontend renders Google Sign-In button (via `@react-oauth/google`)
2. Google returns an ID token (credential)
3. Frontend sends: `POST /api/auth/google/` with `{ token: "<google_id_token>" }`
4. Backend verifies via `google.oauth2.id_token.verify_oauth2_token()` with the `GOOGLE_CLIENT_ID`
5. User created (if new, `onboarding_complete=False`) or fetched (if existing)
6. JWT access+refresh pair returned — new users are redirected to `GoogleOnboardingPage` for role selection

### Email Verification
- `POST /api/auth/register/` creates the user + a `VerificationToken` (UUID, 24 h expiry, type=`email_verify`)
- Token is returned in the API response (no SMTP needed in development)
- `POST /api/auth/verify-email/` with `{ token }` activates the account (`is_email_verified=True`)

### Password Reset
- `POST /api/auth/forgot-password/` `{ email }` → creates `VerificationToken` (type=`password_reset`)
- Token returned in response (or sent by email when SMTP is configured)
- `POST /api/auth/reset-password/` `{ token, new_password }` → validates token, sets new password, marks token used

### Custom Permission Classes (`core/permissions.py`)

| Class | Condition |
|-------|-----------|
| `IsStudent` | `request.user.role == 'student'` |
| `IsMentor` | `request.user.role == 'mentor'` |
| `IsAdmin` | `request.user.role == 'admin'` or `is_staff` |

Composable with DRF's `IsAuthenticated`:
```python
permission_classes = [IsAuthenticated, IsStudent]
```

---

## App Deep-Dives

### `accounts` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `User` | `email`, `first_name`, `last_name`, `role` (student/mentor/admin), `profile_picture`, `onboarding_complete`, `is_email_verified` |
| `StudentProfile` | `user`, `bio`, `skills`, `strongest_domain`, `skill_scores` (JSON), `cluster_id`, `cluster_label`, `cluster_summary`, `assigned_mentor` |
| `MentorProfile` | `user`, `bio`, `expertise_domains`, `specialization`, `availability_status`, `is_auto_assignable` |
| `VerificationToken` | `user`, `token` (UUID4), `token_type` (email_verify / password_reset), `expires_at`, `is_used` |

**Key Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/auth/register/` | None | Register student or mentor |
| POST | `/auth/login/` | None | JWT login |
| POST | `/auth/logout/` | JWT | Blacklist refresh token |
| GET | `/auth/me/` | JWT | Current user info |
| PUT | `/auth/profile/update/` | JWT | Update profile + profile picture upload |
| POST | `/auth/google/` | None | Google OAuth sign-in/sign-up |
| POST | `/auth/verify-email/` | None | Activate account via UUID token |
| POST | `/auth/forgot-password/` | None | Request password reset token |
| POST | `/auth/reset-password/` | None | Set new password via token |
| GET | `/auth/admin/users/` | Admin | List all users with filtering |
| GET | `/auth/admin/stats/` | Admin | Platform-wide statistics |
| POST | `/auth/mentor/auto-assign/` | Admin | Auto-assign mentors to unassigned students |
| GET | `/auth/mentor/students/` | Mentor | List assigned students |

**Profile Picture Upload:**
- Endpoint: `PUT /auth/profile/update/` with `Content-Type: multipart/form-data`
- Flow:
  1. `UpdateProfileSerializer.save()` writes uploaded file to disk
  2. Pillow opens file → converts to RGB → `thumbnail((400, 400), LANCZOS)` → re-saves as JPEG quality=85
  3. Stored at `media/profile_pictures/profile_<user_id>.jpg`
  4. Fresh DB read via `User.objects.get(pk=user_id)` avoids `SimpleLazyObject` staleness
  5. Response always contains `profile_picture_url` (absolute URL via `request.build_absolute_uri()`)
- Nginx serves `/media/` from the shared `media_files` Docker named volume (7-day cache)

---

### `assessments` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `Assessment` | `domain`, `title`, `description`, `difficulty`, `time_limit` |
| `Question` | `assessment`, `text`, `options` (JSON array), `correct_answer`, `concept`, `difficulty_weight`, `order` |
| `AssessmentAttempt` | `student`, `assessment`, `answers` (JSON), `score`, `readiness_level`, `concept_scores`, `skill_profile_vector`, `improvement_delta`, `feedback`, `recommended_task_type`, `adaptive_order_used` |

**Key Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/assessments/` | Student | List all available assessments |
| GET | `/assessments/:id/` | Student | Assessment detail |
| GET | `/assessments/:id/questions/` | Student | Get questions (adaptively ordered by Q-Learning) |
| POST | `/assessments/:id/submit/` | Student | Submit answers → evaluation result |
| GET | `/assessments/my-attempts/` | Student | All past attempts with scores |
| GET | `/assessments/domain-stats/` | Student | Performance breakdown per domain |
| POST | `/assessments/` | Admin/Mentor | Create new assessment |

**10 Supported Domains:**
Graphic Design · Web Development · Digital Marketing · Content Writing · Video Editing · Data Analysis · UI/UX Design · SEO & Analytics · Social Media Management · WordPress

---

### `tasks` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `Task` | `title`, `description`, `domain`, `difficulty`, `skills_required` (JSON), `estimated_duration`, `max_students`, `created_by`, `is_active` |
| `TaskAssignment` | `student`, `task`, `status` (recommended / accepted / in_progress / completed / dropped), `progress_percentage`, `recommendation_score`, `recommendation_explanation` (JSON), `assigned_at` |
| `TaskCompletion` | `assignment`, `reflective_text`, `submitted_at` |
| `TaskMCQ` | `task`, `question`, `options` (JSON), `correct_answer`, `marks` |
| `TaskMCQAttempt` | `completion`, `answers` (JSON), `score`, `total_marks`, `percentage`, `passed` |
| `TaskEvaluation` | `assignment`, `mentor`, `mentor_score`, `mcq_score`, `final_score`, `feedback`, `strengths` (JSON), `suggestions` (JSON), `status` (pending / approved / needs_revision), `evaluated_at` |

**Key Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/tasks/` | Mentor/Admin | List all tasks |
| POST | `/tasks/` | Mentor/Admin | Create task |
| GET | `/tasks/recommended/` | Student | ML-recommended tasks ranked by AI score |
| GET | `/tasks/my-tasks/` | Student | Student's task assignments |
| POST | `/tasks/:id/accept/` | Student | Accept a recommended task |
| PUT | `/tasks/assignments/:id/update/` | Student | Update progress % |
| POST | `/tasks/assignments/:id/complete/` | Student | Submit reflective text |
| POST | `/tasks/completions/:id/submit-mcq/` | Student | Submit per-task MCQ |
| POST | `/tasks/evaluations/:id/evaluate/` | Mentor | Score + feedback + approve/revise |
| GET | `/tasks/analytics/student/` | Student | Personal analytics (domain breakdown, cluster) |
| GET | `/tasks/analytics/mentor/` | Mentor | Assigned students' analytics |
| GET | `/tasks/analytics/admin/` | Admin | Platform-wide analytics |
| GET | `/tasks/analytics/cluster-overview/` | Admin | KMeans cluster distribution |
| POST | `/tasks/analytics/domain-prediction/` | Student | RF-predicted best next domain |

---

### `chatbot` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `ChatSession` | `user`, `session_type` (student / mentor), `created_at`, `last_activity` |
| `ChatMessage` | `session`, `role` (user / assistant), `content`, `timestamp` |

**Provider chain (`providers.py`):**  
OpenRouter (Mistral/Llama) → OpenAI → Gemini → rule-based fallback

System prompts are role-aware:
- Students: freelancing career guidance, skill-building, task recommendations
- Mentors: mentoring strategies, evaluation tips, student progress context

**Key Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/chatbot/sessions/` | JWT | List sessions |
| POST | `/chatbot/sessions/` | JWT | Create session |
| GET | `/chatbot/sessions/:id/messages/` | JWT | Message history |
| POST | `/chatbot/sessions/:id/messages/` | JWT | Send message → AI reply |

---

### `notifications` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `Notification` | `user`, `title`, `message`, `notification_type`, `is_read`, `created_at` |
| `Announcement` | `created_by`, `title`, `message`, `target_role`, `created_at` |
| `DirectMessage` | `sender`, `recipient`, `message`, `is_read`, `sent_at` |

**Key Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/notifications/` | JWT | All notifications for current user |
| POST | `/notifications/:id/read/` | JWT | Mark one notification as read |
| POST | `/notifications/read-all/` | JWT | Mark all as read |
| GET | `/notifications/announcements/` | JWT | Broadcast announcements |
| POST | `/notifications/announcements/` | Admin | Create announcement |
| GET | `/notifications/messages/` | JWT | Direct message inbox |
| POST | `/notifications/messages/` | JWT | Send direct message |

---

### `portfolios` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `Portfolio` | `student`, `total_tasks`, `avg_score`, `domains` (JSON), `skills` (JSON), `last_updated` |
| `PortfolioItem` | `portfolio`, `task_title`, `domain`, `skills`, `final_score`, `mentor_feedback`, `completed_at` |

Items are created/updated automatically by `tasks/portfolio_service.py` when a `TaskEvaluation` is approved. No manual CRUD by students.

---

### `submissions` App

**Models:**

| Model | Key Fields |
|-------|-----------|
| `Submission` | `student`, `assignment`, `content`, `submitted_at` |
| `AIEvaluation` | `submission`, `readability_score`, `grammar_score`, `vocabulary_score`, `originality_score`, `length_score`, `final_score`, `readiness_label`, `strengths` (JSON), `improvement_tips` (JSON), `grammar_issues` (JSON) |
| `MentorEvaluation` | `submission`, `mentor`, `score`, `feedback`, `submitted_at` |

See [Plagiarism / Originality Detection](#plagiarism--originality-detection) for full detail.

---

### `core` App

- `permissions.py` — `IsStudent`, `IsMentor`, `IsAdmin` role-check permission classes
- `exceptions.py` — Custom DRF exception handler wrapping all errors in the standard response envelope

---

## ML Algorithms

### 1. Assessment Evaluation Engine
`apps/assessments/evaluation_engine.py`

Multi-dimensional MCQ evaluation — **no external APIs**.

- **Input**: Student answers + question metadata (concept, difficulty_weight)
- **Output per attempt**:
  - `domain_score` (0–100)
  - `concept_scores` — dict mapping concept → score
  - `readiness_level` — Novice / Developing / Competent / Proficient / Expert
  - `skill_profile_vector` (0.0–1.0 per concept)
  - `improvement_delta` vs previous attempt
  - `recommended_task_type` (Design / Development / Content / etc.)
  - NLP-generated personalized feedback text

### 2. NLP Feedback Generator
`apps/assessments/nlp_feedback.py`

- NLTK WordNet synonym variation for natural-sounding sentences
- Template sentences mapped to skill tier × score range
- Graceful fallback to static templates when NLTK is unavailable

### 3. Hybrid Task Recommendation
`apps/tasks/ml_engine.py` + `apps/tasks/recommendation_service.py`

```
final_score = 0.6 × content_score + 0.4 × collaborative_score
```

**Content-Based (60%):**
- 30-dimensional feature vectors per student and per task:
  - `[0:10]` Domain MCQ scores (concept mastery boost applied)
  - `[10:20]` Skill-level encodings
  - `[20:30]` Preferred-domain one-hots (boosted by log-scaled completion history)
- Cosine similarity between student profile vector and each task feature vector

**Collaborative Filtering (40%):**
- User-based KNN (K=7, minimum 1 shared task)
- Student × Task interaction matrix, cell value = interaction score:
  - Status: recommended=10, accepted=30, in_progress=50, completed=65
  - MCQ blend (×0.35 weight)
  - Mentor review adjustment: +10 (approved) / −8 (needs_revision)
- Student similarity = 55% interaction-cosine + 45% domain-profile-cosine
- Fallback: domain-match heuristic when < 3 students have interactions

**Output per assignment (stored in `recommendation_explanation` JSON):**
```json
{
  "match_reason": "Strong match in Web Development",
  "domain": "Web Development",
  "content_score": 0.91,
  "collaborative_score": 0.79,
  "explanation": [
    "Top performers in your domain completed this task",
    "Matches your skill profile"
  ]
}
```

### 4. Student Clustering (KMeans)
`apps/tasks/ml_engine.py` — `StudentClusterer`

- **K=4 clusters** on 10-dim domain performance vector (one MCQ score per domain)
- Cluster labels: **Explorer** (0) → **Developing** (1) → **Competent** (2) → **Expert** (3)
- Re-trained in-memory on every analytics request (not persisted to disk) using live DB data
- Results stored per student in `StudentProfile.cluster_id`, `.cluster_label`, `.cluster_summary` (JSON: display name + description)
- Displayed as a progress badge on student analytics, mentor dashboards, and admin cluster overview

### 5. Domain Predictor (RandomForest)
`apps/tasks/domain_predictor.py`

- **13-feature input**: `[0:10]` latest MCQ score per domain · `[10]` completion_rate · `[11]` improvement_trend (normalized slope) · `[12]` avg_task_mcq_score
- **Training data**: real student DB records + `datasets/student_performance.csv` (500 rows) + synthetic seed
- **Accuracy: 95.58%** on 905 total samples (trained 2026-05-04)
- **Serialized** to `ml_models/domain_predictor.pkl` via `joblib`
- **Fallback**: recency-decayed softmax heuristic (decay=0.85) when model file is unavailable
- Accessible via `POST /tasks/analytics/domain-prediction/`

### 6. Adaptive Testing — Q-Learning (Reinforcement Learning)
`apps/assessments/adaptive_testing.py`

Questions within each domain assessment are served in an adaptively ordered sequence.

| Component | Detail |
|-----------|--------|
| **Algorithm** | Tabular Q-Learning — Bellman update: `Q(s,a) += α·[r + γ·max(Q(s',·)) − Q(s,a)]` |
| **State space** | 4 states: Unknown · Struggling (acc<40%) · On-track (40–70%) · Excelling (>70%) |
| **Action space** | 3 actions: Easy (weight<0.85) · Medium (0.85–1.15) · Hard (weight>1.15) |
| **Rewards** | +1.0 correct Hard / +0.7 correct Medium / +0.3 correct Easy / −0.5 wrong Hard / −0.2 wrong Medium |
| **Q-table** | Persisted at `ml_models/adaptive_qtable.json`, updated after every attempt |
| **Starting state** | Derived from student's 5 most recent attempt percentages |
| **Fallback** | Default `order` field sequence when Q-table is unavailable |

### 7. MCQ Task Evaluation Engine
`apps/tasks/completion_service.py`

Separate from the assessment engine — evaluates per-task MCQs after task completion:
- Compares submitted answers against `TaskMCQ.correct_answer`
- Calculates `score`, `total_marks`, `percentage`, `passed` (threshold: 50%)
- `mcq_score` stored in `TaskEvaluation` and blended into final score:
  ```
  final_score = avg(mcq_score, mentor_score)
  ```

---

## NLP Pipeline

All NLP runs **locally** — no external APIs required.

### Assessment NLP (`apps/assessments/`)

| Component | File | What it does |
|-----------|------|-------------|
| Evaluation Engine | `evaluation_engine.py` | Scores domain MCQ, computes concept vectors, generates `recommended_task_type` |
| Feedback Generator | `nlp_feedback.py` | NLTK WordNet synonym-varied sentences per skill tier |
| Adaptive Testing | `adaptive_testing.py` | Q-Learning question ordering |
| Domain Stats | `domain_stats.py` | Per-domain performance aggregation across all attempts |

### Submission NLP (`apps/submissions/`)

| Component | Method | Detail |
|-----------|--------|--------|
| Readability | Flesch Reading Ease | `206.835 − 1.015×(words/sentences) − 84.6×(syllables/words)` |
| Vocabulary Diversity | Type-Token Ratio | `unique_words / total_words × 100` |
| Grammar Check | Regex patterns | Repeated words, missing spaces after punctuation, lowercase sentence starts, consecutive punctuation marks |
| Originality / Plagiarism | TF-IDF + Cosine Similarity | See below |

---

## Plagiarism / Originality Detection

`apps/submissions/evaluation_service.py`

This is the platform's built-in **plagiarism detection** mechanism, implemented as TF-IDF originality scoring.

### Algorithm

1. New submission text is vectorized with `sklearn.TfidfVectorizer` (English stop-words removed, L2-normalized)
2. Cosine similarity computed against **every previous submission** in the database
3. `max_similarity` = highest similarity score found
4. `originality_score = round((1 − max_similarity) × 100, 2)`

### Interpretation

| Originality Score | Interpretation |
|-------------------|---------------|
| 80–100 | Highly original — unique content |
| 60–79 | Mostly original — minor overlap |
| 40–59 | Moderate similarity — review recommended |
| 20–39 | High similarity — likely copied |
| 0–19 | Near-identical content — **plagiarism detected** |

### Weight in Composite AI Score

```
final_score = 0.25×readability + 0.25×grammar + 0.20×originality + 0.20×vocabulary + 0.10×length
```

Final score → readiness label:

| Score | Label |
|-------|-------|
| < 40 | Needs Work |
| 40–59 | Satisfactory |
| 60–79 | Good |
| ≥ 80 | Excellent |

All per-component scores and the `originality_score` are stored in `AIEvaluation` and visible to the student on the results page (`TextSubmissionPage`).

---

## Datasets

All files in `backend/datasets/`.

### `student_performance.csv` — 500 rows
Modelled on **Upwork Skills Index 2024** and **Freelancer.com Annual Market Report 2024**.

| Column | Description |
|--------|-------------|
| `Graphic Design` … `WordPress` | MCQ score per domain (0–100) |
| `completion_rate` | Task completion rate (0–1) |
| `improvement_trend` | Score slope across attempts (normalized, −1 to +1) |
| `avg_mcq_score` | Mean score across all domains |
| `recommended_domain` | Ground-truth label (highest market demand for that profile) |

### `freelancer_skills.csv` — 74 rows
Curated from **Kaggle "Freelancer Job Postings 2024"** and Upwork category taxonomy.

| Column | Description |
|--------|-------------|
| `job_title` | Freelancing job title |
| `primary_domain` | VIHub domain match |
| `skill_1` … `skill_4` | Required skills |
| `avg_hourly_rate_usd` | Market hourly rate (USD) |
| `demand_score` | Relative demand (0–100) |

Used by `dataset_loader.get_domain_skill_weights()` to enrich task-skill relevance scoring.

### `text_quality_samples.csv` — 50 rows
Annotated writing samples validated against **Grammarly Blog readability benchmarks**.

| Column | Description |
|--------|-------------|
| `text_excerpt` | Writing sample |
| `approx_flesch_score` | Flesch Reading Ease (0–100) |
| `grammar_issues` | Count of grammar issues |
| `vocabulary_diversity_pct` | TTR × 100 |
| `quality_label` | Needs Work / Satisfactory / Good / Excellent |

Used to validate `evaluation_service.py` thresholds.

---

## ML Model Storage

```
backend/ml_models/
├── domain_predictor.pkl     ← RandomForest (joblib), accuracy 95.58%, trained 2026-05-04
└── adaptive_qtable.json     ← Q-table for adaptive testing (4 states × 3 actions), updated live
```

`ml_models/` is in `.gitignore` — regenerate on deploy:

```bash
python manage.py train_domain_model   # creates domain_predictor.pkl
# adaptive_qtable.json is created automatically on first assessment submission
```

---

## Database & Migrations

PostgreSQL is the only supported database.

```bash
# Apply all migrations
python manage.py migrate

# Make migrations after model changes
python manage.py makemigrations <app_name>
```

The custom `accounts.User` model replaces Django's default auth — `AUTH_USER_MODEL` must be set before the first `migrate`.

---

## Management Commands

| Command | App | Description |
|---------|-----|-------------|
| `create_admin` | accounts | Creates the default admin user (interactive) |
| `reset_admin` | accounts | Resets admin password (interactive) |
| `seed_assessments` | assessments | Populates 10 domains × 10 questions each |
| `train_domain_model` | tasks | Trains & saves the RandomForest domain predictor |
| `train_domain_model --no-seed` | tasks | Same, using only real student data (no synthetic) |
| `train_domain_model --info` | tasks | Shows saved model metadata (accuracy, feature count, date) |

---

## Response Format Convention

Every endpoint follows this envelope:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Validation failed",
    "details": { "field": ["This field is required."] }
  }
}
```

Enforced globally via `core/exceptions.py` (custom DRF exception handler).

---

## Setup & Running

```bash
# 1. Create virtualenv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data (one-time)
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt')"

# 4. Create backend/.env  (see root README for full template)

# 5. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE virtual_internship_hub;"

# 6. Apply migrations
python manage.py migrate

# 7. Seed data + train ML model
python manage.py create_admin
python manage.py seed_assessments
python manage.py train_domain_model

# 8. Start dev server
python manage.py runserver
```

API available at **http://localhost:8000/api/**

---

## Docker / Production

See root `README.md → Production Deployment` for full Docker Compose setup.

Backend-specific details:
- Container: `vihub_backend` running gunicorn on port 8000
- Media files: Docker named volume `media_files` at `/app/media` (rw), shared read-only with `vihub_nginx`
- `entrypoint.sh` sequence:
  1. `python manage.py migrate`
  2. `python manage.py collectstatic --noinput`
  3. `mkdir -p /app/media/profile_pictures && chmod -R 755 /app/media`
  4. `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

```bash
# Full production deploy command
VITE_GOOGLE_CLIENT_ID=<your_client_id> docker compose up -d --build
```
