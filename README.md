# AI-Supported Virtual Internship Hub

> **An AI-powered platform that gives students real-world freelancing experience through simulated projects, ML-driven task recommendations, automated evaluations, mentor guidance, and auto-generated portfolios.**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Features Implemented](#features-implemented)
5. [Project Structure](#project-structure)
6. [Getting Started](#getting-started)
7. [Backend — Django REST API](#backend--django-rest-api)
8. [Frontend — React/Vite SPA](#frontend--reactvite-spa)
9. [AI & ML Capabilities](#ai--ml-capabilities)
10. [Key Workflows](#key-workflows)
11. [API Overview](#api-overview)
12. [User Roles](#user-roles)
13. [Database Schema](#database-schema)
14. [Environment Variables](#environment-variables)
15. [Running Tests & Management Commands](#running-tests--management-commands)

---

## Project Overview

This platform addresses the gap between academic learning and real-world freelancing practice. Students register, take AI-evaluated skill assessments, receive ML-recommended tasks, complete them with reflective submissions and an MCQ quiz, then receive a combined mentor + AI evaluation. Each completed task automatically builds the student's portfolio — ready to showcase on platforms like Upwork or Fiverr.

**Functional Requirements Delivered**

| # | Requirement | Status |
|---|-------------|--------|
| FR1 | User registration & authentication (Student / Mentor / Admin) | ✅ Done |
| FR2 | AI-based skill assessment for domain recommendation | ✅ Done |
| FR3 | ML task/project allocation using hybrid recommendation | ✅ Done |
| FR4 | Automated text evaluation (NLP scoring: readability, grammar, originality) | ✅ Done |
| FR5 | Mentor dashboard — review progress, give scored feedback | ✅ Done |
| FR6 | Auto-generated portfolio from completed tasks + PDF export | ✅ Done |
| FR7 | AI-powered chatbot for career guidance (Student & Mentor) | ✅ Done |
| FR8 | Admin panel — manage users, assessments, tasks, analytics | ✅ Done |
| FR9 | Analytics dashboards — progress, skill trends, cluster insights | ✅ Done |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    React / Vite Frontend                │
│  (Tailwind CSS · React Router v6 · Axios · Toastify)   │
│                                                         │
│  Student ──▶ Assessment ──▶ Tasks ──▶ Submit Text       │
│          ──▶ Portfolio (PDF export) ──▶ Chatbot         │
│  Mentor  ──▶ Review ──▶ Evaluate ──▶ Analytics ──▶ Chat │
│  Admin   ──▶ Users ──▶ Assessments ──▶ Reports          │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP/REST  (JWT Auth)
┌──────────────────────▼──────────────────────────────────┐
│                Django REST Framework API                │
│                   (Python 3 · Django 4.2)               │
│                                                         │
│  /api/auth/          accounts app                       │
│  /api/assessments/   assessments app                    │
│  /api/tasks/         tasks app  ← ML Engine here        │
│  /api/chatbot/       chatbot app                        │
│  /api/notifications/ notifications app                  │
│  /api/portfolios/    portfolios app                     │
│  /api/submissions/   submissions app ← NLP Engine here  │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   PostgreSQL DB            ML Models (.pkl)
   (23+ tables)       domain_predictor.pkl
                      KMeans clustering
                      KNN collaborative filter
                      TF-IDF (submissions)
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, React Router v6 |
| **HTTP Client** | Axios 1.6 |
| **UI / UX** | React Icons, React Toastify, React Markdown |
| **Backend** | Django 4.2, Django REST Framework 3.14 |
| **Authentication** | JWT (djangorestframework-simplejwt) |
| **Database** | PostgreSQL |
| **ML / AI** | scikit-learn (KMeans, KNN, RandomForest), NumPy, Pandas |
| **NLP** | NLTK (WordNet, tokenizers) |
| **Dev Environment** | VS Code, Vite dev server, Django dev server |
| **Version Control** | Git / GitHub |

---

## Features Implemented

### Student Experience
- Register, take AI-graded domain skill assessments (10 domains)
- Receive 5-tier readiness score (Novice → Expert) with NLP feedback
- View ML-recommended tasks ranked by hybrid AI score
- Accept tasks, track progress, submit with reflective writing
- Submit written work → instant AI evaluation (readability, grammar, originality)
- Take per-task MCQ quiz — auto-scored
- View combined mentor + MCQ + NLP evaluation result
- Auto-generated portfolio with score, skills, and mentor feedback
- **Download portfolio as PDF** directly from the portfolio page
- AI chatbot for freelancing career guidance
- View personal analytics (domain breakdown, skill trends, cluster tier)
- Direct messaging with mentor

### Mentor Experience
- View assigned students with cluster labels and progress scores
- See pending task reviews with student reflection + MCQ score
- Submit scored evaluations (mentor score 0–100, feedback, strengths, suggestions)
- Final score = average(MCQ score, mentor score) → auto-updates portfolio
- View review history with final scores
- Analytics dashboard — cluster distribution, AI insights, domain breakdown
- Create / manage custom tasks with MCQ questions
- Select and assign/unassign students
- **AI assistant chat** (mentors can now use the chatbot)

### Admin Experience
- Live stats dashboard (user counts, task/assessment statistics)
- Manage all users (create, edit, delete, reset password)
- Manage assessments (create, add/remove questions, toggle active)
- Manage tasks (view all, toggle active/inactive)
- Analytics — system-wide: mentor workload, cluster overview, popular domains
- Announcements (broadcast to all, students, or mentors)
- Auto-assign mentors to students

---

## Project Structure

```
fyp/
├── README.md                       ← This file
├── backend/
│   ├── README.md                   ← Backend overview
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── accounts/               ← Auth, users, mentor/student profiles
│   │   │   └── README.md
│   │   ├── assessments/            ← Skill assessments, evaluation engine, NLP
│   │   │   └── README.md
│   │   ├── tasks/                  ← Tasks, assignments, ML recommendation, portfolio service
│   │   │   └── README.md
│   │   ├── chatbot/                ← AI career guidance chatbot
│   │   │   └── README.md
│   │   ├── notifications/          ← Notifications, announcements, direct messages
│   │   │   └── README.md
│   │   ├── portfolios/             ← Student portfolio models
│   │   │   └── README.md
│   │   ├── core/                   ← Shared permissions & exception handler
│   │   │   └── README.md
│   │   ├── portfolios/             ← Student portfolio models + stats API
│   │   └── README.md
│   └── submissions/            ← Text submission + NLP evaluation (FR4)
│   └── ml_models/
│       └── domain_predictor.pkl    ← Trained RandomForest model
└── frontend/
    ├── README.md                   ← Frontend overview
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── src/
    │   ├── App.jsx                 ← All routes (50+)
    │   ├── main.jsx
    │   ├── index.css
    │   ├── services/
    │   │   ├── api.js              ← Axios instance + JWT interceptor
    │   │   └── endpoints.js        ← All API service functions
    │   ├── contexts/
    │   │   ├── AuthContext.jsx
    │   │   ├── ChatContext.jsx
    │   │   └── NotificationContext.jsx
    │   ├── components/             ← 13 reusable components
    │   └── pages/                  ← 39 page components
    └── public/
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1 — Clone the Repository

```bash
git clone https://github.com/uaahacker/fyp.git
cd fyp
```

### 2 — Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Download NLTK data (one-time)
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt')"
```

Create a `.env` file in `backend/`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=virtual_internship_hub
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

```bash
# Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE virtual_internship_hub;"

# Run migrations
python manage.py migrate

# Create admin user
python manage.py create_admin

# (Optional) Seed assessment questions
python manage.py seed_assessments

# (Optional) Seed task data
python manage.py seed_tasks

# (Optional) Train ML domain prediction model
python manage.py train_domain_model

# Start server
python manage.py runserver
```

Backend runs at **http://localhost:8000**

### 3 — Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## Backend — Django REST API

Full details → [backend/README.md](backend/README.md)

The backend is a Django 4.2 REST API organized into 7 apps:

| App | URL Prefix | Purpose |
|-----|-----------|---------|
| `accounts` | `/api/auth/` | Authentication, user management, mentor/student profiles |
| `assessments` | `/api/assessments/` | Skill assessments with AI evaluation |
| `tasks` | `/api/tasks/` | Tasks, assignments, ML recommendations, portfolio |
| `chatbot` | `/api/chatbot/` | AI career chatbot sessions (Student + Mentor) |
| `notifications` | `/api/notifications/` | Notifications, announcements, messages |
| `portfolios` | `/api/portfolios/` | Portfolio CRUD, stats, PDF export support |
| `submissions` | `/api/submissions/` | Text submissions + NLP evaluation engine |
| `core` | *(shared)* | Permissions, exception handling |

**Auth**: JWT (60-min access tokens, 7-day refresh with rotation). All endpoints require `Authorization: Bearer <token>` except register and login.

**Response format** (all endpoints):
```json
{ "success": true, "data": { ... } }
{ "success": false, "error": { "code": 400, "message": "..." } }
```

---

## Frontend — React/Vite SPA

Full details → [frontend/README.md](frontend/README.md)

The frontend is a React 18 single-page application with Vite as the build tool and Tailwind CSS for styling.

**50+ routes** organized by role with `ProtectedRoute` guards.  
**Auth state** managed via `AuthContext` (JWT stored in localStorage, 5-sec timeout on initial load).  
**Notifications** polled every 30 seconds via `NotificationContext`.

---

## AI & ML Capabilities

### 1. Assessment Evaluation Engine
`backend/apps/assessments/evaluation_engine.py`

Multi-dimensional MCQ evaluation — no external APIs.

- **Input**: Student answers + question metadata (concept, difficulty_weight)
- **Output**:
  - `domain_score` (0–100)
  - `concept_scores` dict per concept
  - `readiness_level`: Novice / Developing / Competent / Proficient / Expert
  - `skill_profile_vector` (0–1 per concept)
  - `improvement_delta` vs previous attempt
  - `recommended_task_type` (Design / Development / Content / etc.)
  - NLP-generated personalized feedback

### 2. NLP Feedback Generator
`backend/apps/assessments/nlp_feedback.py`

- NLTK WordNet synonym variation for natural-sounding text
- Template sentences per skill tier + score range
- Graceful fallback when NLTK is unavailable

### 3. Hybrid Task Recommendation
`backend/apps/tasks/ml_engine.py` + `recommendation_service.py`

```
Final Score = 0.6 × content_score + 0.4 × collaborative_score
```

- **Content-Based (60%)**: 30-dim feature vectors; cosine similarity between student profile and task features
- **Collaborative Filtering (40%)**: User-based KNN (K=5) on student × task MCQ score matrix
- Fallback to domain-match heuristic when insufficient interaction data

### 4. Student Clustering (KMeans)
`backend/apps/tasks/ml_engine.py` — `StudentClusterer`

- 4 clusters: **Explorer → Developing → Competent → Expert**
- Input: 10-dim domain performance vector (one score per domain)
- Updated automatically after each assessment attempt
- Displayed with cluster badge on analytics + mentor dashboards

### 6. NLP Text Evaluation (FR4)
`backend/apps/submissions/evaluation_service.py`

Automated evaluation of student written submissions — no external APIs.

- **Readability** (25%): Flesch Reading Ease formula — measures sentence/word/syllable ratios. Higher = easier to read.
- **Vocabulary Diversity** (20%): Type-Token Ratio (TTR) — `unique_words / total_words × 100`. Rewards varied vocabulary.
- **Grammar** (25%): Regex-based issue detection — repeated words, missing spaces after punctuation, lowercase sentence starts, multiple punctuation marks. Deducts 5 pts per issue.
- **Originality** (20%): TF-IDF cosine similarity of the new submission vs all previous submissions. `originality = (1 − max_similarity) × 100`.
- **Length** (10%): Linear scale — 200+ words = full score.

**Final AI score** = weighted composite (0–100) mapped to a readiness label:

| Score | Label |
|-------|-------|
| < 40 | Needs Work |
| 40–59 | Satisfactory |
| 60–79 | Good |
| ≥ 80 | Excellent |

Results stored in `AIEvaluation` model (OneToOne → Submission). Students see score circles, strengths, improvement tips, and grammar issues on the `TextSubmissionPage`.

### 7. Domain Predictor (RandomForest)
`backend/apps/tasks/domain_predictor.py`

- 13-feature input vector:
  - `[0:10]` Latest MCQ score per domain
  - `[10]` Task completion rate
  - `[11]` Improvement trend (normalized slope)
  - `[12]` Average task MCQ score
- Trained via `python manage.py train_domain_model`
- Serialized to `backend/ml_models/domain_predictor.pkl`

### 8. Collaborative Filtering
`backend/apps/tasks/collaborative_filtering.py`

- User-based KNN on student × task interaction matrix
- Recommends tasks completed by similar students

---

## Key Workflows

### Assessment → Recommendation

```
Student takes MCQ assessment
        ↓
Evaluation engine calculates domain_score, readiness_level, concept_scores
        ↓
StudentProfile updated (strongest_domain, skill_scores, cluster label)
        ↓
Hybrid recommendation engine selects top-10 tasks
        ↓
Tasks shown with AI score, match reason, and domain badge
```

### Task Completion → Portfolio

```
Student accepts task → TaskAssignment (status: accepted)
        ↓
Student works on task → updates progress %
        ↓
Student submits → TaskCompletion (reflective text)
        ↓
Student completes MCQ → TaskMCQAttempt scored
        ↓
TaskEvaluation created (status: pending, mcq_score set)
        ↓
Mentor evaluates → mentor_score, feedback, strengths, suggestions
        ↓
final_score = avg(mcq_score, mentor_score)
        ↓
PortfolioItem auto-created / updated
        ↓
Portfolio stats recalculated
```

---

## API Overview

All endpoints are prefixed with `/api/`.

| Group | Key Endpoints |
|-------|--------------|
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| Assessments | `GET /assessments/`, `POST /assessments/:id/submit`, `GET /assessments/my-attempts/` |
| Tasks | `GET /tasks/recommended/`, `GET /tasks/my-tasks/`, `PUT /tasks/assignments/:id/update/` |
| Completion | `POST /tasks/assignments/:id/complete/`, `POST /tasks/completions/:id/submit-mcq/` |
| Evaluation | `POST /tasks/evaluations/:id/evaluate/` |
| Portfolio | `GET /tasks/portfolios/me/`, `GET /tasks/portfolios/:id/stats/` |
| Analytics | `GET /tasks/analytics/student/`, `GET /tasks/analytics/mentor/`, `GET /tasks/analytics/admin/` |
| Chatbot | `POST /chatbot/sessions/:id/messages/` |
| Notifications | `GET /notifications/`, `POST /notifications/read-all/` |
| Admin | `GET /auth/admin/stats/`, `GET /auth/admin/users`, `POST /auth/mentor/auto-assign/` |
| Submissions | `POST /submissions/submit/`, `GET /submissions/my/`, `GET /submissions/assignment/:id/` |
| Portfolios | `GET /portfolios/portfolios/me/`, `GET /portfolios/portfolios/:id/stats/` |

---

## User Roles

| Role | Access Level | Key Capabilities |
|------|-------------|-----------------|
| **Student** | Standard | Assessments, tasks, portfolio, chat, analytics |
| **Mentor** | Elevated | Reviews, evaluations, student management, task creation |
| **Admin** | Full | User management, system analytics, announcements |

Route guards implemented via `ProtectedRoute` component checking `user.role`.

---

## Database Schema

Key tables in PostgreSQL:

| Table | Model | Description |
|-------|-------|-------------|
| `users` | User | All users (Student/Mentor/Admin) |
| `accounts_studentprofile` | StudentProfile | Skills, clusters, progress, mentor link |
| `accounts_mentorprofile` | MentorProfile | Expertise, stats, availability |
| `assessments_assessment` | Assessment | MCQ assessments per domain |
| `assessments_question` | Question | Assessment questions with concept weights |
| `assessments_assessmentattempt` | AssessmentAttempt | Attempt results, skill vectors |
| `tasks_task` | Task | Tasks with domain, difficulty, skills |
| `task_assignments` | TaskAssignment | Student–task link with progress |
| `task_completions` | TaskCompletion | Submission + reflective text |
| `task_mcq_attempts` | TaskMCQAttempt | MCQ answers + auto-score |
| `task_evaluations` | TaskEvaluation | Mentor score + final score |
| `portfolio_items` | PortfolioItem | Auto-generated portfolio entries |
| `submissions_submission` | Submission | Student text submissions |
| `submissions_aievaluation` | AIEvaluation | NLP evaluation results (scores, feedback) |
| `submissions_mentorevaluation` | MentorEvaluation | Mentor scored feedback on submissions |
| `chatbot_chatsession` | ChatSession | Chat sessions per user |
| `chatbot_chatmessage` | ChatMessage | Chat messages |
| `notifications_notification` | Notification | In-app notifications |
| `notifications_announcement` | Announcement | Broadcast announcements |
| `notifications_directmessage` | DirectMessage | 1-to-1 messages |

---

## Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=virtual_internship_hub
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Chatbot — OpenRouter LLM (used in production)
OPENROUTER_API_KEY=sk-or-...

# Site URL for chatbot HTTP-Referer header
SITE_URL=https://vihub.site

# Legacy optional keys (if switching providers)
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
```

---

## Running Tests & Management Commands

```bash
# Create admin user
python manage.py create_admin

# Reset admin password
python manage.py reset_admin

# Seed assessment questions
python manage.py seed_assessments

# Train domain prediction ML model
python manage.py train_domain_model

# Train with real data only (no synthetic seed)
python manage.py train_domain_model --no-seed

# Check ML model metadata
python manage.py train_domain_model --info

# Download NLTK data (required for NLP evaluation)
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"

# Run development server
python manage.py runserver

# Apply database migrations
python manage.py migrate
```

---

## Production Deployment

The platform is deployed at **https://vihub.site** on a Contabo VPS (Ubuntu, 8GB RAM) using Docker Compose.

```
Internet → Nginx (HTTPS/443) → Django/Gunicorn (:8000) → PostgreSQL 16
                             ↑ React SPA served as static files by Nginx
```

SSL: Let's Encrypt (auto-renewed). See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full setup instructions.

```bash
# Quick update after a code push:
cd /opt/vihub
git pull origin master
docker compose build nginx backend
docker compose up -d
docker compose exec backend python manage.py migrate
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: your feature"`
4. Push and open a Pull Request

---

## License

This project was developed as a Final Year Project (FYP) for academic purposes.
