# accounts — Authentication & User Management

The `accounts` app handles all user identity: registration, JWT-based login, Google OAuth sign-in/up, email verification, password reset, profile picture upload (Pillow-compressed), profile management for students and mentors, and admin-level user administration.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Authentication Flow](#authentication-flow)
4. [Google OAuth Flow](#google-oauth-flow)
5. [Email Verification](#email-verification)
6. [Password Reset](#password-reset)
7. [Profile Picture Upload](#profile-picture-upload)
8. [Student Profile Management](#student-profile-management)
9. [Mentor Profile Management](#mentor-profile-management)
10. [Mentor–Student Assignment](#mentorstudent-assignment)
11. [Admin Endpoints](#admin-endpoints)
12. [Serializers](#serializers)
13. [Custom User Backend](#custom-user-backend)
14. [Management Commands](#management-commands)

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
| `profile_picture` | ImageField (nullable) | Stored in `media/profile_pictures/` |
| `is_active` | BooleanField | Default True |
| `is_staff` | BooleanField | Default False |
| `is_email_verified` | BooleanField | Default False; set True after token verification |
| `onboarding_complete` | BooleanField | Default False for Google OAuth new users |
| `date_joined` | DateTimeField | Auto set on create |

Auth backend: `apps.accounts.backends.EmailBackend`

---

### `VerificationToken`
Used for both email verification and password reset.

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey → User | Token owner |
| `token` | UUIDField, default=uuid4 | Unique one-time token |
| `token_type` | CharField | `email_verify` / `password_reset` |
| `expires_at` | DateTimeField | 24 hours after creation |
| `is_used` | BooleanField | Default False; set True on use |

---

### `StudentProfile`
One-to-one with User (role=student). Auto-created on student registration.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField → User | `related_name='student_profile'` |
| `assigned_mentor` | ForeignKey → User (nullable) | Assigned mentor (`related_name='assigned_students'`) |
| `bio` | TextField | Optional student bio |
| `skills` | JSONField | List of self-declared skills |
| `education` | CharField | |
| `experience_level` | CharField | beginner / intermediate / advanced |
| `strongest_domain` | CharField | Updated by assessment evaluation engine |
| `weakest_domain` | CharField | Updated by assessment evaluation engine |
| `skill_scores` | JSONField | Dict `{domain: score}`, 10 domains |
| `cluster_id` | IntegerField (nullable) | KMeans cluster 0–3 |
| `cluster_label` | CharField | Explorer / Developing / Competent / Expert |
| `cluster_summary` | JSONField (nullable) | `{display_name, description}` for UI badge |
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
| `expertise_domains` | JSONField | List of domain strings |
| `specialization` | CharField | Primary area of specialization |
| `years_experience` | IntegerField | |
| `availability_status` | CharField | available / busy / away |
| `is_auto_assignable` | BooleanField | Whether admin can auto-assign students |
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
| PUT | `profile/update/` | `UpdateProfileView` | Update profile + upload profile picture |
| POST | `google/` | `GoogleAuthView` | Google OAuth sign-in/up — returns JWT pair |
| POST | `verify-email/` | `VerifyEmailView` | Activate account via UUID token |
| POST | `forgot-password/` | `ForgotPasswordView` | Request password reset token |
| POST | `reset-password/` | `ResetPasswordView` | Set new password via token |

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

1. `POST /api/auth/register/` — creates User + profile (StudentProfile or MentorProfile) + `VerificationToken`
2. Client calls `POST /api/auth/verify-email/` with the returned token to activate account
3. `POST /api/auth/login/` — validates credentials via `EmailBackend`, returns:
   ```json
   { "access": "...", "refresh": "..." }
   ```
4. Frontend stores tokens in `localStorage`.
5. Each request adds `Authorization: Bearer <access>` header.
6. On 401, frontend hits `POST /api/token/refresh/` with the refresh token.
7. `POST /api/auth/logout/` blacklists the refresh token.

---

## Google OAuth Flow

1. Frontend renders the Google Sign-In button (`@react-oauth/google`).
2. Google returns a credential (ID token) to the frontend.
3. Frontend sends: `POST /api/auth/google/` `{ "token": "<google_id_token>" }`
4. `GoogleAuthView` verifies via `google.oauth2.id_token.verify_oauth2_token()` using `GOOGLE_CLIENT_ID`.
5. If user exists → log in. If new → create user with `onboarding_complete=False`.
6. JWT pair is returned.
7. Frontend checks `onboarding_complete`:
   - `False` → redirect to `GoogleOnboardingPage` for role selection
   - `True` → redirect to role dashboard directly

```python
# backend/apps/accounts/views.py
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

payload = id_token.verify_oauth2_token(
    token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
)
```

---

## Email Verification

```
1. POST /api/auth/register/
       → User created (is_email_verified=False)
       → VerificationToken created (type='email_verify', 24h expiry)
       → Token returned in response body (no SMTP required in dev)

2. POST /api/auth/verify-email/
       body: { "token": "<uuid>" }
       → Token validated (not expired, not used, correct type)
       → user.is_email_verified = True
       → token.is_used = True
       → JWT pair returned
```

---

## Password Reset

```
1. POST /api/auth/forgot-password/
       body: { "email": "user@example.com" }
       → VerificationToken created (type='password_reset')
       → Token returned in response (or emailed if SMTP configured)

2. POST /api/auth/reset-password/
       body: { "token": "<uuid>", "new_password": "..." }
       → Token validated
       → user.set_password(new_password)
       → token.is_used = True
```

---

## Profile Picture Upload

Endpoint: `PUT /api/auth/profile/update/`  
Content-Type: `multipart/form-data`

**Server-side flow:**
1. `UpdateProfileSerializer.save()` writes the file to disk
2. Pillow opens the file and:
   - Converts to RGB (handles PNG alpha channels)
   - `image.thumbnail((400, 400), Image.LANCZOS)` — maintains aspect ratio
   - Re-saves as JPEG at quality=85
3. Fresh DB read: `User.objects.get(pk=user_id)` avoids `SimpleLazyObject` caching issues
4. Response includes `profile_picture_url` — absolute URL via `request.build_absolute_uri()`

**Frontend requirement:**  
Do **not** set `Content-Type: application/json` when sending FormData — let the browser set the `multipart/form-data; boundary=...` header automatically.

**Storage:** `media/profile_pictures/profile_<user_id>.jpg` (Docker named volume `media_files`)  
**Nginx:** Serves `/media/` from the volume with 7-day cache headers

---

## Student Profile Management

Students can GET and update their own profile via:
- `GET /api/auth/student/profile/` — returns full profile with cluster info, skill scores, mentor details
- `PUT /api/auth/student/profile/update/` — update bio, skills, education, experience_level

The following fields are **system-managed** (not editable via API):
- `strongest_domain`, `weakest_domain` — set by assessment evaluation engine
- `skill_scores` — set by assessment evaluation engine
- `cluster_id`, `cluster_label`, `cluster_summary` — set by KMeans `StudentClusterer`
- `total_tasks_completed`, `average_score`, `completion_rate` — set by portfolio service
- `assigned_mentor` — set by mentor assignment (manual or auto)

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
| `UserSerializer` | Full user info including `profile_picture_url` (absolute URL via `get_profile_picture_url` SerializerMethodField) |
| `UpdateProfileSerializer` | Profile update with optional profile picture |
| `StudentProfileSerializer` | Student profile R/W |
| `MentorProfileSerializer` | Mentor profile R/W |
| `AdminUserSerializer` | Admin view of user with profile info |

**`UserSerializer.get_profile_picture_url()`** — returns absolute URL using `request.build_absolute_uri()` from serializer context; returns `None` defensively if no picture or URL resolution fails.

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
