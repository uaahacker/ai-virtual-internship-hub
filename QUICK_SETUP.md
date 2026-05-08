# AI-Supported Virtual Internship Hub — Quick Setup Guide

> **For the Evaluator:** This guide gets the full system running locally in under 15 minutes.  
> No Docker or internet connection is needed beyond the initial dependency install.

---161.97.145.123

## What is this project?

An AI-powered virtual freelancing internship platform for students. Key features:

- **Adaptive MCQ Assessments** — 10 freelancing domains, questions ordered by Q-Learning based on student ability
- **AI Task Recommendation** — Hybrid content-based + collaborative filtering (KNN, K=7) recommends internship tasks
- **Student Clustering** — KMeans groups students into Explorer / Developing / Competent / Expert tiers
- **Domain Predictor** — RandomForest (95.58% accuracy) predicts the student's best-fit domain
- **Plagiarism Detection** — TF-IDF cosine similarity on task reflections
- **NLP Feedback** — NLTK-powered automatic feedback on assessment results
- **AI Chatbot** — Career guidance chatbot (rule-based fallback; plug in OpenRouter/OpenAI key for LLM)
- **Three Roles** — Student · Mentor · Admin, each with a dedicated dashboard
- **Google OAuth** — Sign in with Google (optional; requires a Client ID)

---

## Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10 or 3.11 | https://www.python.org/downloads/ |
| Node.js | 18 or 20 | https://nodejs.org/ |
| PostgreSQL | 14 – 16 | https://www.postgresql.org/download/ |

> During PostgreSQL install, keep the default port **5432** and note the password you set for the `postgres` user.

---

## Backend Setup

### Step 1 — Create the database

Open the **psql** shell (search "psql" in Start Menu or run `psql -U postgres`):

```sql
CREATE DATABASE virtual_internship_hub;
\q
```

---

### Step 2 — Create the `.env` file

Inside the `backend/` folder, create a file named **`.env`** with the content below.  
Replace `YOUR_POSTGRES_PASSWORD` with the password you set during PostgreSQL install.

```env
DJANGO_SECRET_KEY=dev-secret-key-for-local-testing-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=virtual_internship_hub
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173

JWT_ACCESS_LIFETIME_MINUTES=60
JWT_REFRESH_LIFETIME_DAYS=7

# Optional — leave blank to use the built-in rule-based chatbot
OPENROUTER_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

# Optional — leave blank to disable Google OAuth sign-in
GOOGLE_CLIENT_ID=
```

> **Tip:** If your PostgreSQL password is simply `postgres` (common on fresh installs), set `DB_PASSWORD=postgres`.

---

### Step 3 — Install Python dependencies

Open a terminal inside the `backend/` folder:

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install all packages
pip install -r requirements.txt
```

---

### Step 4 — Run database migrations

```bash
python manage.py migrate
```

---

### Step 5 — Seed the platform data

```bash
# Creates assessments for all 10 domains (10 x 10 questions each)
python manage.py seed_assessments

# Creates 90 internship tasks (3 tasks x 3 difficulty levels x 10 domains)
# Each task includes MCQ questions
python manage.py seed_tasks

# Creates the admin account
python manage.py create_admin
```

---

### Step 6 — Download NLTK data (for NLP feedback engine)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords'); nltk.download('punkt_tab'); nltk.download('words')"
```

---

### Step 7 — (Optional) Train the domain predictor ML model

```bash
python manage.py train_domain_model
```

> The pre-trained model is included in `ml_models/` so this step is optional.

---

### Step 8 — Start the backend server

```bash
python manage.py runserver
```

Backend is now running at **http://localhost:8000**

---

## Frontend Setup

Open a **second terminal** in the `frontend/` folder:

```bash
cd frontend
npm install
npm run dev
```

Frontend is now running at **http://localhost:5173**

---

## Login Credentials

The `create_admin` command creates this account automatically:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@hub.com` | `Admin@123` |

To test **Student** and **Mentor** flows, register new accounts through the frontend:
- Go to **http://localhost:5173**
- Click **Register**
- Choose role: Student or Mentor
- Fill in the details and submit

> Email verification tokens are printed in the backend terminal output (no email server needed).

---

## What to Check / Demo Path

### As Admin (`admin@hub.com` / `Admin@123`)
1. Log in → Admin Dashboard shows platform-wide analytics
2. Go to **Users** — manage students and mentors, assign mentors to students
3. Go to **Analytics** → Cluster Overview (KMeans student groupings)
4. Go to **Analytics** → Domain Prediction (RandomForest predictions)
5. Create an **Announcement** — broadcasts to all users

### As Student (register a new account)
1. Complete an **Assessment** in any domain → see adaptive question ordering + NLP feedback
2. View **Recommended Tasks** → AI-generated list (content-based + collaborative filter)
3. Accept a task → update progress → submit with a reflection text
4. Complete the **MCQ Quiz** attached to the task
5. View **Portfolio** after mentor evaluates
6. Use the **AI Chatbot** for career guidance
7. View **Notifications** (polling every 30 seconds)

### As Mentor (register a new account, role = Mentor)
1. View **Assigned Students** and their skill profiles
2. Go to **Pending Reviews** → evaluate submitted tasks (score + feedback)
3. Send a **Direct Message** to an assigned student

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `password authentication failed for user "postgres"` | Wrong password in `.env` — check `DB_PASSWORD` |
| `could not connect to server` (port 5432) | Start the PostgreSQL service: **Services → postgresql-x64-16 → Start** |
| `database "virtual_internship_hub" does not exist` | Run `CREATE DATABASE virtual_internship_hub;` in psql |
| `relation does not exist` | Run `python manage.py migrate` |
| `No module named 'psycopg2'` | Run `pip install psycopg2-binary` |
| `ModuleNotFoundError` for any package | Ensure the venv is activated, then `pip install -r requirements.txt` |
| Frontend shows CORS error | Confirm backend is on port 8000 and `.env` has `CORS_ALLOWED_ORIGINS=http://localhost:5173` |
| Chatbot returns canned replies | Expected — rule-based fallback is active. Add an `OPENROUTER_API_KEY` for LLM responses |
| Google login button does nothing | Expected — `GOOGLE_CLIENT_ID` is blank. All other features work without it |

---

## Project Structure (top-level)

```
fyp/
├── backend/          Django 4.2 + DRF API
│   ├── apps/
│   │   ├── accounts/     Auth, JWT, Google OAuth, profiles
│   │   ├── assessments/  MCQ assessments + adaptive Q-Learning
│   │   ├── tasks/        Task lifecycle, AI recommender, analytics
│   │   ├── chatbot/      AI career chatbot
│   │   ├── notifications/ Notifications, announcements, DMs
│   │   ├── portfolios/   Auto-generated student portfolio
│   │   └── core/         Shared permissions
│   ├── ml_models/        Pre-trained model files (.pkl, .json)
│   └── datasets/         Training data CSVs
└── frontend/         React 18 + Vite + Tailwind CSS SPA
```

**Full documentation:** See `README.md` (project overview) and `backend/README.md` (API + ML details).
