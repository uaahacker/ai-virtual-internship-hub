# 📋 PostgreSQL Setup - Quick Reference Card

## 🚀 TL;DR - 5 Minute Setup

### 1. Install PostgreSQL
- **Download:** https://www.postgresql.org/download/
- **Install:** Keep default port 5432
- **Note:** Remember postgres password

### 2. Create Database
```bash
psql -U postgres
CREATE DATABASE virtual_internship_hub;
\q
```

### 3. Update .env
```
DB_NAME=virtual_internship_hub
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Run Migrations & Seed Data
```bash
cd backend
python manage.py migrate
python manage.py seed_assessments
python manage.py seed_tasks

# Download NLTK data (for NLP text evaluation)
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

### 5. Start Server
```bash
python manage.py runserver
```

---

## ✅ Validation Command
```bash
python validate_migration.py
```

---

## 🧪 Test Endpoints

```bash
# Test API is running
curl http://localhost:8000/api/

# Test assessments
curl http://localhost:8000/api/assessments/

# Test login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

---

## 📱 Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

---

## 🐛 Quick Troubleshoot

| Problem | Solution |
|---------|----------|
| "password authentication failed" | Check .env passwords match |
| "ECONNREFUSED" on port 5432 | Start PostgreSQL service |
| "database does not exist" | Create with: `CREATE DATABASE virtual_internship_hub;` |
| "relation does not exist" | Run: `python manage.py migrate` |
| "psycopg2 not found" | Run: `pip install psycopg2-binary` |

---

## 🔄 Database Commands

```bash
# Connect to database
psql -U postgres -d virtual_internship_hub

# List tables
\dt

# List databases
\l

# Change password
ALTER USER postgres PASSWORD 'newpass';

# Exit
\q
```

---

## 🎯 Status

✅ Code migration complete  
✅ All validations passed  
✅ Ready for PostgreSQL deployment  

⏭️ Next: Install PostgreSQL and run migrations

---

**For detailed guide:** See `MIGRATION_COMPLETE.md`  
**For full documentation:** See `MONGODB_TO_POSTGRESQL_MIGRATION.md`
