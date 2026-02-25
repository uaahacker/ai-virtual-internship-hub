# PROJECT SPEC FOR CLAUDE — AI-Supported Virtual Internship Hub

> **Purpose:** This file is "memory" for future Claude sessions. It captures scope rules,
> architectural decisions, diagram mappings, and where each feature lives in code.
> Read this file first before making any changes.

---

## 1. PROJECT OVERVIEW

**Project:** AI-Supported Virtual Internship Hub for Freelancing Careers  
**Tech Stack:** Django 4.2 + DRF (backend) | React 18 + Vite + Tailwind (frontend) | MongoDB via Djongo  
**Auth:** JWT via SimpleJWT | Custom User model with role field  

---

## 2. SCOPE RULES

### Prototype (Current — FR1 + FR2)
- **FR1:** User Registration + Authentication + Role-Based Access Control
- **FR2:** Skill Assessment (MCQ) + Automated Score + Domain Recommendation

### What is FULLY implemented:
- Custom User model (email-based auth, roles: Student/Mentor/Admin)
- Registration (Student/Mentor only), Login, Logout, Me endpoint
- JWT token auth with role embedded in payload
- Role-based permissions (IsStudent, IsMentor, IsAdmin)
- Protected frontend routes per role
- Admin user list (read-only)
- MCQ assessments with 5 seeded domains (10-12 questions each)
- Automatic scoring + skill level classification + recommendation engine
- Assessment history tracking per student
- All dashboard UIs (Student, Mentor, Admin)

### What is STUB ONLY (models exist, no logic):
- Tasks & TaskAssignments
- Submissions
- AI Evaluations
- Mentor Evaluations
- Portfolios & Portfolio Items & External Profiles
- Notifications
- Student Profiles, Mentor Profiles, Skills, Student Skills

---

## 3. MAPPING TO DESIGN DIAGRAMS

### 3.1 Class Diagram (classdiagram.png)
| Class in Diagram       | Django Model                    | Status        |
|------------------------|---------------------------------|---------------|
| User                   | apps.accounts.models.User       | ✅ Implemented |
| Assessment             | apps.assessments.models.Assessment | ✅ Implemented |
| AssessmentAttempt      | apps.assessments.models.AssessmentAttempt | ✅ Implemented |
| Skill                  | (not created yet)               | 🔲 Future      |
| StudentSkill           | (not created yet)               | 🔲 Future      |
| StudentProfile         | (not created yet)               | 🔲 Future      |
| MentorProfile          | (not created yet)               | 🔲 Future      |
| Task                   | apps.tasks.models.Task          | 📦 Stub        |
| TaskAssignment         | apps.tasks.models.TaskAssignment | 📦 Stub       |
| Submission             | apps.submissions.models.Submission | 📦 Stub     |
| AIEvaluation           | apps.submissions.models.AIEvaluation | 📦 Stub   |
| MentorEvaluation       | apps.submissions.models.MentorEvaluation | 📦 Stub |
| Portfolio              | apps.portfolios.models.Portfolio | 📦 Stub      |
| PortfolioItem          | apps.portfolios.models.PortfolioItem | 📦 Stub  |
| ExternalProfile        | apps.portfolios.models.ExternalProfile | 📦 Stub |
| Notification           | apps.notifications.models.Notification | 📦 Stub |

### 3.2 Database Design (databaseDesign.png) — MongoDB Collections
| Collection (Diagram)   | Django db_table         | Status        |
|------------------------|-------------------------|---------------|
| users                  | users                   | ✅ Implemented |
| assessments            | assessments             | ✅ Implemented |
| questions              | questions               | ✅ Implemented |
| assessment_attempts    | assessment_attempts     | ✅ Implemented |
| tasks                  | tasks                   | 📦 Stub        |
| task_assignments       | task_assignments        | 📦 Stub        |
| submissions            | submissions             | 📦 Stub        |
| ai_evaluations         | ai_evaluations          | 📦 Stub        |
| mentor_evaluations     | mentor_evaluations      | 📦 Stub        |
| portfolios             | portfolios              | 📦 Stub        |
| portfolio_items        | portfolio_items         | 📦 Stub        |
| external_profiles      | external_profiles       | 📦 Stub        |
| notifications          | notifications           | 📦 Stub        |
| student_profiles       | (not created)           | 🔲 Future      |
| mentor_profiles        | (not created)           | 🔲 Future      |
| skills                 | (not created)           | 🔲 Future      |
| student_skills         | (not created)           | 🔲 Future      |

