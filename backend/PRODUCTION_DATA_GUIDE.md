# Production Data Population Guide

## Overview
The `create_production_data.py` script populates your Virtual Internship Hub database with comprehensive, realistic test data for production deployment.

## What's Included

### 📊 Database Content
- **11 Assessments** across all domains (Graphic Design, Programming, Digital Marketing, Data Analytics, Content Writing)
- **58 Realistic MCQ Questions** with industry-level content and proper answers
- **20 Tasks** with realistic descriptions, required skills, and learning outcomes
- **4 Users** (3 students with different skill levels, 1 mentor)
- **64 Assessment Attempts** with varied scores (Beginner/Intermediate/Advanced skill levels)
- **19 Task Recommendations** personalized based on assessment performance

### 👥 Test Users
All test users use password: `password123`

| Email | Name | Role | Purpose |
|-------|------|------|---------|
| student1@example.com | Aisha Khan | Student | Advanced learner example |
| student2@example.com | Alex Rodriguez | Student | Intermediate learner example |
| student3@example.com | Priya Patel | Student | Diverse skill portfolio |
| mentor@example.com | Dr. Sarah Chen | Mentor | Can assign tasks & mentor |

### 📚 Assessment Topics

#### Graphic Design (2 assessments)
- Graphic Design Fundamentals
- UI/UX Design Principles

#### Programming (3 assessments)
- Python Programming Essentials
- Web Development Basics
- Python Programming Basics

#### Digital Marketing (2 assessments)
- Digital Marketing Strategy
- Social Media Marketing

#### Data Analytics (1 assessment)
- Data Analytics Fundamentals

#### Content Writing (1 assessment)
- Content Writing & SEO

### 🎯 Task Types
- **Design Tasks**: Logo design, UI mockups, infographics
- **Development Tasks**: Web scraper, Django e-commerce, React frontend
- **Marketing Tasks**: Social media campaigns, SEO audit, competitor analysis
- **Content Tasks**: Blog posts, video content, email campaigns
- **Analytics Tasks**: Dashboards, database design, data analysis

## Deployment Instructions

### Option 1: Using Django Shell (Recommended)
```bash
cd backend
python manage.py shell < create_production_data.py
```

### Option 2: Direct Script Execution
```bash
cd backend
python create_production_data.py
```

### Step-by-Step Deployment

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Ensure database is ready:**
   ```bash
   python manage.py migrate
   ```

3. **Run the data population script:**
   ```bash
   python create_production_data.py
   ```

4. **Verify data was populated:**
   ```bash
   python manage.py shell
   >>> from apps.assessments.models import Assessment, Question
   >>> print(f"Assessments: {Assessment.objects.count()}")
   >>> print(f"Questions: {Question.objects.count()}")
   >>> exit()
   ```

5. **Start your servers:**
   ```bash
   # Backend (in one terminal)
   python manage.py runserver
   
   # Frontend (in another terminal)
   cd ../frontend
   npm run dev
   ```

6. **Test the application:**
   - Navigate to http://localhost:5174
   - Click "Login" or go to login page
   - Use any test user credentials from above

## Testing Workflows

### Test Student Progression
1. Login as `student1@example.com` (password: `password123`)
2. Go to **Assessments** tab
3. Take various assessments and see different score results
4. Go to **Recommended** tab to see personalized task recommendations
5. View **Analytics** to see performance insights
6. Use **Chat** for learning assistance

### Test Multiple Students
Each test user has different assessment results and recommendations:
- **Aisha Khan**: Strong in design and content, various skill levels
- **Alex Rodriguez**: Mixed performance across domains
- **Priya Patel**: Advanced in some areas, beginner in others

### Test Mentor Features
1. Login as `mentor@example.com`
2. View student analytics and assignments
3. See task recommendations made to students

## Data Characteristics

### Realistic Assessment Scores
- Scores range from 20% to 100%
- Multiple attempts per assessment per student
- Skill levels automatically determined:
  - **Beginner**: 0-69%
  - **Intermediate**: 70-84%
  - **Advanced**: 85-100%

