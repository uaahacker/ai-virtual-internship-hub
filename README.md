# AI-Supported Virtual Internship Hub

A web-based platform that helps students build freelancing careers through AI-powered skill assessments, personalized domain recommendations, and structured virtual internship tasks.

**Current Version: Prototype (FR1 + FR2)**

---

## Tech Stack

| Layer      | Technology                      |
|------------|---------------------------------|
| Backend    | Django 4.2 + Django REST Framework |
| Database   | MongoDB (via Djongo)            |
| Auth       | JWT (SimpleJWT)                 |
| Frontend   | React 18 (Vite) + Tailwind CSS |
| State Mgmt | React Context API               |

---

## Features Implemented (Prototype)

### FR1: User Registration & Authentication
- Role-based registration (Student / Mentor)
- Admin creation via management command
- JWT-based login & logout
- Password validation (min 8 chars + Django validators)
- Role-based access control (Student, Mentor, Admin)
- Protected routes & dashboards per role

### FR2: Skill Assessment + Recommendations
- Browse domain-specific MCQ assessments
- Take assessments with interactive UI
- Automatic score calculation
- Skill level classification (Beginner / Intermediate / Advanced)
- Personalized freelancing domain recommendations
- Assessment history on student dashboard

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+ & npm**
- **MongoDB** running locally on `mongodb://localhost:27017`
  - Install MongoDB Community Edition: https://www.mongodb.com/try/download/community
  - Or use MongoDB Atlas (update `MONGO_HOST` in `.env`)

---

## Quick Start

### 1. Clone & Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies (order matters for djongo compatibility)
pip install Django==4.2.11 djangorestframework djangorestframework-simplejwt pymongo==3.13.0 django-cors-headers python-dotenv pytz sqlparse==0.2.4
pip install djongo==1.3.6 --no-deps

# Copy environment file
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py create_admin

# Seed assessment data (5 assessments, 10-12 MCQs each)
python manage.py seed_assessments

# Start backend server
python manage.py runserver
```

Backend runs at: `http://localhost:8000`

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Default Accounts

| Role    | Email           | Password   |
|---------|-----------------|------------|
| Admin   | admin@hub.com   | Admin@123  |
| Student | (register new)  | (your pwd) |
| Mentor  | (register new)  | (your pwd) |

---

## API Endpoints

### Authentication
| Method | Endpoint                 | Auth     | Description              |
|--------|--------------------------|----------|--------------------------|
| POST   | `/api/auth/register`     | Public   | Register Student/Mentor  |
| POST   | `/api/auth/login`        | Public   | Login, returns JWT       |
| POST   | `/api/auth/logout`       | Bearer   | Logout (blacklist token) |
| GET    | `/api/auth/me`           | Bearer   | Get current user profile |
| GET    | `/api/auth/admin/users`  | Admin    | List all users           |

### Assessments
| Method | Endpoint                           | Auth    | Description              |
|--------|------------------------------------|---------|--------------------------|
| GET    | `/api/assessments/`                | Student | List active assessments  |
| GET    | `/api/assessments/<id>/`           | Student | Assessment with questions |
| POST   | `/api/assessments/<id>/submit`     | Student | Submit & get results     |
| GET    | `/api/assessments/attempts/<id>/`  | Student | View past attempt result |
| GET    | `/api/assessments/my-attempts/`    | Student | List all past attempts   |

---

## Frontend Routes

| Path                          | Role      | Page                     |
|-------------------------------|-----------|--------------------------|
| `/login`                      | Public    | Login                    |
| `/register`                   | Public    | Registration             |
| `/student/dashboard`          | Student   | Student Dashboard        |
| `/student/assessments`        | Student   | Assessment List          |
| `/student/assessments/:id`    | Student   | Take Assessment          |
| `/student/results/:attemptId` | Student   | View Result              |
| `/mentor/dashboard`           | Mentor    | Mentor Dashboard         |
| `/admin/dashboard`            | Admin     | Admin Dashboard          |

---

## Security Notes

- **JWT tokens are stored in `localStorage`** for simplicity in this prototype. In production, consider:
  - HttpOnly cookies for refresh tokens
  - In-memory storage for access tokens
  - CSRF protection with cookie-based auth
- Passwords are hashed using Django's default PBKDF2 algorithm.
- CORS is configured to allow only the React dev server origin.

---

## Project Structure

```
fyp/
├── backend/
│   ├── config/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/            # Shared utilities (permissions, exceptions)
│   │   ├── accounts/        # FR1: User model, auth views
│   │   ├── assessments/     # FR2: Assessment models, views, recommendations
│   │   ├── tasks/           # Stub (future)
│   │   ├── submissions/     # Stub (future)
│   │   ├── portfolios/      # Stub (future)
│   │   └── notifications/   # Stub (future)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── contexts/        # React Context (Auth)
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── README.md
└── PROJECT_SPEC_FOR_CLAUDE.md
```

---

## Future Modules (Stubs Created)

- **Tasks**: Task creation, assignment, student task management
- **Submissions**: File upload, submission tracking
- **AI Evaluation**: Automated scoring with AI
- **Mentor Evaluation**: Manual feedback from mentors
- **Portfolios**: Student work showcase + external profiles
- **Notifications**: Real-time notification system

---

## License

This project is part of an academic Final Year Project (FYP).