### 3.3 Architecture Diagram (architectureDiagram.png) — 3-Tier
| Tier               | Implementation                                  |
|--------------------|--------------------------------------------------|
| Presentation       | React (Vite) + Tailwind CSS + React Router       |
| Application/API    | Django REST Framework (DRF) APIViews              |
| AI Services Layer  | recommendation.py (simple rule-based engine)      |
| Database           | MongoDB via Djongo                                |
| Auth Service       | SimpleJWT + custom EmailBackend                   |
| Notification Svc   | 📦 Stub (future)                                  |
| Task Mgmt Service  | 📦 Stub (future)                                  |

### 3.4 Sequence Diagrams (sequencediagram.png)
| Sequence                  | Implementation Path                              |
|---------------------------|--------------------------------------------------|
| User Login                | LoginView → EmailBackend → JWT token generation  |
| Task Submit + Evaluation  | 📦 Stub (future)                                 |
| AI Recommendation         | SubmitAssessmentView → recommendation.py → store attempt |

### 3.5 UI Reference (interfaceDesign.png)
| Screen                 | Frontend Component         | Status        |
|------------------------|----------------------------|---------------|
| Login page             | pages/LoginPage.jsx        | ✅ Implemented |
| Student Dashboard      | pages/StudentDashboard.jsx | ✅ Implemented |
| Submit Task page       | (not created)              | 🔲 Future      |
| Mentor Dashboard       | pages/MentorDashboard.jsx  | ✅ Placeholder |

---

## 4. API ENDPOINTS

### Auth (apps.accounts)
```
POST   /api/auth/register        → RegisterView (public, Student|Mentor)
POST   /api/auth/login           → LoginView (public, returns JWT tokens)
POST   /api/auth/logout          → LogoutView (authenticated, blacklists refresh)
GET    /api/auth/me              → MeView (authenticated)
GET    /api/auth/admin/users     → AdminUserListView (admin only)
```

### Assessments (apps.assessments)
```
GET    /api/assessments/              → AssessmentListView (student)
GET    /api/assessments/<id>/         → AssessmentDetailView (student)
POST   /api/assessments/<id>/submit   → SubmitAssessmentView (student)
GET    /api/assessments/attempts/<id>/ → AttemptDetailView (student)
GET    /api/assessments/my-attempts/  → StudentAttemptsListView (student)
```

---

## 5. KEY ARCHITECTURAL DECISIONS

1. **Custom User Model** (AbstractBaseUser + PermissionsMixin) — email as USERNAME_FIELD
2. **Email-based auth** via custom `EmailBackend`
3. **Role stored in User model** — not a separate table; roles are: Student, Mentor, Admin
4. **Permissions** — custom DRF permission classes in `apps.core.permissions`
5. **Assessment Questions** — stored as separate model rows with option_a/b/c/d fields (not JSON array)
6. **Recommendation engine** — simple rule-based (≥80% Advanced, 50-79% Intermediate, <50% Beginner) in `apps.assessments.recommendation.py`
7. **JWT payload** includes role and name for frontend convenience
8. **Frontend auth** — tokens stored in localStorage (see security notes in README)
9. **CORS** — configured for React dev server at localhost:5173

---

## 6. MANAGEMENT COMMANDS

```bash
python manage.py create_admin              # Creates admin@hub.com / Admin@123
python manage.py create_admin --email xyz  # Custom admin email
python manage.py seed_assessments          # Seeds 5 assessments with MCQs
python manage.py seed_assessments --clear  # Clears and re-seeds
```