### Dynamic Recommendations
- Tasks recommended based on assessment domain
- Difficulty levels match student skill level
- Each student has 3-5 personalized recommendations

### Rich Task Descriptions
Each task includes:
- Realistic, detailed description
- Required skills (2-4 per task)
- Learning outcomes (3 per task)
- Estimated duration in minutes
- Appropriate difficulty level

## Customization

To modify the test data before running:

### Add More Students
Edit the `users_data` list in the script:
```python
users_data = [
    {
        'email': 'newstudent@example.com',
        'name': 'New Student Name',
        'password': 'password123',
        'role': 'Student',
    },
    # ... add more users
]
```

### Add More Assessments
Add to the `assessments_data` list with new MCQ questions:
```python
{
    'title': 'New Assessment Title',
    'domain': 'Programming',  # Choose from: Graphic Design, Programming, Digital Marketing, Data Analytics, Content Writing
    'description': 'Description of the assessment',
    'time_limit': 45,
    'questions': [
        {
            'text': 'Question text?',
            'options': ['A) Option A', 'B) Option B', 'C) Option C', 'D) Option D'],
            'correct': 'A',
        },
        # ... add more questions
    ]
}
```

### Add More Tasks
Add to the `tasks_data` list:
```python
{
    'title': 'New Task Title',
    'domain': 'Programming',  # Match to assessment domains
    'difficulty': 'Intermediate',  # Beginner, Intermediate, or Advanced
    'task_type': 'Development',
    'description': 'Detailed task description',
    'required_skills': ['Skill 1', 'Skill 2'],
    'learning_outcomes': ['Outcome 1', 'Outcome 2'],
    'estimated_duration': 300,  # in minutes
}
```

## Resetting Data

If you need to reset and repopulate the database:

```bash
cd backend

# Option 1: Delete specific data
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from apps.assessments.models import Assessment
>>> User = get_user_model()
>>> User.objects.exclude(is_superuser=True).delete()  # Keep superuser
>>> Assessment.objects.all().delete()
>>> exit()

# Then run the population script again
python create_production_data.py

# Option 2: Full database reset (Warning: Deletes everything)
python manage.py flush  # This will prompt for confirmation
python manage.py migrate
python create_production_data.py
```

## Production Deployment Checklist

- [ ] Run database migrations: `python manage.py migrate`
- [ ] Run population script: `python create_production_data.py`
- [ ] Verify data: Check admin panel or run shell queries
- [ ] Update environment variables (if needed)
- [ ] Test login with each user type
- [ ] Verify assessments display correctly
- [ ] Check task recommendations
- [ ] Test analytics calculations
- [ ] Verify chatbot integration
- [ ] Clear browser cache and test frontend

## Troubleshooting

### Script Runs but Creates No Data
- Check that `python manage.py migrate` was run first
- Verify database connection in `.env` file
- Ensure Django settings are correct

### Import Errors
- Verify you're in the `backend` directory
- Check that Django environment is properly set up
- Run `pip install -r requirements.txt` if needed

### Database Already Has Data
- The script uses `get_or_create()`, so it won't duplicate existing data
- To force repopulation, see "Resetting Data" section above

## File Location
```
backend/
├── create_production_data.py  ← Run this for deployment data population
├── manage.py
├── requirements.txt
└── apps/
    ├── assessments/
    ├── tasks/
    ├── accounts/
    └── ...
```

## Next Steps After Deployment

1. **Verify all features work:**
   - Students can view assessments
   - Students can see recommendations
   - Analytics page displays correctly
   - Chat is responsive

2. **Monitor user activity:**
   - Track assessment completion rates
   - Monitor task recommendations acceptance
   - Track chatbot usage

3. **Gather feedback:**
   - Assessment difficulty
   - Task relevance
   - Content quality

## Support

If you encounter issues:
1. Check that all migrations are applied
2. Verify database connectivity
3. Ensure all required packages are installed
4. Check Django logs for error messages
5. Review the troubleshooting section above

---

**Created for: Virtual Internship Hub Platform**  
**Last Updated:** May 2026  
**Compatibility:** Django 4.2.30+, Python 3.8+, PostgreSQL
