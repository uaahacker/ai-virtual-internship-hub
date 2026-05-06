# notifications — Notifications, Announcements & Direct Messages

The `notifications` app delivers three types of in-app communication:

1. **Notifications** — system-generated alerts triggered by platform events (evaluation complete, task assigned, etc.)
2. **Announcements** — broadcast messages from admin/mentors to all users, students only, or mentors only
3. **Direct Messages** — 1-to-1 messages between students and their assigned mentor

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Notification Flow](#notification-flow)
4. [Announcement Broadcasting](#announcement-broadcasting)
5. [Direct Messages](#direct-messages)

---

## Models

### `Notification`

System-generated per-user notification.

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey → User | Recipient |
| `title` | CharField | Short heading |
| `message` | TextField | Full notification text |
| `notification_type` | CharField | `task_assigned` / `evaluation_complete` / `announcement` / `message` / `system` |
| `is_read` | BooleanField | Default False |
| `created_at` | DateTimeField | |
| `related_object_id` | IntegerField (nullable) | FK to related object (task, evaluation, etc.) |
| `related_object_type` | CharField (nullable) | Model name for the related object |

---

### `Announcement`

Admin or mentor broadcast message.

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField | |
| `content` | TextField | Announcement body |
| `created_by` | ForeignKey → User | Admin or Mentor who created it |
| `target_audience` | CharField | `all` / `students` / `mentors` |
| `is_active` | BooleanField | Inactive announcements hidden from feed |
| `created_at` | DateTimeField | |
| `expires_at` | DateTimeField (nullable) | Optional expiry |

---

### `DirectMessage`

1-to-1 message between a student and their assigned mentor.

| Field | Type | Notes |
|-------|------|-------|
| `sender` | ForeignKey → User | `related_name='sent_messages'` |
| `recipient` | ForeignKey → User | `related_name='received_messages'` |
| `content` | TextField | Message body |
| `is_read` | BooleanField | Default False |
| `sent_at` | DateTimeField | Auto-set |

---

## URL Reference

All URLs prefixed with `/api/notifications/`.

### Notifications

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/` | Authenticated | List notifications for current user |
| POST | `/read/:id/` | Authenticated | Mark one notification as read |
| POST | `/read-all/` | Authenticated | Mark all notifications as read |
| GET | `/unread-count/` | Authenticated | Get count of unread notifications |

### Announcements

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/announcements/` | Authenticated | List announcements for current user's audience |
| POST | `/announcements/create/` | Admin / Mentor | Create new announcement |
| DELETE | `/announcements/:id/delete/` | Admin | Delete announcement |

### Direct Messages

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/messages/` | Authenticated | List DM thread with assigned mentor/student |
| POST | `/messages/send/` | Authenticated | Send a message |
| POST | `/messages/read-all/` | Authenticated | Mark all incoming DMs as read |

---

## Notification Flow

Notifications are created programmatically by other apps when events occur:

| Event | Notification created for |
|-------|--------------------------|
| Task evaluation completed | Student (result ready) |
| New task assigned by mentor | Student |
| New announcement | All targeted users |
| Direct message received | Recipient |

**Frontend polling**: `NotificationContext.jsx` polls `GET /api/notifications/unread-count/` every **30 seconds** and refreshes the notification list when the count changes. `DashboardLayout.jsx` subscribes to the context to display an unread count badge on the Notifications sidebar link.

---

## Announcement Broadcasting

When an announcement is created with `target_audience`:

- `all` — shown to all authenticated users
- `students` — shown only to users with `role='student'`
- `mentors` — shown only to users with `role='mentor'`

The filter is applied at query time (no fan-out to individual Notification records — announcements are stored once and filtered on read).

---

## Direct Messages

DMs are scoped to the mentor–student relationship:
- A student can only message their **assigned mentor** (from `StudentProfile.mentor`)
- A mentor can message any of their **assigned students**
- The frontend DM page fetches the full thread sorted by `sent_at`
- Unread count for DMs is separate from notification unread count
