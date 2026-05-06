# Complete Production Deployment Guide
## VIHub — vihub.site — Contabo VPS (8GB RAM, 75GB NVMe, Docker)

This guide takes you from zero to a fully running production deployment — step by step.

---

## Overview

What will be running after this guide:

```
Internet
    │
    ▼ Port 80 (HTTP → redirected to HTTPS)
    ▼ Port 443 (HTTPS)
┌──────────────────────────────────┐
│  Nginx container  (vihub_nginx)  │
│  ● Serves React SPA (/)          │
│  ● Proxies /api/ → Django        │
│  ● Proxies /django-admin/ → Django│
│  ● Serves /static/ (admin CSS)   │
└──────────────┬───────────────────┘
               │ internal Docker network
┌──────────────▼───────────────────┐
│  Django + Gunicorn  (vihub_backend)│
│  Port 8000 (internal only)       │
└──────────────┬───────────────────┘
               │
┌──────────────▼───────────────────┐
│  PostgreSQL 16  (vihub_db)       │
│  Port 5432 (internal only)       │
└──────────────────────────────────┘
```

---

## PHASE 1 — Local Machine: Prepare & Push

Do this on your Windows PC before touching the VPS.

### Step 1 — Generate a Django Secret Key

Run this in PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Copy the output — you will use it as `DJANGO_SECRET_KEY` in Step 7.

### Step 2 — Commit and push all deployment files to GitHub

```powershell
cd D:\FYP\finalcode\fyp

git add .
git status
git commit -m "chore: add Docker production deployment files"
git push origin master
```

