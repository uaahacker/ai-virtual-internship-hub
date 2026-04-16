"""
Recommendation engine for skill assessments.

Logic (simple + explainable, aligned with sequence diagram):
  - >= 80%  => Advanced   => strongly recommend domain + 2 freelancing roles
  - 50-79%  => Intermediate => recommend domain + improvement suggestions
  - < 50%   => Beginner   => recommend learning path + domain if close

Enhanced: Now generates detailed feedback including strengths, weaknesses, and next steps.
"""

# Maps domain -> { roles, resources, tips }
DOMAIN_DATA = {
    'Graphic Design': {
        'roles': ['Logo & Brand Identity Designer', 'Social Media Graphics Freelancer'],
        'resources': ['Adobe Illustrator tutorials', 'Canva design courses', 'Color theory fundamentals'],
        'tips': 'Practice recreating existing designs and build a portfolio on Behance.',
    },
    'Content Writing': {
        'roles': ['SEO Blog Writer', 'Copywriting Freelancer'],
        'resources': ['Grammarly writing guides', 'HubSpot content marketing course', 'Neil Patel SEO blog'],
        'tips': 'Write daily articles on Medium and learn SEO basics to boost visibility.',
    },
    'Programming': {
        'roles': ['Full-Stack Web Developer', 'Python Automation Freelancer'],
        'resources': ['freeCodeCamp curriculum', 'CS50 by Harvard', 'LeetCode practice'],
        'tips': 'Build real projects on GitHub and contribute to open source.',
    },
    'Freelancing': {
        'roles': ['Virtual Assistant', 'Project Management Freelancer'],
        'resources': ['Fiverr & Upwork profile optimization', 'Freelancing 101 by Skillshare'],
        'tips': 'Create profiles on multiple platforms and focus on client communication.',
    },
    'E-Commerce': {
        'roles': ['Shopify Store Manager', 'Amazon FBA Consultant'],
        'resources': ['Shopify Academy', 'Google Digital Garage', 'Oberlo dropshipping guides'],
        'tips': 'Start a small test store and learn about product research & listing optimization.',
    },
    'QuickBooks': {
        'roles': ['Bookkeeping Freelancer', 'QuickBooks ProAdvisor'],
        'resources': ['QuickBooks certification program', 'Accounting fundamentals on Coursera'],
        'tips': 'Get QuickBooks certified and offer bookkeeping services on freelancing platforms.',
    },
    'AutoCAD': {
        'roles': ['CAD Drafting Freelancer', '3D Modeling Specialist'],
        'resources': ['Autodesk official tutorials', 'LinkedIn Learning AutoCAD courses'],
        'tips': 'Build a portfolio of technical drawings and offer services on Upwork.',
    },
    'Data Analytics': {
        'roles': ['Data Analyst Freelancer', 'Business Intelligence Consultant'],
        'resources': ['Google Data Analytics Certificate', 'Kaggle datasets & competitions'],
        'tips': 'Master Excel, SQL, and one visualization tool (Tableau or Power BI).',
    },
    'Digital Marketing': {
        'roles': ['Social Media Manager', 'PPC Advertising Freelancer'],
        'resources': ['Google Ads certification', 'HubSpot Academy', 'Meta Blueprint'],
        'tips': 'Run small ad campaigns for local businesses to build case studies.',
    },
    'WordPress': {
        'roles': ['WordPress Developer', 'Website Maintenance Freelancer'],
        'resources': ['WordPress.org documentation', 'Elementor tutorials', 'WooCommerce guides'],
        'tips': 'Build 3-5 demo sites and list your services on freelancing platforms.',
    },
}


