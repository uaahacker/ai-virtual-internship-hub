# Frontend — React / Vite SPA

The frontend is a React 18 single-page application built with Vite and styled with Tailwind CSS. It communicates with the Django REST API exclusively over HTTP/JSON using JWT authentication.

---

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Getting Started](#getting-started)
4. [Authentication & Routing](#authentication--routing)
5. [State Management & Contexts](#state-management--contexts)
6. [API Services Layer](#api-services-layer)
7. [Pages Reference](#pages-reference)
8. [Components Reference](#components-reference)
9. [Styling Conventions](#styling-conventions)
10. [Environment & Build](#environment--build)

---

## Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| React | 18.2.0 | UI framework |
| Vite | 5.0.0 | Build tool + dev server |
| Tailwind CSS | 3.3.6 | Utility-first styling |
| React Router DOM | 6.20.0 | Client-side routing |
| Axios | 1.6.2 | HTTP client || @react-oauth/google | 0.12.x | Google OAuth Sign-In button || React Icons | 4.12.0 | Icon library |
| React Markdown | 10.1.0 | Render markdown in chat messages |
| React Toastify | 9.1.3 | Toast notifications |

---

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx              ← App entry point (ToastContainer lives here)
    ├── App.jsx               ← All 50+ route definitions
    ├── index.css             ← Tailwind base imports
    ├── services/
    │   ├── api.js            ← Axios instance + JWT interceptor
    │   └── endpoints.js      ← All API service functions (grouped by feature)
    ├── contexts/
    │   ├── AuthContext.jsx   ← User auth state + login/logout/register
    │   ├── ChatContext.jsx   ← Chat session state
    │   └── NotificationContext.jsx ← Notification polling + read state
    ├── components/           ← 13 reusable components
    └── pages/                ← 39 page-level components
```

---

## Getting Started

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
# → Runs on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

The Vite dev server proxies API calls to `http://localhost:8000` (configured in `vite.config.js`).

---

## Authentication & Routing

### JWT Storage

Access and refresh tokens are stored in `localStorage`:
- `access_token`
- `refresh_token`

### Axios Interceptor (`services/api.js`)

Every outgoing request automatically includes `Authorization: Bearer <access_token>`.  
On a 401 response, the interceptor calls `POST /api/token/refresh/` and retries the original request.  
If the refresh also fails, the user is logged out and redirected to `/login`.

### Route Guards (`components/ProtectedRoute.jsx`)

```jsx
<ProtectedRoute role="student">
  <StudentDashboard />
</ProtectedRoute>
```

- Checks `AuthContext.user` is loaded
- Checks `user.role` matches the required `role` prop
- Redirects to `/login` if not authenticated, or `/unauthorized` if wrong role

### Route Map (`App.jsx`)

50+ routes organized by role:

| Path Prefix | Role | Key Pages |
|-------------|------|-----------|
| `/login`, `/register` | Public | Auth pages |
| `/google-onboarding` | New Google users | Role selection after OAuth sign-up |
| `/verify-email` | Public | Email verification after registration |
| `/forgot-password`, `/reset-password` | Public | Password reset flow |
| `/` | Public | Landing page |
| `/student/*` | Student | Dashboard, assessments, tasks, portfolio, analytics, chat |
| `/mentor/*` | Mentor | Dashboard, students, reviews, tasks, analytics, chat |
| `/admin/*` | Admin | Dashboard, users, assessments, tasks, analytics |

---

## State Management & Contexts

### `AuthContext` (`contexts/AuthContext.jsx`)

**Provider**: Wraps entire app in `App.jsx`

**State**:
- `user` — the logged-in user object (with `role`, `id`, `email`, profile data)
- `loading` — true during initial token validation

**Methods**:
- `login(email, password)` — calls API, stores tokens, sets user
- `loginWithGoogle(googleToken)` — sends Google ID token to `/auth/google/`, stores JWT pair
- `register(data)` — creates account, returns verification token
- `logout()` — blacklists refresh token, clears localStorage
- `clearAuth()` — clears local state without API call (used on 401 cascade)
- `setUser(userData)` — updates user state (used after profile picture upload)

**Key notes**:
- User object and tokens stored in `localStorage` (`user`, `access_token`, `refresh_token`)
- `user.profile_picture_url` (not `profile_picture`) holds the absolute URL for display
- After profile update: `setUser(response.data.data)` + `localStorage.setItem('user', JSON.stringify(response.data.data))`

**Hook**: `useAuth()` — used by all pages needing user info or auth actions.

---

### `ChatContext` (`contexts/ChatContext.jsx`)

**State**: `sessions`, `currentSession`, `messages`, `loading`, `error`

**Methods**:
- `fetchSessions()` — loads all sessions for current user
- `createSession(title?)` — start a new chat session
- `loadSession(id)` — load a session with its message history
- `sendMessage(content)` — sends message to current session, appends response
- `deleteSession(id)` — removes a session
- `archiveSession(id)` — archives a session

**Hook**: `useChatContext()`

---

### `NotificationContext` (`contexts/NotificationContext.jsx`)

**State**: `notifications`, `unreadCount`

**Behaviour**: Polls `GET /api/notifications/unread-count/` every **30 seconds**. Refreshes full notification list when count changes. Unread count badge displayed in `DashboardLayout` top nav.

**Methods**:
- `markRead(id)` — marks one notification as read
- `markAllRead()` — marks all as read
- `refreshNotifications()` — manual refresh

**Hook**: `useNotification()`

---

## API Services Layer

`services/endpoints.js` — all API functions organized as service objects.

| Service | Key Methods |
|---------|------------|
| `authService` | `login`, `register`, `logout`, `getMe`, `refreshToken` |
| `profileService` | `getStudentProfile`, `updateStudentProfile`, `getMentorProfile`, `updateMentorProfile` |
| `assessmentService` | `getAssessments`, `getAssessment`, `submitAssessment`, `getMyAttempts` |
| `taskService` | `getRecommendedTasks`, `getMyTasks`, `acceptTask`, `updateAssignment`, `completeTask`, `getTaskMCQ`, `submitMCQ`, `getEvaluation`, `mentorEvaluateTask` |
| `mentorService` | `getStudents`, `getPendingReviews`, `getReviewHistory`, `createTask`, `assignStudent`, `unassignStudent`, `getAvailableStudents` |
| `adminService` | `getStats`, `getUsers`, `createUser`, `updateUser`, `deleteUser`, `resetPassword`, `autoAssignMentors` |
| `analyticsService` | `getStudentAnalytics`, `getMentorAnalytics`, `getAdminAnalytics`, `getDomainPrediction` |
| `notificationService` | `getNotifications`, `getUnreadCount`, `markRead`, `markAllRead` |
| `announcementService` | `getAnnouncements`, `createAnnouncement`, `deleteAnnouncement` |
| `directMessageService` | `getMessages`, `sendMessage`, `markAllRead` |
| `portfolioService` | `getMyPortfolio`, `getPortfolio`, `getPortfolioStats` |
| `chatService` | `getSessions`, `createSession`, `getSession`, `sendMessage`, `deleteSession`, `archiveSession` |

All functions return Axios promise responses. Error handling is done via try/catch in components or via the global Axios interceptor.

---

## Pages Reference

### Auth & Landing

| Page | Path | Description |
|------|------|-------------|
| `LandingPage` | `/` | Public landing page with feature overview |
| `LoginPage` | `/login` | Email + password login form; includes Google Sign-In button |
| `RegisterPage` | `/register` | Registration with role selection; includes Google Sign-In button |
| `GoogleOnboardingPage` | `/google-onboarding` | Role selection for new Google OAuth users (`onboarding_complete=False`) |
| `EmailVerificationPage` | `/verify-email` | Enter/paste email verification token |
| `ForgotPasswordPage` | `/forgot-password` | Enter email to request reset token |
| `ResetPasswordPage` | `/reset-password` | Enter token + new password |

### Student Pages

| Page | Path | Description |
|------|------|-------------|
| `StudentDashboard` | `/student/dashboard` | Overview: stats, recent activity, quick links |
| `StudentAnalyticsDashboard` | `/student/analytics` | Domain scores, skill trends, cluster info |
| `AssessmentList` | `/student/assessments` | All available assessments |
| `TakeAssessment` | `/student/assessments/:id` | MCQ assessment form |
| `AssessmentResult` | `/student/assessments/:id/result` | Score + NLP feedback |
| `AssessmentResultEnhanced` | `/student/assessments/:id/result-enhanced` | Detailed concept breakdown |
| `RecommendedTasksPage` | `/student/tasks/recommended` | ML-ranked task cards |
| `MyTasksPage` | `/student/tasks/my-tasks` | Student's task assignments |
| `TaskCompletionPage` | `/student/tasks/:id/complete` | Submit reflective text |
| `TaskMCQQuizPage` | `/student/tasks/:id/mcq` | Per-task MCQ quiz |
| `TaskEvaluationResultPage` | `/student/tasks/:id/evaluation` | View final evaluation result |
| `PortfolioPage` | `/student/portfolio` | Portfolio with item cards |
| `PortfolioItemDetailPage` | `/student/portfolio/:id` | Single portfolio item detail |
| `StudentSettingsPage` | `/student/settings` | Profile settings + profile picture upload |
| `NotificationsPage` | `/student/notifications` | In-app notifications with read/unread state |
| `ChatPage` | `/student/chat` | AI chatbot full page |
| `AnnouncementsPage` | `/student/announcements` | Platform announcements |
| `DirectChatPage` | `/student/messages` | 1-to-1 message thread with mentor |

### Mentor Pages

| Page | Path | Description |
|------|------|-------------|
| `MentorDashboard` | `/mentor/dashboard` | Overview + recent evaluations panel |
| `MentorAnalyticsDashboard` | `/mentor/analytics` | Student clusters, domain stats, AI insights |
| `MentorAssignedStudentsPage` | `/mentor/students` | All assigned students with progress |
| `MentorStudentDetailPage` | `/mentor/students/:id` | Individual student detail + portfolio |
| `MentorPendingReviewsPage` | `/mentor/reviews` | Tasks awaiting mentor evaluation |
| `MentorReviewTaskPage` | `/mentor/reviews/:id` | Full review form with score slider |
| `MentorSelectStudentsPage` | `/mentor/select-students` | Assign/unassign students |
| `MentorTasksPage` | `/mentor/tasks` | All tasks (view/manage) |
| `MentorCreateTaskPage` | `/mentor/tasks/create` | Create new task |
| `MentorTaskMCQPage` | `/mentor/tasks/:id/mcq` | Manage task MCQ questions |
| `MentorSettingsPage` | `/mentor/settings` | Mentor profile settings + profile picture upload |
| `NotificationsPage` | `/mentor/notifications` | In-app notifications |
| `MentorChatPage` | `/mentor/chat` | Mentor AI assistant |
| `AnnouncementsPage` | `/mentor/announcements` | Announcements (mentor view) |

### Admin Pages

| Page | Path | Description |
|------|------|-------------|
| `AdminDashboard` | `/admin/dashboard` | System stats + quick actions |
| `AdminAnalyticsDashboard` | `/admin/analytics` | System-wide analytics |
| `AdminUsersPage` | `/admin/users` | User management table |
| `AdminAssessmentsPage` | `/admin/assessments` | Assessment management |
| `AdminTasksPage` | `/admin/tasks` | Task management |
| `AnnouncementsPage` | `/admin/announcements` | Create/delete announcements |

---

## Components Reference

| Component | Description |
|-----------|-------------|
| `DashboardLayout` | Main layout wrapper — sidebar + top nav + unread notification badge |
| `Sidebar` | Navigation sidebar; role-aware (different items per Student/Mentor/Admin) |
| `ProtectedRoute` | Route guard — checks `AuthContext.user` exists and `user.role` matches |
| `TaskCard` | Task card with title, domain, difficulty, ML recommendation score + match reason |
| `CardComponents` | Assessment card, stats card, score card reusable UI |
| `ProgressAndUtilityComponents` | Progress bars, skill badges, cluster tier badges, spinner |
| `DataTable` | Reusable sortable/filterable data table |
| `StudentProfileCard` | Student info card with KMeans cluster badge |
| `MentorProfileCard` | Mentor info card with expertise domain tags |
| `ChatWidget` | Minimizable floating chat widget (overlays all pages) |
| `FloatingChatButton` | Persistent floating button to open/close the chat widget |
| `ChatMessage` | Single chat message bubble (user vs assistant styling) |
| `ConfirmModal` | Reusable confirmation dialog |

**Profile Picture in DashboardLayout:**
- Top nav shows profile picture (`user.profile_picture_url`) with `onError` fallback to letter avatar
- Both the `<img>` and letter-avatar `<div>` are always in the DOM; toggled via `display` style
- Prevents broken image icons if the URL is unavailable

---

## Styling Conventions

- **Tailwind CSS** utility classes used exclusively — no custom CSS files
- **Color palette**: Indigo/blue primary, emerald/green for success, amber/yellow for warnings, red for errors
- **Responsive**: All dashboards use Tailwind responsive prefixes (`md:`, `lg:`, `xl:`)
- **Dark mode**: Not implemented in current version
- **Toast notifications**: All user feedback uses `react-toastify` — `ToastContainer` is in `main.jsx`

---

## Environment & Build

`vite.config.js` configures the dev server proxy:

```js
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

For production, set `VITE_API_BASE_URL` in a `.env.production` file and configure `api.js` to use it:

```env
VITE_API_BASE_URL=https://your-backend-domain.com
```

The production build output (`npm run build`) generates static files in `dist/` which can be served by any static host (Netlify, Vercel, Nginx, etc.).

### Google OAuth Setup

Add `VITE_GOOGLE_CLIENT_ID` to your environment:

```env
# frontend/.env.local (development)
VITE_GOOGLE_CLIENT_ID=276821512866-xxxx.apps.googleusercontent.com
```

In `main.jsx` the app is wrapped with `GoogleOAuthProvider`:
```jsx
<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
  <App />
</GoogleOAuthProvider>
```

In production the client ID is passed as a Docker build argument:
```bash
VITE_GOOGLE_CLIENT_ID=<your_client_id> docker compose up -d --build
```

### Axios FormData Handling

Profile picture uploads use `multipart/form-data`. The Axios interceptor in `api.js` detects `FormData` and deliberately **omits** the `Content-Type` header so the browser sets the correct `multipart/form-data; boundary=...` automatically:

```js
if (config.data instanceof FormData) {
  config.headers['Content-Type'] = undefined;  // let browser set boundary
} else {
  config.headers['Content-Type'] = 'application/json';
}
```

Do **not** set a default `Content-Type` in the Axios instance — doing so overrides the multipart boundary and causes the backend to reject the upload.