Verify on GitHub (https://github.com/uaahacker/fyp) that these files are present:
- `docker-compose.yml`
- `backend/Dockerfile`
- `backend/entrypoint.sh`
- `backend/.env.example`
- `nginx/Dockerfile`
- `nginx/conf.d/vihub.conf`
- `nginx/conf.d/vihub-ssl.conf`

---

## PHASE 2 — DNS Setup (do this BEFORE SSL)

Log into your domain registrar (wherever you bought vihub.site).

Add these DNS records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | Your VPS IP address | 300 |
| A | `www` | Your VPS IP address | 300 |

**Find your VPS IP:** It was shown in your Contabo welcome email, or log into Contabo panel.

Wait 5–15 minutes for DNS to propagate before running certbot.

Verify DNS:
```
ping vihub.site
```
It should resolve to your VPS IP.

---

## PHASE 3 — VPS First-Time Setup

SSH into your VPS:
```bash
ssh root@YOUR_VPS_IP
```

### Step 3 — Update the system

```bash
apt-get update && apt-get upgrade -y
```

### Step 4 — Install Git (if not already)

```bash
apt-get install -y git curl
```

Verify:
```bash
git --version
docker --version
```

### Step 5 — Clone your GitHub repository

```bash
cd /opt
git clone https://github.com/uaahacker/fyp.git vihub
cd /opt/vihub
```

From now on, your project lives at `/opt/vihub`.

---

## PHASE 4 — Configure Environment

### Step 6 — Create the backend .env file

```bash
cd /opt/vihub/backend
cp .env.example .env
nano .env
```

Fill in these values (press `Ctrl+X`, then `Y`, then `Enter` to save):

```env
# Django Core
DJANGO_SECRET_KEY=PASTE_YOUR_SECRET_KEY_FROM_STEP_1_HERE
DEBUG=False
ALLOWED_HOSTS=vihub.site,www.vihub.site

# Database
DB_NAME=vihub_db
DB_USER=vihub_user
DB_PASSWORD=CHOOSE_A_STRONG_PASSWORD_HERE
DB_HOST=db
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://vihub.site,https://www.vihub.site

# JWT
JWT_ACCESS_LIFETIME_MINUTES=60
JWT_REFRESH_LIFETIME_DAYS=7

# CSRF
CSRF_TRUSTED_ORIGINS=https://vihub.site,https://www.vihub.site

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Chatbot LLM (OpenRouter — used in production)
OPENROUTER_API_KEY=sk-or-...

# Site URL for chatbot HTTP-Referer header
SITE_URL=https://vihub.site

# Legacy optional keys (if switching providers)
# OPENAI_API_KEY=
# GEMINI_API_KEY=
```

**IMPORTANT:** Use the same `DB_PASSWORD` value — remember it for the next steps.

---

## PHASE 5 — First Deployment (HTTP, no SSL yet)

### Step 7 — Build and start all containers

```bash
cd /opt/vihub

# Build all images and start in background
docker compose up -d --build
```

This will take 3–8 minutes the first time (downloading images, installing Python packages, building React app).

### Step 8 — Check all containers are running

```bash
docker compose ps
```

Expected output:
```
NAME              STATUS
vihub_db          Up (healthy)
vihub_backend     Up
vihub_nginx       Up
vihub_certbot     Up
```

If any container shows `Exit` status, check its logs:
```bash
docker compose logs backend
docker compose logs nginx
docker compose logs db
```

### Step 9 — Test the site (HTTP)

Open in your browser:
```
http://vihub.site
```

You should see the React frontend loading.

Test the API:
```
http://vihub.site/api/auth/me/
```
Should return a 401 JSON response (not an nginx error) — this means the backend is reachable.

---

## PHASE 6 — SSL Certificate (Let's Encrypt / HTTPS)

### Step 10 — Obtain SSL certificate

```bash
cd /opt/vihub

docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d vihub.site \
  -d www.vihub.site
```

Replace `your-email@gmail.com` with your actual email.

If successful, you will see:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/vihub.site/fullchain.pem
```

### Step 11 — Switch nginx to HTTPS config

```bash
# Copy the SSL nginx config over the HTTP one
cp /opt/vihub/nginx/conf.d/vihub-ssl.conf /opt/vihub/nginx/conf.d/vihub.conf
```

Now rebuild the nginx container to bake in the new config:
```bash
cd /opt/vihub
docker compose up -d --build nginx
```

### Step 12 — Test HTTPS

Open in browser:
```
https://vihub.site
```

You should see a padlock + the React app. HTTP should auto-redirect to HTTPS.

SSL certificates auto-renew every 12 hours via the certbot container (only renews when <30 days left).

---

## PHASE 7 — Post-Deployment: Create Admin & Seed Data

All commands below run inside the backend container.

### Step 13 — Create the admin user

```bash
docker compose exec backend python manage.py create_admin
```

Follow the prompts:
```
Email: admin@vihub.site
First name: Admin
Last name: VIHub
Password: (choose strong password)
```

### Step 14 — Seed assessment questions and tasks

```bash
docker compose exec backend python manage.py seed_assessments
docker compose exec backend python manage.py seed_tasks
```

`seed_assessments` creates 10 domain MCQ assessments. `seed_tasks` creates sample tasks for all domains so students have tasks to accept immediately after registration.

This creates 10 domain assessments (Web Dev, Graphic Design, Content Writing, Digital Marketing, Video Editing, Data Analysis, Mobile Dev, UI/UX, Cybersecurity, Cloud Computing) with multiple MCQ questions each.

### Step 15 — Train the ML domain prediction model

```bash
docker compose exec backend python manage.py train_domain_model
```

This trains the RandomForest domain predictor with synthetic seed data (so it works even with 0 real students). Saves model to `ml_models/domain_predictor.pkl`.

### Step 16 — Download NLTK data (for NLP feedback)

```bash
docker compose exec backend python -c "
import nltk
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
print('NLTK data downloaded successfully')
"
```

---

## PHASE 8 — Create Real Users, Tasks, Quizzes

### Step 17 — Create student and mentor users via API

Use curl or your browser DevTools / Postman to hit the API.

**Create a mentor:**
```bash
curl -X POST https://vihub.site/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mentor@vihub.site",
    "password": "Mentor@12345",
    "first_name": "Sarah",
    "last_name": "Khan",
    "role": "mentor"
  }'
```

**Create a student:**
```bash
curl -X POST https://vihub.site/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@vihub.site",
    "password": "Student@12345",
    "first_name": "Ali",
    "last_name": "Ahmed",
    "role": "student"
  }'
```

**Get auth token (for admin):**
```bash
curl -X POST https://vihub.site/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vihub.site",
    "password": "YOUR_ADMIN_PASSWORD"
  }'
```
Save the `access` token from the response.

### Step 18 — Auto-assign students to mentors (admin action)

```bash
# First get the admin token
TOKEN="PASTE_ACCESS_TOKEN_HERE"

curl -X POST https://vihub.site/api/auth/mentor/auto-assign/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Step 19 — Create tasks with MCQ questions

