"""
Recommendation engine for skill assessments.

Logic (simple + explainable, aligned with sequence diagram):
  - >= 80%  => Advanced   => strongly recommend domain + 2 freelancing roles
  - 50-79%  => Intermediate => recommend domain + improvement suggestions
  - < 50%   => Beginner   => recommend learning path + domain if close
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
            ],
            'message': (
                f'Excellent! You scored {percentage:.0f}% in {domain}. '
                f'You are at an Advanced level. We strongly recommend pursuing '
                f'freelancing in this domain. Suggested roles: {", ".join(data["roles"])}.'
            ),
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
            ],
            'message': (
                f'Good effort! You scored {percentage:.0f}% in {domain}. '
                f'You are at an Intermediate level. {data["tips"]} '
                f'Keep improving and you\'ll be ready to freelance soon.'
            ),
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
            ],
            'message': (
                f'You scored {percentage:.0f}% in {domain}. '
                f'You are at a Beginner level. Don\'t worry — everyone starts somewhere! '
                f'We recommend starting with: {", ".join(data["resources"][:2])}. '
                f'{data["tips"]}'
            ),
        }
