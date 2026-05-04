#!/usr/bin/env python
"""
Production-ready data population script.
Creates comprehensive, realistic test data for deployment.

Usage:
    python manage.py shell < create_production_data.py
    or
    python create_production_data.py
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent))

def setup_django():
    """Initialize Django."""
    django.setup()

def populate_database():
    """Populate database with comprehensive realistic test data."""
    from apps.assessments.models import Assessment, Question, AssessmentAttempt
    from apps.tasks.models import Task, TaskAssignment
    from apps.accounts.models import User
    
    print("\n" + "="*80)
    print("🚀 PRODUCTION DATA POPULATION SCRIPT")
    print("="*80 + "\n")
    
    # ========== CREATE TEST USERS ==========
    print("👥 Creating Users...\n")
    
    users_data = [
        {
            'email': 'student1@example.com',
            'name': 'Aisha Khan',
            'password': 'password123',
            'role': 'Student',
        },
        {
            'email': 'student2@example.com',
            'name': 'Alex Rodriguez',
            'password': 'password123',
            'role': 'Student',
        },
        {
            'email': 'student3@example.com',
            'name': 'Priya Patel',
            'password': 'password123',
            'role': 'Student',
        },
        {
            'email': 'mentor@example.com',
            'name': 'Dr. Sarah Chen',
            'password': 'password123',
            'role': 'Mentor',
        },
    ]
    
    users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'name': user_data['name'],
                'role': user_data['role'],
                'is_active': True,
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"  ✓ Created user: {user_data['name']} ({user_data['role']})")
        else:
            print(f"  ✓ User exists: {user_data['name']}")
        users[user_data['email']] = user
    
    student1 = users['student1@example.com']
    
    # ========== CREATE ASSESSMENTS WITH REALISTIC MCQs ==========
    print("\n📋 Creating Assessments with Realistic MCQs...\n")
    
    assessments_data = [
        {
            'title': 'Graphic Design Fundamentals',
            'domain': 'Graphic Design',
            'description': 'Master the core principles of graphic design including color theory, typography, composition, and visual hierarchy. This assessment tests foundational knowledge essential for any designer.',
            'time_limit': 40,
            'questions': [
                {
                    'text': 'What is the principle of visual hierarchy in design?',
                    'options': [
                        'A) Creating a clear order of importance in visual elements',
                        'B) Making all elements the same size and weight',
                        'C) Using only black and white colors',
                        'D) Filling the entire canvas with images'
                    ],
                    'correct': 'A',
                },
                {
                    'text': 'Which color combination is most complementary?',
                    'options': [
                        'A) Two shades of the same color',
                        'B) Colors opposite each other on the color wheel',
                        'C) Random colors',
                        'D) Only primary colors'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is kerning in typography?',
                    'options': [
                        'A) The space between lines of text',
                        'B) The weight of a typeface',
                        'C) The space between individual characters',
                        'D) The thickness of text strokes'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'Which design principle emphasizes balance and organization?',
                    'options': [
                        'A) Emphasis',
                        'B) Balance',
                        'C) Movement',
                        'D) Contrast'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is the rule of thirds?',
                    'options': [
                        'A) Always use 3 colors in a design',
                        'B) Dividing an image into 9 equal parts for better composition',
                        'C) Using 3 different fonts',
                        'D) Creating 3 separate design elements'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which file format is best for web graphics with transparency?',
                    'options': [
                        'A) JPEG',
                        'B) BMP',
                        'C) PNG',
                        'D) TIFF'
                    ],
                    'correct': 'C',
                },
            ]
        },
        {
            'title': 'Python Programming Essentials',
            'domain': 'Programming',
            'description': 'Comprehensive assessment of Python fundamentals including data types, control structures, functions, and object-oriented programming concepts.',
            'time_limit': 50,
            'questions': [
                {
                    'text': 'What is the correct way to create a list in Python?',
                    'options': [
                        'A) list = (1, 2, 3)',
                        'B) list = [1, 2, 3]',
                        'C) list = {1, 2, 3}',
                        'D) list = <1, 2, 3>'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which keyword is used to create a function in Python?',
                    'options': [
                        'A) def',
                        'B) function',
                        'C) func',
                        'D) define'
                    ],
                    'correct': 'A',
                },
                {
                    'text': 'What is the output of len("Python")?',
                    'options': [
                        'A) 5',
                        'B) 6',
                        'C) 7',
                        'D) Error'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which of these is NOT a Python data type?',
                    'options': [
                        'A) String',
                        'B) List',
                        'C) Dictionary',
                        'D) Array'
                    ],
                    'correct': 'D',
                },
                {
                    'text': 'What does the range(5) function return?',
                    'options': [
                        'A) [0, 1, 2, 3, 4, 5]',
                        'B) [1, 2, 3, 4, 5]',
                        'C) [0, 1, 2, 3, 4]',
                        'D) range object from 0 to 4'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'How do you start a comment in Python?',
                    'options': [
                        'A) //',
                        'B) #',
                        'C) --',
                        'D) /* */'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'Digital Marketing Strategy',
            'domain': 'Digital Marketing',
            'description': 'Evaluate your understanding of digital marketing channels, SEO, SEM, social media marketing, content strategy, and analytics.',
            'time_limit': 45,
            'questions': [
                {
                    'text': 'What does SEO stand for?',
                    'options': [
                        'A) Social Engine Optimization',
                        'B) Search Engine Optimization',
                        'C) Site Engine Optimization',
                        'D) Search Enabled Operation'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which metric measures how many times your ad is clicked?',
                    'options': [
                        'A) Impressions',
                        'B) Click-Through Rate (CTR)',
                        'C) Clicks',
                        'D) Conversions'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is a buyer persona?',
                    'options': [
                        'A) A real customer',
                        'B) A detailed fictional representation of your ideal customer',
                        'C) A marketing campaign',
                        'D) A social media profile'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which platform is best for B2B marketing?',
                    'options': [
                        'A) TikTok',
                        'B) Instagram',
                        'C) LinkedIn',
                        'D) Snapchat'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What does CTA stand for?',
                    'options': [
                        'A) Customer Trade Agreement',
                        'B) Click To Action',
                        'C) Call To Action',
                        'D) Content Traffic Analysis'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is organic reach in social media?',
                    'options': [
                        'A) Paid advertisements',
                        'B) Users you reach without paying',
                        'C) Email subscribers',
                        'D) Website visitors'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'Web Development Basics',
            'domain': 'Programming',
            'description': 'Test your knowledge of HTML, CSS, JavaScript fundamentals, and web development best practices.',
            'time_limit': 50,
            'questions': [
                {
                    'text': 'What does HTML stand for?',
                    'options': [
                        'A) Hyper Text Markup Language',
                        'B) High Tech Modern Language',
                        'C) Home Tool Markup Language',
                        'D) Hyperlinks and Text Markup Language'
                    ],
                    'correct': 'A',
                },
                {
                    'text': 'Which HTML tag is used for the largest heading?',
                    'options': [
                        'A) <h6>',
                        'B) <h1>',
                        'C) <heading>',
                        'D) <header>'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What CSS property is used to change text color?',
                    'options': [
                        'A) text-color',
                        'B) font-color',
                        'C) color',
                        'D) text-style'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'Which is a valid CSS selector?',
                    'options': [
                        'A) @classname',
                        'B) .classname',
                        'C) *classname',
                        'D) &classname'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is the correct syntax for JavaScript variables?',
                    'options': [
                        'A) v myVar = 5;',
                        'B) var myVar = 5;',
                        'C) variable myVar = 5;',
                        'D) my_var = 5;'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'Data Analytics Fundamentals',
            'domain': 'Data Analytics',
            'description': 'Assess your knowledge of data analysis, visualization, SQL, and business intelligence concepts.',
            'time_limit': 45,
            'questions': [
                {
                    'text': 'What is a data type in databases?',
                    'options': [
                        'A) The way data is organized',
                        'B) A classification defining the kind of values a column can hold',
                        'C) The format of a spreadsheet',
                        'D) A type of database query'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which SQL command retrieves data?',
                    'options': [
                        'A) UPDATE',
                        'B) DELETE',
                        'C) SELECT',
                        'D) INSERT'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What does KPI stand for?',
                    'options': [
                        'A) Key Performance Indicator',
                        'B) Knowledge Performance Index',
                        'C) Key Process Improvement',
                        'D) Knowledge Product Integration'
                    ],
                    'correct': 'A',
                },
                {
                    'text': 'Which visualization is best for showing trends over time?',
                    'options': [
                        'A) Pie chart',
                        'B) Line graph',
                        'C) Bar chart',
                        'D) Scatter plot'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is the median in a dataset?',
                    'options': [
                        'A) The most frequent value',
                        'B) The average of all values',
                        'C) The middle value when sorted',
                        'D) The difference between max and min'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is a dashboard in BI tools?',
                    'options': [
                        'A) A car control panel',
                        'B) A visual representation of key metrics and KPIs',
                        'C) A database table',
                        'D) A type of chart'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'Content Writing & SEO',
            'domain': 'Content Writing',
            'description': 'Test your skills in content creation, copywriting, SEO optimization, and audience engagement.',
            'time_limit': 40,
            'questions': [
                {
                    'text': 'What is meta description?',
                    'options': [
                        'A) A description of the website author',
                        'B) A brief summary of a webpage shown in search results',
                        'C) A type of HTML tag',
                        'D) The main heading of a page'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is a long-tail keyword?',
                    'options': [
                        'A) A keyword longer than 10 characters',
                        'B) A keyword with 3+ words that is more specific',
                        'C) The last keyword in a list',
                        'D) A keyword used at the end of content'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which is a best practice for headlines?',
                    'options': [
                        'A) Make them as long as possible',
                        'B) Use clickbait always',
                        'C) Make them clear, compelling, and descriptive',
                        'D) Avoid using numbers'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is the ideal content length for blog posts?',
                    'options': [
                        'A) 100-200 words',
                        'B) 500-1000 words',
                        'C) 1000-2000+ words for comprehensive posts',
                        'D) No limit'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is the CTA in content?',
                    'options': [
                        'A) Content Title Area',
                        'B) Call To Action - directing readers to take action',
                        'C) Content Traffic Analytics',
                        'D) Citation To Article'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'Social Media Marketing',
            'domain': 'Digital Marketing',
            'description': 'Comprehensive assessment of social media strategy, content creation, engagement, and platform-specific best practices.',
            'time_limit': 35,
            'questions': [
                {
                    'text': 'What is engagement rate in social media?',
                    'options': [
                        'A) Number of followers',
                        'B) The percentage of followers who interact with your content',
                        'C) The number of posts',
                        'D) The number of shares'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'Which platform has the highest average engagement rate?',
                    'options': [
                        'A) Facebook',
                        'B) LinkedIn',
                        'C) Instagram',
                        'D) Twitter'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is a hashtag strategy?',
                    'options': [
                        'A) Using as many hashtags as possible',
                        'B) Not using hashtags at all',
                        'C) Strategically using relevant hashtags to increase discoverability',
                        'D) Using the same hashtags every day'
                    ],
                    'correct': 'C',
                },
                {
                    'text': 'What is user-generated content (UGC)?',
                    'options': [
                        'A) Content created only by brands',
                        'B) Content created by users and followers of the brand',
                        'C) Advertisements',
                        'D) Official company announcements'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is the best time to post on Instagram?',
                    'options': [
                        'A) Always at 12:00 PM',
                        'B) When your audience is most active (usually 11 AM - 1 PM, 7 PM - 9 PM)',
                        'C) Midnight',
                        'D) Early morning (5-6 AM)'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What does "going viral" mean?',
                    'options': [
                        'A) Spreading a computer virus',
                        'B) Content rapidly spreading and gaining massive engagement',
                        'C) A type of post',
                        'D) An algorithm change'
                    ],
                    'correct': 'B',
                },
            ]
        },
        {
            'title': 'UI/UX Design Principles',
            'domain': 'Graphic Design',
            'description': 'Master user interface and user experience design principles, usability testing, and design thinking methodology.',
            'time_limit': 45,
            'questions': [
                {
                    'text': 'What is the primary goal of UX design?',
                    'options': [
                        'A) Making things look beautiful',
                        'B) Creating a positive and useful user experience',
                        'C) Using latest design trends',
                        'D) Complex animations'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is a wireframe in UI design?',
                    'options': [
                        'A) A final design mockup',
                        'B) A low-fidelity sketch showing layout and structure',
                        'C) A type of font',
                        'D) A color palette'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What does WCAG stand for?',
                    'options': [
                        'A) Web Content Accessibility Guidelines',
                        'B) Website Color And Graphics',
                        'C) Web Creation And Generation',
                        'D) Wireless Content And Gateway'
                    ],
                    'correct': 'A',
                },
                {
                    'text': 'What is a user persona?',
                    'options': [
                        'A) Your personal user account',
                        'B) A fictional representation of your target user',
                        'C) The designer\'s profile',
                        'D) A type of website'
                    ],
                    'correct': 'B',
                },
                {
                    'text': 'What is the F-pattern in web design?',
                    'options': [
                        'A) A font type',
                        'B) A color pattern',
                        'C) How users typically scan webpages (left to right, top to bottom)',
                        'D) A type of layout'
                    ],
                    'correct': 'C',
                },
            ]
        },
    ]
    
    # ── concept tag + difficulty weight per (assessment title, 1-based order) ──
    # difficulty_weight: 1.0 = standard, 1.2 = harder, 0.8 = easier
    QUESTION_CONCEPT_MAP = {
        # Graphic Design Fundamentals
        ('Graphic Design Fundamentals', 1): ('visual hierarchy',  1.0),
        ('Graphic Design Fundamentals', 2): ('colour theory',     1.2),
        ('Graphic Design Fundamentals', 3): ('typography',        1.0),
        ('Graphic Design Fundamentals', 4): ('design principles', 1.0),
        ('Graphic Design Fundamentals', 5): ('composition',       1.2),
        ('Graphic Design Fundamentals', 6): ('file formats',      0.8),
        # Python Programming Essentials
        ('Python Programming Essentials', 1): ('data structures', 1.2),
        ('Python Programming Essentials', 2): ('functions',       1.0),
        ('Python Programming Essentials', 3): ('strings',         1.0),
        ('Python Programming Essentials', 4): ('data types',      1.0),
        ('Python Programming Essentials', 5): ('loops',           1.2),
        ('Python Programming Essentials', 6): ('syntax',          0.8),
        # Digital Marketing Strategy
        ('Digital Marketing Strategy', 1): ('SEO',                1.0),
        ('Digital Marketing Strategy', 2): ('advertising metrics',1.2),
        ('Digital Marketing Strategy', 3): ('audience targeting', 1.2),
        ('Digital Marketing Strategy', 4): ('platform strategy',  1.0),
        ('Digital Marketing Strategy', 5): ('conversion',         1.0),
        ('Digital Marketing Strategy', 6): ('social media',       1.0),
        # Web Development Basics
        ('Web Development Basics', 1): ('HTML',       0.8),
        ('Web Development Basics', 2): ('HTML',       0.8),
        ('Web Development Basics', 3): ('CSS',        1.0),
        ('Web Development Basics', 4): ('CSS',        1.0),
        ('Web Development Basics', 5): ('JavaScript', 1.2),
        # Data Analytics Fundamentals
        ('Data Analytics Fundamentals', 1): ('databases',           1.0),
        ('Data Analytics Fundamentals', 2): ('SQL',                 1.2),
        ('Data Analytics Fundamentals', 3): ('business intelligence',1.0),
        ('Data Analytics Fundamentals', 4): ('data visualization',  1.2),
        ('Data Analytics Fundamentals', 5): ('statistics',          1.2),
        ('Data Analytics Fundamentals', 6): ('business intelligence',1.0),
        # Content Writing & SEO
        ('Content Writing & SEO', 1): ('SEO',              1.2),
        ('Content Writing & SEO', 2): ('SEO',              1.2),
        ('Content Writing & SEO', 3): ('copywriting',      1.0),
        ('Content Writing & SEO', 4): ('content strategy', 1.0),
        ('Content Writing & SEO', 5): ('conversion',       1.0),
        # Social Media Marketing
        ('Social Media Marketing', 1): ('analytics',       1.2),
        ('Social Media Marketing', 2): ('platform strategy',1.0),
        ('Social Media Marketing', 3): ('content strategy', 1.0),
        ('Social Media Marketing', 4): ('content strategy', 1.2),
        ('Social Media Marketing', 5): ('platform strategy',1.0),
        ('Social Media Marketing', 6): ('content strategy', 1.0),
        # UI/UX Design Principles
        ('UI/UX Design Principles', 1): ('UX principles', 1.0),
        ('UI/UX Design Principles', 2): ('UI design',     1.0),
        ('UI/UX Design Principles', 3): ('accessibility', 1.2),
        ('UI/UX Design Principles', 4): ('user research', 1.2),
        ('UI/UX Design Principles', 5): ('UX principles', 1.0),
    }

    assessment_map = {}
    for data in assessments_data:
        questions = data.pop('questions')
        assessment, created = Assessment.objects.get_or_create(
            title=data['title'],
            domain=data['domain'],
            defaults={
                'description': data['description'],
                'time_limit': data['time_limit'],
                'is_active': True,
                'created_by': student1,
            }
        )
        
        assessment_map[assessment.title] = assessment
        
        if created:
            print(f"  ✓ Created: {assessment.title}")
            
            for order, q_data in enumerate(questions, 1):
                options = q_data.pop('options')
                correct = q_data.pop('correct')
                concept, weight = QUESTION_CONCEPT_MAP.get(
                    (assessment.title, order), ('', 1.0)
                )
                
                Question.objects.get_or_create(
                    assessment=assessment,
                    order=order,
                    defaults={
                        'text': q_data['text'],
                        'option_a': options[0].replace('A) ', ''),
                        'option_b': options[1].replace('B) ', ''),
                        'option_c': options[2].replace('C) ', ''),
                        'option_d': options[3].replace('D) ', ''),
                        'correct_option': correct,
                        'concept': concept,
                        'difficulty_weight': weight,
                    }
                )
            
            print(f"    └─ Added {len(questions)} MCQ questions with concept tags")
        else:
            print(f"  ✓ Already exists: {assessment.title} — patching concept tags...")
            for order, q_data in enumerate(questions, 1):
                concept, weight = QUESTION_CONCEPT_MAP.get(
                    (assessment.title, order), ('', 1.0)
                )
                if concept:
                    Question.objects.filter(
                        assessment=assessment, order=order, concept=''
                    ).update(concept=concept, difficulty_weight=weight)
            print(f"    └─ Concept tags applied")
    
    # ========== CREATE TASKS ==========
    print("\n📝 Creating Realistic Tasks...\n")
    
    tasks_data = [
        {
            'title': 'Design a Modern Mobile App UI',
            'domain': 'Graphic Design',
            'difficulty': 'Advanced',
            'task_type': 'Design',
            'description': 'Create a complete UI design for a mobile app including screens for onboarding, home, profile, and settings. Include wireframes and high-fidelity mockups with proper spacing, typography, and color scheme.',
            'required_skills': ['Figma', 'UI Design', 'Mobile Design', 'User Testing'],
            'learning_outcomes': ['Master mobile app design', 'Learn design systems', 'Improve user research skills'],
            'estimated_duration': 720,
        },
        {
            'title': 'Build an E-Commerce Website with Django',
            'domain': 'Programming',
            'difficulty': 'Advanced',
            'task_type': 'Development',
            'description': 'Develop a fully functional e-commerce website using Django with product listings, shopping cart, payment integration, and admin panel. Include proper authentication and database design.',
            'required_skills': ['Django', 'Python', 'PostgreSQL', 'REST API'],
            'learning_outcomes': ['Build production-ready web apps', 'Learn payment integration', 'Master database design'],
            'estimated_duration': 1200,
        },
        {
            'title': 'Create a Comprehensive Blog Post on AI Trends',
            'domain': 'Content Writing',
            'difficulty': 'Intermediate',
            'task_type': 'Content',
            'description': 'Write a 2000+ word blog post about current AI trends and their impact on various industries. Include research, data visualization, and call-to-action. Optimize for SEO.',
            'required_skills': ['Research', 'SEO Writing', 'Data Analysis', 'Copywriting'],
            'learning_outcomes': ['Master long-form content', 'Learn SEO optimization', 'Develop research skills'],
            'estimated_duration': 480,
        },
        {
            'title': 'Build a Data Analytics Dashboard',
            'domain': 'Data Analytics',
            'difficulty': 'Advanced',
            'task_type': 'Analysis',
            'description': 'Create an interactive dashboard analyzing real-world dataset. Include multiple visualizations, filters, and key metrics. Use tools like Tableau or Power BI.',
            'required_skills': ['Tableau', 'SQL', 'Data Analysis', 'Visualization'],
            'learning_outcomes': ['Master BI tools', 'Learn data storytelling', 'Improve analysis skills'],
            'estimated_duration': 600,
        },
        {
            'title': 'Plan and Execute a Social Media Campaign',
            'domain': 'Digital Marketing',
            'difficulty': 'Intermediate',
            'task_type': 'Marketing',
            'description': 'Plan a 30-day social media campaign for a fictional brand including content calendar, engagement strategy, and success metrics. Then execute on at least one platform.',
            'required_skills': ['Social Media Strategy', 'Content Creation', 'Analytics', 'Copywriting'],
            'learning_outcomes': ['Develop campaign strategy', 'Learn social media management', 'Improve analytics skills'],
            'estimated_duration': 360,
        },
        {
            'title': 'Develop a Python Web Scraper',
            'domain': 'Programming',
            'difficulty': 'Intermediate',
            'task_type': 'Development',
            'description': 'Create a web scraper using Beautiful Soup or Scrapy to collect data from 3+ websites. Store data in a database and generate reports.',
            'required_skills': ['Python', 'BeautifulSoup', 'Web Scraping', 'Data Processing'],
            'learning_outcomes': ['Learn web scraping', 'Master data collection', 'Improve Python skills'],
            'estimated_duration': 300,
        },
        {
            'title': 'Create a Logo and Brand Identity',
            'domain': 'Graphic Design',
            'difficulty': 'Intermediate',
            'task_type': 'Design',
            'description': 'Design a complete brand identity for a startup including logo, color palette, typography, and brand guidelines document.',
            'required_skills': ['Adobe Illustrator', 'Logo Design', 'Color Theory', 'Brand Strategy'],
            'learning_outcomes': ['Master logo design', 'Learn brand development', 'Improve design thinking'],
            'estimated_duration': 480,
        },
        {
            'title': 'Conduct SEO Audit and Optimization',
            'domain': 'Digital Marketing',
            'difficulty': 'Intermediate',
            'task_type': 'Marketing',
            'description': 'Perform a comprehensive SEO audit of a website. Identify issues, create an optimization plan, and implement improvements. Track results.',
            'required_skills': ['SEO Tools', 'Technical SEO', 'Copywriting', 'Analytics'],
            'learning_outcomes': ['Learn technical SEO', 'Improve audit skills', 'Master SEO tools'],
            'estimated_duration': 240,
        },
        {
            'title': 'React Frontend Development Project',
            'domain': 'Programming',
            'difficulty': 'Intermediate',
            'task_type': 'Development',
            'description': 'Build a React application with multiple components, state management, and API integration. Include routing and responsive design.',
            'required_skills': ['React', 'JavaScript', 'CSS', 'API Integration'],
            'learning_outcomes': ['Master React framework', 'Learn state management', 'Improve component design'],
            'estimated_duration': 360,
        },
        {
            'title': 'Email Marketing Campaign Creation',
            'domain': 'Digital Marketing',
            'difficulty': 'Beginner',
            'task_type': 'Marketing',
            'description': 'Design and execute an email marketing campaign including segmentation, A/B testing, and performance analysis using platforms like Mailchimp.',
            'required_skills': ['Email Marketing', 'Copywriting', 'Design', 'Analytics'],
            'learning_outcomes': ['Learn email marketing', 'Master campaign design', 'Improve conversion skills'],
            'estimated_duration': 180,
        },
        {
            'title': 'Infographic Design Project',
            'domain': 'Graphic Design',
            'difficulty': 'Intermediate',
            'task_type': 'Design',
            'description': 'Create 3 infographics presenting complex data in visually engaging ways. Include data visualization best practices and proper attribution.',
            'required_skills': ['Data Visualization', 'Design Tools', 'Infographic Design', 'Copywriting'],
            'learning_outcomes': ['Master infographic design', 'Learn data visualization', 'Improve presentation skills'],
            'estimated_duration': 300,
        },
        {
            'title': 'SQL Database Design and Optimization',
            'domain': 'Data Analytics',
            'difficulty': 'Advanced',
            'task_type': 'Analysis',
            'description': 'Design a normalized SQL database schema, create complex queries, and optimize performance. Include documentation and ER diagrams.',
            'required_skills': ['SQL', 'Database Design', 'Query Optimization', 'PostgreSQL'],
            'learning_outcomes': ['Master database design', 'Learn query optimization', 'Improve performance tuning'],
            'estimated_duration': 420,
        },
        {
            'title': 'Video Content Creation and Editing',
            'domain': 'Content Writing',
            'difficulty': 'Intermediate',
            'task_type': 'Content',
            'description': 'Create a series of 5 short videos (30-60 seconds each) for social media. Include scripting, filming, and professional editing.',
            'required_skills': ['Video Editing', 'Scriptwriting', 'Filming', 'Adobe Premiere'],
            'learning_outcomes': ['Learn video production', 'Master editing software', 'Improve storytelling skills'],
            'estimated_duration': 480,
        },
        {
            'title': 'Competitor Analysis Report',
            'domain': 'Digital Marketing',
            'difficulty': 'Beginner',
            'task_type': 'Marketing',
            'description': 'Analyze 5 competitors in a chosen industry. Create a detailed report with insights on their strategies, strengths, and weaknesses.',
            'required_skills': ['Market Research', 'Analysis', 'Strategic Thinking', 'Report Writing'],
            'learning_outcomes': ['Learn market analysis', 'Develop strategic thinking', 'Improve research skills'],
            'estimated_duration': 240,
        },
        {
            'title': 'Advanced Excel Dashboard Creation',
            'domain': 'Data Analytics',
            'difficulty': 'Intermediate',
            'task_type': 'Analysis',
            'description': 'Create a dynamic Excel dashboard with pivot tables, charts, slicers, and KPI indicators for business reporting.',
            'required_skills': ['Excel', 'Pivot Tables', 'Data Analysis', 'Visualization'],
            'learning_outcomes': ['Master Excel dashboards', 'Learn data presentation', 'Improve analysis skills'],
            'estimated_duration': 300,
        },
    ]
    
    task_map = {}
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
                'created_by': student1,
            }
        )
        
        task_map[task.title] = task
        
        if created:
            print(f"  ✓ Created: {task.title}")
        else:
            print(f"  ✓ Already exists: {task.title}")
    
    # ========== CREATE ASSESSMENT ATTEMPTS ==========
    print("\n✅ Creating Assessment Attempts (Test Results)...\n")
    
    students = [student1] + [users['student2@example.com'], users['student3@example.com']]
    
    for student in students:
        for assessment in Assessment.objects.all():
            # Create 1-3 attempts per student per assessment
            num_attempts = random.randint(1, 3)
            
            for attempt_num in range(num_attempts):
                # Generate realistic answers and scores
                questions = assessment.questions.all()
                answers = {}
                correct_count = 0
                
                for question in questions:
                    # 70% chance to answer correctly (higher for better students)
                    if random.random() < (0.6 + random.random() * 0.3):
                        answers[f'q{question.order}'] = question.correct_option
                        correct_count += 1
                    else:
                        # Random wrong answer
                        wrong_options = ['A', 'B', 'C', 'D']
                        wrong_options.remove(question.correct_option)
                        answers[f'q{question.order}'] = random.choice(wrong_options)
                
                total = len(questions)
                percentage = (correct_count / total) * 100
                
                # Determine skill level based on score
                if percentage >= 85:
                    skill_level = 'Advanced'
                elif percentage >= 70:
                    skill_level = 'Intermediate'
                else:
                    skill_level = 'Beginner'
                
                attempt_date = timezone.now() - timedelta(days=random.randint(1, 90))
                
                attempt, created = AssessmentAttempt.objects.get_or_create(
                    student=student,
                    assessment=assessment,
                    attempted_at__date=attempt_date.date(),
                    defaults={
                        'answers': answers,
                        'score': int(correct_count),
                        'total_questions': total,
                        'percentage': round(percentage, 2),
                        'skill_level': skill_level,
                        'recommended_domains': [assessment.domain],
                        'attempted_at': attempt_date,
                        'strengths': ['Problem solving', 'Theory understanding'],
                        'weaknesses': ['Time management', 'Complex problems'],
                        'next_steps': ['Practice more problems', 'Review weak areas', 'Study case studies'],
                    }
                )
                
                if created:
                    print(f"  ✓ {student.name} - {assessment.title}: {percentage:.1f}% ({skill_level})")
    
    # ========== CREATE TASK RECOMMENDATIONS ==========
    print("\n🎯 Creating Task Recommendations...\n")
    
    for student in students:
        # Get last assessment attempt to base recommendations on
        last_assessment = AssessmentAttempt.objects.filter(student=student).latest('attempted_at')
        
        if last_assessment:
            # Recommend tasks based on assessment domain and skill level
            recommended_tasks = Task.objects.filter(domain=last_assessment.recommended_domains[0])
            
            # Sort by difficulty matching skill level
            if last_assessment.skill_level == 'Advanced':
                recommended_tasks = recommended_tasks.filter(difficulty__in=['Intermediate', 'Advanced'])
            elif last_assessment.skill_level == 'Intermediate':
                recommended_tasks = recommended_tasks.filter(difficulty__in=['Beginner', 'Intermediate', 'Advanced'])
            
            for task in recommended_tasks[:3]:  # Recommend top 3 tasks
                assignment, created = TaskAssignment.objects.get_or_create(
                    student=student,
                    task=task,
                    defaults={
                        'status': 'recommended',
                        'progress_percentage': 0,
                        'assigned_by': users['mentor@example.com'],
                        'recommended_score': round(last_assessment.percentage * 0.9, 2),
                        'recommendation_reason': f'Recommended based on {last_assessment.assessment.title} assessment ({last_assessment.percentage:.1f}% score)',
                    }
                )
                
                if created:
                    print(f"  ✓ Recommended to {student.name}: {task.title}")
    
    # ========== PRINT SUMMARY ==========
    print("\n" + "="*80)
    print("✨ PRODUCTION DATABASE POPULATED SUCCESSFULLY!")
    print("="*80)
    
    print(f"\n📊 Database Summary:")
    print(f"  • Users: {User.objects.count()}")
    print(f"  • Assessments: {Assessment.objects.count()}")
    print(f"  • Questions: {Question.objects.count()}")
    print(f"  • Tasks: {Task.objects.count()}")
    print(f"  • Assessment Attempts: {AssessmentAttempt.objects.count()}")
    print(f"  • Task Assignments (Recommendations): {TaskAssignment.objects.count()}")
    
    print(f"\n👥 Test Users (All use password: 'password123'):")
    for user_data in users_data:
        print(f"  • {user_data['email']} - {user_data['name']} ({user_data['role']})")
    
    print("\n✅ Ready for Deployment!")
    print("  1. All data is realistic and production-ready")
    print("  2. Multiple students with different skill levels")
    print("  3. Comprehensive assessments with real MCQ questions")
    print("  4. Diverse tasks covering all domains")
    print("  5. Proper recommendations based on assessment results")
    print("\n📝 Next Steps:")
    print("  1. Login as student1@example.com with password: password123")
    print("  2. Navigate to 'Assessments' to see all available tests")
    print("  3. Check 'Recommended' tab to see personalized task recommendations")
    print("  4. View 'Analytics' to see assessment performance insights")
    print("  5. Try the chatbot for learning assistance")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    setup_django()
    populate_database()