---

## 7. FUTURE MODULES PLAN

### Phase 2: FR3 — Task Management
- Implement Task CRUD (mentor/admin creates tasks)
- Task assignment to students
- File: `apps.tasks.views`, `apps.tasks.serializers`
- Frontend: `/student/tasks`, `/mentor/tasks`

### Phase 3: FR4 — Submissions & AI Evaluation
- Student submits work (file upload)
- AI evaluation engine (plagiarism check, quality scoring)
- Mentor manual evaluation
- Files: `apps.submissions.views`, `apps.submissions.serializers`
- Frontend: `/student/submissions`, `/mentor/reviews`

### Phase 4: FR5 — Portfolio Management
- Auto-build portfolio from completed tasks
- External profile linking (Upwork, Fiverr, LinkedIn)
- Files: `apps.portfolios.views`, `apps.portfolios.serializers`
- Frontend: `/student/portfolio`

### Phase 5: FR6 — Notifications
- Real-time notifications for task assignments, evaluation results
- Files: `apps.notifications.views`
- Frontend: notification bell in header

### Phase 6: FR7 — AI Chatbot (Career Guidance)
- New app: `apps.chatbot`
- Integration with LLM API for career guidance
- Frontend: chat widget

### Phase 7: FR8 — Reporting & Analytics
- Admin analytics dashboard
- Student progress reports
- New app: `apps.analytics`

---

## 8. SEEDED ASSESSMENT DOMAINS

Aligned with DigiSkills Pakistan areas:
1. **Programming** (Web Development Fundamentals) — 12 questions
2. **Content Writing** (Content Writing Skills) — 12 questions
3. **Graphic Design** (Graphic Design Fundamentals) — 10 questions
4. **Freelancing** (Freelancing Essentials) — 10 questions
5. **E-Commerce** (E-Commerce Knowledge) — 10 questions

More can be added via `seed_assessments` command or Django admin.

---

## 9. RECOMMENDATION LOGIC

Located in: `backend/apps/assessments/recommendation.py`

```
percentage >= 80%  → Advanced     → strong recommendation + 2 freelancing roles
50% <= pct < 80%   → Intermediate → recommend domain + improvement resources
percentage < 50%   → Beginner     → learning path + foundational resources
```

Each domain has pre-configured:
- `roles`: 2 example freelancing careers
- `resources`: 2-3 learning resources
- `tips`: one actionable tip

---

## 10. FILE LOCATIONS QUICK REFERENCE

```
backend/config/settings.py          — Django settings (DB, JWT, CORS, etc.)
backend/apps/core/permissions.py    — IsStudent, IsMentor, IsAdmin
backend/apps/core/exceptions.py     — Centralized error handler
backend/apps/accounts/models.py     — User model
backend/apps/accounts/views.py      — Auth views
backend/apps/accounts/backends.py   — Email auth backend
backend/apps/assessments/models.py  — Assessment, Question, AssessmentAttempt
backend/apps/assessments/views.py   — Assessment API views
backend/apps/assessments/recommendation.py — Recommendation engine

frontend/src/contexts/AuthContext.jsx   — Auth state management
frontend/src/services/api.js            — Axios instance with interceptors
frontend/src/services/endpoints.js      — API endpoint functions
frontend/src/components/ProtectedRoute.jsx — Role-based route guard
frontend/src/components/DashboardLayout.jsx — Sidebar layout
frontend/src/pages/LoginPage.jsx        — Login page
frontend/src/pages/RegisterPage.jsx     — Registration page
frontend/src/pages/StudentDashboard.jsx — Student home
frontend/src/pages/AssessmentList.jsx   — Browse assessments
frontend/src/pages/TakeAssessment.jsx   — MCQ test interface
frontend/src/pages/AssessmentResult.jsx — Result + recommendations
frontend/src/pages/AdminDashboard.jsx   — Admin user list
frontend/src/pages/MentorDashboard.jsx  — Mentor placeholder
```
