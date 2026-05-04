# accounts — Authentication & User Management

The `accounts` app handles all user identity: registration, JWT-based login, profile management for students and mentors, and admin-level user administration.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Authentication Flow](#authentication-flow)
4. [Student Profile Management](#student-profile-management)
5. [Mentor Profile Management](#mentor-profile-management)
6. [Mentor–Student Assignment](#mentorstudent-assignment)
7. [Admin Endpoints](#admin-endpoints)
8. [Serializers](#serializers)
9. [Custom User Backend](#custom-user-backend)
10. [Management Commands](#management-commands)

---

## Models

### `User`
Custom `AbstractBaseUser` extending Django's auth framework.

| Field | Type | Notes |
|-------|------|-------|
| `email` | EmailField, unique | Primary username field (`USERNAME_FIELD = 'email'`) |
| `first_name` | CharField | |
| `last_name` | CharField | |
| `role` | CharField | `student` / `mentor` / `admin` |
| `is_active` | BooleanField | Default True |
| `is_staff` | BooleanField | Default False |
| `date_joined` | DateTimeField | Auto set on create |

Auth backend: `apps.accounts.backends.EmailBackend`

---

### `StudentProfile`
One-to-one with User (role=student). Auto-created on student registration.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField → User | `related_name='student_profile'` |
| `mentor` | ForeignKey → User (nullable) | Assigned mentor |
| `bio` | TextField | Optional student bio |
| `skills` | JSONField | List of self-declared skills |
| `education` | CharField | |
| `experience_level` | CharField | beginner / intermediate / advanced |
| `strongest_domain` | CharField | Updated by assessment engine |
| `weakest_domain` | CharField | Updated by assessment engine |
| `skill_scores_by_domain` | JSONField | Dict `{domain: score}`, 10 domains |
| `cluster_id` | IntegerField (nullable) | KMeans cluster 0–3 |
| `cluster_label` | CharField | Explorer / Developing / Competent / Expert |
| `total_tasks_completed` | IntegerField | |
| `average_score` | FloatField | |
| `completion_rate` | FloatField | |

---

### `MentorProfile`
One-to-one with User (role=mentor). Auto-created on mentor registration.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField → User | `related_name='mentor_profile'` |
| `bio` | TextField | |
| `expertise` | JSONField | List of domains |
| `years_experience` | IntegerField | |
| `hourly_rate` | DecimalField | |
| `is_available` | BooleanField | |
| `max_students` | IntegerField | Default 10 |
| `total_reviews` | IntegerField | Counter |
| `average_rating` | FloatField | |

---

## URL Reference

All URLs are prefixed with `/api/auth/`.

### Authentication

| Method | Path | View | Description |
|--------|------|------|-------------|
| POST | `register/` | `RegisterView` | Register new user (student or mentor) |
| POST | `login/` | `LoginView` | Login — returns JWT access + refresh tokens |
| POST | `logout/` | `LogoutView` | Blacklist refresh token |
| POST | `token/refresh/` | `TokenRefreshView` | Get new access token |
| GET | `me/` | `MeView` | Get current authenticated user info |

### Student Profile

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `student/profile/` | `StudentProfileView` | Get own profile |
| PUT | `student/profile/update/` | `StudentProfileUpdateView` | Update own profile |
| GET | `student/mentor/` | `StudentMentorView` | Get assigned mentor info |

### Mentor Profile

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `mentor/profile/` | `MentorProfileView` | Get own profile |
| PUT | `mentor/profile/update/` | `MentorProfileUpdateView` | Update own profile |
| GET | `mentor/students/` | `MentorStudentsView` | List assigned students |
| GET | `mentor/pending-reviews/` | `MentorPendingReviewsView` | Tasks pending mentor evaluation |
| GET | `mentor/review-history/` | `MentorReviewHistoryView` | Last 20 evaluations by this mentor |

### Admin — User Management

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `admin/stats/` | `AdminStatsView` | System-wide counts |
| GET | `admin/users/` | `AdminUsersView` | List all users |
| POST | `admin/users/` | `AdminCreateUserView` | Create any user |
| GET | `admin/users/:id/` | `AdminUserDetailView` | Get user detail |
| PUT | `admin/users/:id/update/` | `AdminUserUpdateView` | Edit user |
| DELETE | `admin/users/:id/delete/` | `AdminUserDeleteView` | Delete user |
| POST | `admin/users/:id/reset-password/` | `AdminResetPasswordView` | Force reset password |

### Mentor–Student Assignment

| Method | Path | View | Description |
|--------|------|------|-------------|
| POST | `mentor/assign-student/` | `AssignStudentView` | Mentor assigns a student to themselves |
| POST | `mentor/unassign-student/` | `UnassignStudentView` | Remove student from mentor |
| GET | `mentor/available-students/` | `AvailableStudentsView` | Students without a mentor |
| POST | `mentor/auto-assign/` | `AutoAssignMentorsView` | Admin auto-assign unassigned students |

---

## Authentication Flow

1. `POST /api/auth/register/` — creates User + profile (StudentProfile or MentorProfile)
2. `POST /api/auth/login/` — validates credentials, returns:
   ```json
   { "access": "...", "refresh": "..." }
   ```
3. Frontend stores tokens in `localStorage`.
4. Each request adds `Authorization: Bearer <access>` header.
5. On 401, frontend hits `POST /api/token/refresh/` with the refresh token.
6. `POST /api/auth/logout/` blacklists the refresh token.

---

## Student Profile Management

Students can GET and update their own profile via:
- `GET /api/auth/student/profile/` — returns full profile with cluster info, skill scores, mentor details
- `PUT /api/auth/student/profile/update/` — update bio, skills, education, experience_level

The following fields are **system-managed** (not editable via API):
- `strongest_domain`, `weakest_domain` — set by assessment evaluation engine
- `skill_scores_by_domain` — set by assessment evaluation engine
- `cluster_id`, `cluster_label` — set by KMeans StudentClusterer
- `total_tasks_completed`, `average_score`, `completion_rate` — set by portfolio service

---

## Mentor Profile Management

Mentors can update bio, expertise, availability, and hourly rate.  
The `total_reviews` and `average_rating` fields are updated automatically when TaskEvaluations are completed.

---

## Mentor–Student Assignment

**Manual (by mentor):**
```
POST /api/auth/mentor/assign-student/
{ "student_id": 42 }
```

**Auto-assign (admin only):**
```
POST /api/auth/mentor/auto-assign/
```
Assigns all unassigned students to the mentor with the fewest current students (load-balancing).

---

## Admin Endpoints

Admin endpoints require `IsAdmin` permission (`role == 'admin'` or `is_staff == True`).

`GET /api/auth/admin/stats/` returns:
```json
{
  "total_users": 120,
  "total_students": 100,
  "total_mentors": 15,
  "total_admins": 5,
  "active_users": 118
}
```

---

## Serializers

| Serializer | Purpose |
|-----------|---------|
| `UserRegistrationSerializer` | Validates registration, hashes password, creates profile |
| `UserLoginSerializer` | Email + password → JWT tokens |
| `UserSerializer` | Full user info (used by `GET /me/`) |
| `StudentProfileSerializer` | Student profile R/W |
| `MentorProfileSerializer` | Mentor profile R/W |
| `AdminUserSerializer` | Admin view of user with profile info |

---

## Custom User Backend

`apps/accounts/backends.py` — `EmailBackend`

Overrides `ModelBackend.authenticate()` to use `email` instead of `username` for password-based login. This backend is added to `AUTHENTICATION_BACKENDS` in settings.

---

## Management Commands

```bash
# Interactively create an admin user
python manage.py create_admin

# Interactively reset the admin user's password
python manage.py reset_admin
```
