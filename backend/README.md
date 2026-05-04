# Backend — Django REST API

This directory contains the full Django 4.2 + Django REST Framework backend for the **AI-Supported Virtual Internship Hub**.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [App Summary](#app-summary)
3. [Project Configuration](#project-configuration)
4. [URL Routing](#url-routing)
5. [Authentication & Permissions](#authentication--permissions)
6. [Database & Migrations](#database--migrations)
7. [ML Model Training & Storage](#ml-model-training--storage)
8. [Management Commands](#management-commands)
9. [Setup & Running](#setup--running)
10. [Response Format Convention](#response-format-convention)
11. [App Deep-Dives](#app-deep-dives)

---

## Architecture Overview

```
backend/
├── config/             ← Django settings, URL root, WSGI/ASGI
├── apps/
│   ├── accounts/       ← Auth, JWT, user profiles, mentor assignment
│   ├── assessments/    ← Skill assessments, MCQ, evaluation engine
│   ├── tasks/          ← Tasks, assignment, ML recommendation, evaluation, portfolio
│   ├── chatbot/        ← AI chatbot sessions & messages
│   ├── notifications/  ← Notifications, announcements, direct messages
│   ├── portfolios/     ← Portfolio model (items auto-created by tasks app)
│   ├── core/           ← Shared permissions & custom exception handler
│   └── submissions/    ← (stub, reserved for future expansion)
├── ml_models/          ← Trained .pkl files
├── manage.py
└── requirements.txt
```

---

## App Summary

| App | URL Prefix | Key Responsibility |
|-----|-----------|-------------------|
| `accounts` | `/api/auth/` | Registration, JWT login/refresh/logout, student & mentor profile management, admin user management, mentor-student assignment |
| `assessments` | `/api/assessments/` | Domain skill assessments (MCQ), multi-dimensional evaluation engine, NLP feedback generation, attempt history |
| `tasks` | `/api/tasks/` | Task CRUD, ML-powered recommendations, task assignment lifecycle, MCQ per task, mentor evaluation, auto portfolio generation, analytics |
| `chatbot` | `/api/chatbot/` | Chat sessions, message history, AI career guidance, mentor AI assistant |
| `notifications` | `/api/notifications/` | In-app notifications, broadcast announcements, 1-to-1 direct messages |
| `portfolios` | — | Portfolio and PortfolioItem models; items are created/updated automatically by the tasks app's portfolio service |
| `core` | — | `IsStudent`, `IsMentor`, `IsAdmin` permission classes; custom DRF exception handler |
| `submissions` | — | Reserved stub |

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
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` (configurable via `.env`) |

Database configuration is driven by `.env` variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

---

## URL Routing

`config/urls.py`:

```
/api/auth/           → apps.accounts.urls
/api/assessments/    → apps.assessments.urls
/api/tasks/          → apps.tasks.urls
/api/chatbot/        → apps.chatbot.urls
/api/notifications/  → apps.notifications.urls
/api/token/          → JWT obtain pair (login)
/api/token/refresh/  → JWT refresh
```

---

## Authentication & Permissions

**JWT** issued via `POST /api/auth/login/` (returns `access` + `refresh` tokens).  
All protected endpoints require: `Authorization: Bearer <access_token>`

**Custom permission classes** in `core/permissions.py`:

| Class | Checks |
|-------|--------|
| `IsStudent` | `request.user.role == 'student'` |
| `IsMentor` | `request.user.role == 'mentor'` |
| `IsAdmin` | `request.user.role == 'admin'` or `is_staff` |

These are composable with DRF's `IsAuthenticated`:
```python
permission_classes = [IsAuthenticated, IsStudent]
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

Each app's `migrations/` directory contains its own migration files. The custom User model (`accounts.User`) replaces Django's default auth model — `AUTH_USER_MODEL` must be set before the first migration.

---

## ML Model Training & Storage

Trained models are stored in `backend/ml_models/` (created automatically).

```bash
# Train the RandomForest domain prediction model
python manage.py train_domain_model

# Train without synthetic seed data (only real student records)
python manage.py train_domain_model --no-seed

# Show metadata about the currently saved model
python manage.py train_domain_model --info
```

The KMeans student clustering and KNN collaborative filter are retrained in-memory on each analytics request — they use live database data and do not persist to disk.

---

## Management Commands

| Command | App | Description |
|---------|-----|-------------|
| `create_admin` | accounts | Creates the default admin user interactively |
| `reset_admin` | accounts | Resets admin user's password interactively |
| `seed_assessments` | assessments | Populates the database with domain assessment questions |
| `train_domain_model` | tasks | Trains and saves the RandomForest domain predictor |
| `train_domain_model --no-seed` | tasks | Same, using only real student data |
| `train_domain_model --info` | tasks | Prints metadata for saved model |

---

## Setup & Running

```bash
# 1. Create and activate virtualenv
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK resources (one-time)
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt')"

# 4. Create backend/.env  (see root README for template)

# 5. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE virtual_internship_hub;"

# 6. Run migrations
python manage.py migrate

# 7. Create admin + seed data
python manage.py create_admin
python manage.py seed_assessments
python manage.py train_domain_model

# 8. Start development server
python manage.py runserver
```

API available at **http://localhost:8000/api/**

---

## Response Format Convention

Every API response follows this envelope:

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
    "details": { ... }
  }
}
```

This is enforced via DRF exception handling in `core/exceptions.py`.

---

## App Deep-Dives

See each app's own README for full details:

- [accounts/README.md](apps/accounts/README.md) — Auth, users, profiles, mentor assignment
- [assessments/README.md](apps/assessments/README.md) — Assessments, MCQ, AI evaluation
- [tasks/README.md](apps/tasks/README.md) — Tasks, ML engine, portfolio service, analytics
- [chatbot/README.md](apps/chatbot/README.md) — Chatbot architecture, providers, session flow
- [notifications/README.md](apps/notifications/README.md) — Notifications, announcements, DMs
- [portfolios/README.md](apps/portfolios/README.md) — Portfolio models
- [core/README.md](apps/core/README.md) — Permissions, exceptions