**Step 19a — Get mentor token:**
```bash
curl -X POST https://vihub.site/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "mentor1@vihub.site", "password": "Mentor@12345"}'
```

**Step 19b — Create a task:**
```bash
MENTOR_TOKEN="PASTE_MENTOR_TOKEN"

curl -X POST https://vihub.site/api/tasks/mentor/create/ \
  -H "Authorization: Bearer $MENTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a Personal Portfolio Website",
    "description": "Create a responsive portfolio website using HTML, CSS, and JavaScript. Include sections for About Me, Skills, Projects, and Contact. The site should be mobile-friendly and use modern CSS Grid/Flexbox layout.",
    "domain": "Web Development",
    "difficulty": "beginner",
    "estimated_duration": 300,
    "skills_required": ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Git"],
    "learning_outcomes": ["Build responsive layouts", "Use CSS Grid and Flexbox", "Deploy a static website", "Version control with Git"],
    "prerequisites": ["Basic HTML knowledge", "Basic CSS knowledge"]
  }'
```
Save the task `id` from the response.

**Step 19c — Add MCQ questions to the task:**
```bash
TASK_ID=1   # Replace with the actual task ID from above

curl -X POST https://vihub.site/api/tasks/mentor/$TASK_ID/mcq/add/ \
  -H "Authorization: Bearer $MENTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Which CSS property is used to create a flexible container?",
    "option_a": "display: flex",
    "option_b": "display: block",
    "option_c": "display: grid",
    "option_d": "display: inline",
    "correct_answer": "a",
    "concept": "CSS Flexbox",
    "difficulty_weight": 1.0
  }'

curl -X POST https://vihub.site/api/tasks/mentor/$TASK_ID/mcq/add/ \
  -H "Authorization: Bearer $MENTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What does the viewport meta tag do in a responsive website?",
    "option_a": "Sets the page background color",
    "option_b": "Controls how the page scales on mobile devices",
    "option_c": "Loads external JavaScript files",
    "option_d": "Defines the page title",
    "correct_answer": "b",
    "concept": "Responsive Design",
    "difficulty_weight": 1.2
  }'

curl -X POST https://vihub.site/api/tasks/mentor/$TASK_ID/mcq/add/ \
  -H "Authorization: Bearer $MENTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Which HTML element is used to link an external CSS file?",
    "option_a": "<script>",
    "option_b": "<style>",
    "option_c": "<link>",
    "option_d": "<css>",
    "correct_answer": "c",
    "concept": "HTML5",
    "difficulty_weight": 0.8
  }'
```

Repeat Step 19b and 19c to create more tasks for other domains.

### Step 20 — Use the Django Admin Panel

Go to: `https://vihub.site/django-admin/`

Log in with your admin credentials. From here you can:
- Create/edit/delete users
- Manage assessments and questions
- View all task assignments and evaluations
- Inspect all database tables

---

## PHASE 9 — Git Workflow (Updating the App)

### Daily workflow on your local machine

```powershell
# On your local Windows machine

# 1. Make your code changes

# 2. Stage and commit
git add .
git commit -m "feat: describe what you changed"

# 3. Push to GitHub
git push origin master
```

### Pulling updates on the VPS

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP
cd /opt/vihub

# 1. Pull latest code
git pull origin master

# 2. Rebuild and restart (only rebuilds changed layers — fast)
docker compose up -d --build

# Done. The backend auto-applies migrations on startup.
```

### If you only changed frontend code

```bash
# Only rebuild nginx (which builds React inside it)
docker compose up -d --build nginx
```

### If you only changed backend code (no new dependencies)

```bash
# Only rebuild backend
docker compose up -d --build backend
```

### If you added new Python packages

```bash
# Rebuild backend (pip install will run)
docker compose up -d --build backend
```

### Checking logs after an update

```bash
# All services live
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f db
```

---

## PHASE 10 — Useful Management Commands

### Run any Django management command

```bash
docker compose exec backend python manage.py COMMAND
```

| Task | Command |
|------|---------|
| Create admin user | `docker compose exec backend python manage.py create_admin` |
| Reset admin password | `docker compose exec backend python manage.py reset_admin` |
| Seed assessments | `docker compose exec backend python manage.py seed_assessments` |
| Seed tasks | `docker compose exec backend python manage.py seed_tasks` |
| Train ML model | `docker compose exec backend python manage.py train_domain_model` |
| Train ML (real data only) | `docker compose exec backend python manage.py train_domain_model --no-seed` |
| Check ML model info | `docker compose exec backend python manage.py train_domain_model --info` |
| Run migrations | `docker compose exec backend python manage.py migrate` |
| Open Django shell | `docker compose exec backend python manage.py shell` |
| Create superuser | `docker compose exec backend python manage.py createsuperuser` |

### Database operations

```bash
# Open PostgreSQL prompt
docker compose exec db psql -U vihub_user -d vihub_db

