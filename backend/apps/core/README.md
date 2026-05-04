# core — Shared Permissions & Exception Handling

The `core` app provides shared infrastructure used across all other Django apps. It contains no models or URLs — only reusable utilities.

---

## Contents

1. [Permission Classes](#permission-classes)
2. [Custom Exception Handler](#custom-exception-handler)

---

## Permission Classes

`apps/core/permissions.py`

Three custom DRF permission classes for role-based access control:

### `IsStudent`

```python
from apps.core.permissions import IsStudent
permission_classes = [IsAuthenticated, IsStudent]
```

Passes if `request.user.role == 'student'`.

---

### `IsMentor`

```python
from apps.core.permissions import IsMentor
permission_classes = [IsAuthenticated, IsMentor]
```

Passes if `request.user.role == 'mentor'`.

---

### `IsAdmin`

```python
from apps.core.permissions import IsAdmin
permission_classes = [IsAuthenticated, IsAdmin]
```

Passes if `request.user.role == 'admin'` **or** `request.user.is_staff == True`.  
This allows Django superusers to access admin endpoints.

---

### Usage Pattern

All views use standard DRF `permission_classes`:

```python
class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    ...

class MentorEvaluateTaskView(APIView):
    permission_classes = [IsAuthenticated, IsMentor]
    ...

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    ...
```

---

## Custom Exception Handler

`apps/core/exceptions.py`

Overrides Django REST Framework's default exception handler to enforce the platform-wide response envelope format.

### Standard DRF Response (before)

```json
{ "detail": "Authentication credentials were not provided." }
```

### Custom Response (after)

```json
{
  "success": false,
  "error": {
    "code": 401,
    "message": "Authentication credentials were not provided."
  }
}
```

### Registered In Settings

```python
# config/settings.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    ...
}
```

This ensures all error responses across every app follow the same `{ success, error }` structure, making frontend error handling uniform.
