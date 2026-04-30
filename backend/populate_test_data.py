#!/usr/bin/env python
"""
Management command to populate database with sample data for testing.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def populate_database():
    """Populate database with test data."""
    django.setup()
    
    from django.conf import settings
    from apps.assessments.models import Assessment, Question, AssessmentAttempt
    from apps.tasks.models import Task, TaskAssignment
    from apps.accounts.models import User
    from django.utils import timezone
    
    print("\n" + "="*60)
    print("🗄️ POPULATING DATABASE WITH TEST DATA")
    print("="*60 + "\n")
    
    # Get or create test student
    student, created = User.objects.get_or_create(
        email='student@example.com',
        defaults={
            'name': 'John Student',
            'role': 'Student',
            'is_active': True,
        }
    )
    if created:
        student.set_password('password123')
        student.save()
        print("✓ Created test student: student@example.com")
    else:
        print("✓ Using existing student: student@example.com")
    
    # Create assessments for each domain
    assessments_data = [
        {
            'title': 'Graphic Design Fundamentals',
            'domain': 'Graphic Design',
            'description': 'Test your knowledge of graphic design principles, tools, and best practices.',
            'time_limit': 30,
        },
        {
            'title': 'Python Programming Basics',
            'domain': 'Programming',
            'description': 'Assess your Python programming skills.',
            'time_limit': 45,
        },
        {
            'title': 'Digital Marketing Essentials',
            'domain': 'Digital Marketing',
            'description': 'Evaluate your digital marketing knowledge.',
            'time_limit': 30,
        },
        {
            'title': 'Content Writing Skills',
            'domain': 'Content Writing',
            'description': 'Test your content writing and copywriting abilities.',
            'time_limit': 40,
        },
        {
            'title': 'Data Analytics Fundamentals',
            'domain': 'Data Analytics',
            'description': 'Assess your data analysis and visualization skills.',
            'time_limit': 35,
        },
    ]
    
    print("\n📋 Creating Assessments...\n")
    
    for data in assessments_data:
        assessment, created = Assessment.objects.get_or_create(
            title=data['title'],
            domain=data['domain'],
            defaults={
                'description': data['description'],
                'time_limit': data['time_limit'],
                'is_active': True,
                'created_by': student,
            }
        )
        
        if created:
            print(f"  ✓ Created: {assessment.title}")
            
            # Create questions for this assessment
            questions_data = [
                {
                    'text': f'Question 1 about {data["domain"]}?',
                    'option_a': 'Option A - Correct answer',
                    'option_b': 'Option B - Wrong',
                    'option_c': 'Option C - Wrong',
                    'option_d': 'Option D - Wrong',
                    'correct_option': 'A',
                    'order': 1,
                },
                {
                    'text': f'Question 2 about {data["domain"]}?',
                    'option_a': 'Option A - Wrong',
                    'option_b': 'Option B - Correct answer',
                    'option_c': 'Option C - Wrong',
                    'option_d': 'Option D - Wrong',
                    'correct_option': 'B',
                    'order': 2,
                },
                {
                    'text': f'Question 3 about {data["domain"]}?',
                    'option_a': 'Option A - Wrong',
                    'option_b': 'Option B - Wrong',
                    'option_c': 'Option C - Correct answer',
                    'option_d': 'Option D - Wrong',
                    'correct_option': 'C',
                    'order': 3,
                },
                {
                    'text': f'Question 4 about {data["domain"]}?',
                    'option_a': 'Option A - Wrong',
                    'option_b': 'Option B - Wrong',
                    'option_c': 'Option C - Wrong',
                    'option_d': 'Option D - Correct answer',
                    'correct_option': 'D',
                    'order': 4,
                },
                {
                    'text': f'Question 5 about {data["domain"]}?',
                    'option_a': 'Option A - Correct answer',
                    'option_b': 'Option B - Wrong',
                    'option_c': 'Option C - Wrong',
                    'option_d': 'Option D - Wrong',
                    'correct_option': 'A',
                    'order': 5,
                },
            ]
            
            for q_data in questions_data:
                Question.objects.get_or_create(
                    assessment=assessment,
                    order=q_data['order'],
                    defaults=q_data
                )
            
            print(f"    └─ Added 5 questions")
        else:
            print(f"  ✓ Already exists: {assessment.title}")
    
    # Create sample tasks
    print("\n📝 Creating Tasks...\n")
    
    tasks_data = [
        {
            'title': 'Design a Logo for a Tech Startup',
            'domain': 'Graphic Design',
            'difficulty': 'Intermediate',
            'task_type': 'Design',
            'description': 'Create a modern logo design for a fictional tech startup. Include multiple variations.',
            'required_skills': ['Adobe Illustrator', 'Color Theory', 'Typography'],
            'learning_outcomes': ['Master logo design principles', 'Learn brand identity', 'Practice design tools'],
            'estimated_duration': 480,
        },
        {
            'title': 'Build a Python Web Scraper',
            'domain': 'Programming',
            'difficulty': 'Intermediate',
            'task_type': 'Development',
            'description': 'Create a web scraper using Python to collect data from a website.',
            'required_skills': ['Python', 'BeautifulSoup', 'HTTP Requests'],
            'learning_outcomes': ['Learn web scraping', 'Work with APIs', 'Data processing'],
            'estimated_duration': 360,
        },
        {
            'title': 'Create a Blog Post on Digital Marketing',
            'domain': 'Content Writing',
            'difficulty': 'Beginner',
            'task_type': 'Content',
            'description': 'Write a comprehensive blog post about digital marketing trends.',
            'required_skills': ['Writing', 'SEO', 'Content Strategy'],
            'learning_outcomes': ['Content creation', 'SEO optimization', 'Audience engagement'],
            'estimated_duration': 240,
        },
        {
            'title': 'Data Analysis Project - Sales Dashboard',
            'domain': 'Data Analytics',
            'difficulty': 'Advanced',
            'task_type': 'Analysis',
            'description': 'Analyze sales data and create an interactive dashboard.',
            'required_skills': ['Excel', 'SQL', 'Data Visualization'],
            'learning_outcomes': ['Data analysis', 'Dashboard creation', 'Business insights'],
            'estimated_duration': 600,
        },
        {
            'title': 'Instagram Marketing Campaign',
            'domain': 'Digital Marketing',
            'difficulty': 'Intermediate',
            'task_type': 'Marketing',
            'description': 'Plan and design a complete Instagram marketing campaign.',
            'required_skills': ['Social Media Marketing', 'Content Creation', 'Analytics'],
            'learning_outcomes': ['Campaign planning', 'Social media strategy', 'Engagement metrics'],
            'estimated_duration': 420,
        },
    ]
    
    for data in tasks_data:
        task, created = Task.objects.get_or_create(
            title=data['title'],
            defaults={
                'domain': data['domain'],
                'difficulty': data['difficulty'],
                'task_type': data['task_type'],
                'description': data['description'],
                'required_skills': data['required_skills'],
                'learning_outcomes': data['learning_outcomes'],
                'estimated_duration': data['estimated_duration'],
                'is_active': True,
                'created_by': student,
            }
        )
        
        if created:
            print(f"  ✓ Created: {task.title}")
        else:
            print(f"  ✓ Already exists: {task.title}")
    
    # Create task assignments (recommendations)
    print("\n🎯 Creating Task Recommendations...\n")
    
    tasks = Task.objects.all()[:5]
    for idx, task in enumerate(tasks, 1):
        assignment, created = TaskAssignment.objects.get_or_create(
            student=student,
            task=task,
            defaults={
                'status': 'recommended',
                'progress_percentage': 0,
                'assigned_by': student,
                'recommended_score': 85.0,
                'recommendation_reason': f'Recommended based on assessment results',
            }
        )
        
        if created:
            print(f"  ✓ Recommended: {task.title}")
        else:
            print(f"  ✓ Already recommended: {task.title}")
    
    # Create assessment attempts (completed assessments)
    print("\n✅ Creating Assessment Attempts (Test Results)...\n")
    
    assessments = Assessment.objects.all()
    for idx, assessment in enumerate(assessments, 1):
        attempt, created = AssessmentAttempt.objects.get_or_create(
            student=student,
            assessment=assessment,
            defaults={
                'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D', 'q5': 'A'},
                'score': 80 + (idx * 5),
                'total_questions': 5,
                'percentage': 80 + (idx * 5),
                'skill_level': 'Intermediate' if idx % 2 == 0 else 'Beginner',
                'recommended_domains': [assessment.domain],
                'attempted_at': timezone.now(),
                'strengths': ['Understanding concepts', 'Problem solving'],
                'weaknesses': ['Time management'],
                'next_steps': ['Practice more', 'Review fundamentals'],
            }
        )
        
        if created:
            print(f"  ✓ Created attempt: {assessment.title} - Score: {attempt.percentage}%")
        else:
            print(f"  ✓ Already exists: {assessment.title}")
    
    print("\n" + "="*60)
    print("✨ DATABASE POPULATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Assessments: {Assessment.objects.count()}")
    print(f"  • Questions: {Question.objects.count()}")
    print(f"  • Tasks: {Task.objects.count()}")
    print(f"  • Task Assignments: {TaskAssignment.objects.count()}")
    print(f"  • Assessment Attempts: {AssessmentAttempt.objects.count()}")
    print(f"\n👤 Test Student:")
    print(f"  • Email: student@example.com")
    print(f"  • Password: password123")
    print(f"  • Role: Student")
    print("\n✅ You can now:")
    print("  1. Login as student@example.com")
    print("  2. View assessments and take tests")
    print("  3. See recommended tasks")
    print("  4. View analytics dashboard")
    print("\n")

if __name__ == '__main__':
    populate_database()