# Backup database
docker compose exec db pg_dump -U vihub_user vihub_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database from backup
cat backup_20260505_120000.sql | docker compose exec -T db psql -U vihub_user -d vihub_db
```

### Container operations

```bash
# Start everything
docker compose up -d

# Stop everything (keeps data)
docker compose down

# Stop everything AND delete volumes (DESTROYS all data)
docker compose down -v

# Restart a single service
docker compose restart backend

# View resource usage
docker stats

# List all images
docker images

# Clean up unused images (free disk space)
docker image prune -f
```

---

## PHASE 11 — Renewing SSL

SSL auto-renews via the certbot container. To force-renew manually:

```bash
docker compose run --rm certbot renew --force-renewal
docker compose restart nginx
```

---

## PHASE 12 — Monitoring & Troubleshooting

### Container not starting?

```bash
docker compose logs backend   # Check Python/Django errors
docker compose logs nginx     # Check nginx config errors
docker compose logs db        # Check PostgreSQL errors
```

### Backend 500 errors?

```bash
docker compose exec backend python manage.py check
docker compose logs -f backend
```

### Database connection refused?

```bash
# Check DB is healthy
docker compose ps db

# Test connection from backend container
docker compose exec backend python -c "
import psycopg2, os
conn = psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
)
print('DB connection OK')
conn.close()
"
```

### Nginx 502 Bad Gateway?

The backend container isn't running or crashed. Check:
```bash
docker compose ps
docker compose logs backend
```

### Site not loading (DNS issue)?

```bash
# From VPS
curl -I http://vihub.site

# Check nginx is listening
docker compose ps nginx

# Check ports are open
ss -tlnp | grep -E '80|443'
```

### Reset everything and redeploy

```bash
cd /opt/vihub

# Stop and remove containers (keeps volumes/data)
docker compose down

# Pull latest code
git pull origin master

# Rebuild from scratch
docker compose up -d --build
```

---

## Full File Structure After Deployment

```
/opt/vihub/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── .env                    ← YOUR SECRETS (not in git)
│   ├── .env.example            ← Template (in git)
│   └── ...
├── frontend/
│   └── ...
└── nginx/
    ├── Dockerfile
    ├── conf.d/
    │   ├── vihub.conf          ← Active nginx config
    │   └── vihub-ssl.conf      ← SSL template
    └── certbot/
        ├── conf/               ← SSL certificates (auto-created)
        └── www/                ← ACME challenge files (auto-created)
```

---

## Quick Reference Card

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Navigate to project
cd /opt/vihub

# Update from GitHub and restart
git pull origin master && docker compose up -d --build

# Check status
docker compose ps

# View live logs
docker compose logs -f

# Create admin
docker compose exec backend python manage.py create_admin

# Open Django shell
docker compose exec backend python manage.py shell

# Database backup
docker compose exec db pg_dump -U vihub_user vihub_db > backup.sql

# Restart all
docker compose restart

# Stop all
docker compose down
```

---

## Security Checklist

- [x] `DEBUG=False` in production `.env`
- [x] Strong `DJANGO_SECRET_KEY` (50+ chars, random)
- [x] Strong `DB_PASSWORD`
- [x] HTTPS enforced (HTTP redirects to HTTPS)
- [x] `SESSION_COOKIE_SECURE=True`
- [x] `CSRF_COOKIE_SECURE=True`
- [x] HSTS enabled
- [x] PostgreSQL port not exposed to internet (internal Docker network only)
- [x] Gunicorn port not exposed to internet (internal Docker network only)
- [ ] Consider firewall rules: `ufw allow 22,80,443/tcp && ufw enable`
- [ ] Consider fail2ban for SSH brute-force protection