def generate_recommendation(domain, percentage):
    """
    Generate recommendation dict based on assessment score.

    Returns:
    {
        "skill_level": str,
        "domain": str,
        "strength": str,
        "recommended_roles": list[str],
        "suggestions": list[str],
        "message": str,
        "reason": str,
        "improvement_areas": list[str],
    }
    """
    data = DOMAIN_DATA.get(domain, DOMAIN_DATA.get('Programming'))

    if percentage >= 80:
        skill_level = 'Advanced'
        return {
            'skill_level': skill_level,
            'domain': domain,
            'strength': 'Strong',
            'recommended_roles': data['roles'],
            'suggestions': [
                f'You have strong skills in {domain}. Start freelancing immediately!',
                f'Consider creating a professional portfolio showcasing your {domain} work.',
                'Seek advanced projects to specialize further in this field.',
            ],
            'message': (
                f'Excellent! You scored {percentage:.0f}% in {domain}. '
                f'You are at an Advanced level. We strongly recommend pursuing '
                f'freelancing in this domain. Suggested roles: {", ".join(data["roles"])}.'
            ),
            'reason': (
                f'Your score of {percentage:.0f}% demonstrates mastery of {domain}. '
                f'You have successfully demonstrated advanced understanding across most concepts.'
            ),
            'improvement_areas': [],
        }

    elif percentage >= 50:
        skill_level = 'Intermediate'
        return {
            'skill_level': skill_level,
            'domain': domain,
            'strength': 'Moderate',
            'recommended_roles': data['roles'],
            'suggestions': [
                f'Improve your {domain} skills with these resources: {", ".join(data["resources"][:2])}.',
                data['tips'],
                'Practice regularly and retake the assessment to track your progress.',
                'Focus on weakest areas before taking freelancing projects.',
            ],
            'message': (
                f'Good effort! You scored {percentage:.0f}% in {domain}. '
                f'You are at an Intermediate level. {data["tips"]} '
                f'Keep improving and you\'ll be ready to freelance soon.'
            ),
            'reason': (
                f'Your score of {percentage:.0f}% shows solid understanding, but there\'s room for improvement. '
                f'Focus on the weaker areas identified above before pursuing advanced work.'
            ),
            'improvement_areas': [
                'Review concepts where you scored incorrectly',
                'Practice with real-world scenarios',
                'Study recommended resources to fill knowledge gaps',
            ],
        }

    else:
        skill_level = 'Beginner'
        return {
            'skill_level': skill_level,
            'domain': domain,
            'strength': 'Developing',
            'recommended_roles': data['roles'],
            'suggestions': [
                f'Start with foundational courses: {", ".join(data["resources"])}.',
                data['tips'],
                'Focus on learning the basics before taking on freelancing projects.',
                'Retake this assessment after completing the recommended resources.',
                'Consider mentorship from experienced professionals in this field.',
            ],
            'message': (
                f'You scored {percentage:.0f}% in {domain}. '
                f'You are at a Beginner level. Don\'t worry — everyone starts somewhere! '
                f'We recommend starting with: {", ".join(data["resources"][:2])}. '
                f'{data["tips"]}'
            ),
            'reason': (
                f'Your score of {percentage:.0f}% indicates you\'re just starting your journey. '
                f'This is a great opportunity to build a strong foundation by studying the fundamentals.'
            ),
            'improvement_areas': [
                'Master fundamental concepts',
                'Complete beginner-level courses',
                'Build basic practice projects',
                'Take the assessment again after 2-3 weeks of study',
            ],
        }


def calculate_performance_breakdown(questions, submitted_answers):
    """
    Calculate detailed breakdown of correct/incorrect responses.
    
    Returns:
    {
        "question_id": {
            "text": str,
            "submitted": str,
            "correct": bool,
            "correct_option": str,
            "explanation": str,
        },
        ...
    }
    """
    breakdown = {}
    for question in questions:
        q_id = str(question.id)
        submitted = submitted_answers.get(q_id, 'Not answered')
        is_correct = submitted == question.correct_option
        
        breakdown[q_id] = {
            'text': question.text[:100],  # Truncate for storage
            'submitted': submitted,
            'correct_option': question.correct_option,
            'is_correct': is_correct,
            'explanation': (
                f"Correct answer: {question.correct_option}. "
                f"You selected: {submitted}."
            ) if not is_correct else "Correctly answered!",
        }
    return breakdown
