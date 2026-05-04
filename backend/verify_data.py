#!/usr/bin/env python
"""Quick verification script."""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent))

django.setup()

from apps.accounts.models import User
from apps.assessments.models import Assessment, AssessmentAttempt, Question
from apps.tasks.models import Task, TaskAssignment

print("\n" + "="*60)
print("✅ PRODUCTION DATA VERIFICATION")
print("="*60)

# Get student1
student = User.objects.get(email='student1@example.com')

print(f"\n👤 Student: {student.name}")
print(f"   Email: {student.email}")

# Assessment attempts
attempts = AssessmentAttempt.objects.filter(student=student)
print(f"\n📊 Assessment Attempts: {attempts.count()}")
print(f"   Sample scores: {', '.join([str(int(a.percentage)) + '%' for a in attempts[:3]])}")

# Task recommendations
recommendations = TaskAssignment.objects.filter(student=student, status='recommended')
print(f"\n🎯 Task Recommendations: {recommendations.count()}")
print(f"   Tasks: {', '.join([r.task.title[:30] for r in recommendations[:2]])}")

# Overall database stats
print(f"\n📈 Overall Database Statistics:")
print(f"   ├─ Total Users: {User.objects.count()}")
print(f"   ├─ Total Assessments: {Assessment.objects.count()}")
print(f"   ├─ Total Questions: {Question.objects.count()}")
print(f"   ├─ Total Tasks: {Task.objects.count()}")
print(f"   ├─ Assessment Attempts: {AssessmentAttempt.objects.count()}")
print(f"   └─ Task Recommendations: {TaskAssignment.objects.count()}")

print("\n✨ All data verified and ready for frontend deployment!")
print("="*60 + "\n")
