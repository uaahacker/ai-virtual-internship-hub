"""
Management command: seed_tasks

Seeds the database with internship-style tasks for all 10 domains at
Beginner, Intermediate, and Advanced difficulty levels.
Each task includes MCQ questions for learning assessment.

Usage:
    python manage.py seed_tasks
    python manage.py seed_tasks --clear   # remove existing tasks first
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------------------------------------------------------
# Task seed data  (3 tasks × 3 difficulties × 10 domains = 90 tasks)
# Each task has 3 MCQ questions for learning reinforcement.
# ---------------------------------------------------------------------------

SEED_TASKS = [

    # ── GRAPHIC DESIGN ──────────────────────────────────────────────────────
    {
        'title': 'Design a Logo for a Startup',
        'description': (
            'Create a professional logo for a fictional tech startup. '
            'The logo must be delivered in vector format and work on both '
            'light and dark backgrounds. Consider typography, color theory, '
            'and brand identity principles.'
        ),
        'domain': 'Graphic Design',
        'difficulty': 'Beginner',
        'task_type': 'Design',
        'required_skills': ['Adobe Illustrator', 'Color Theory', 'Typography'],
        'learning_outcomes': [
            'Understand logo design principles',
            'Work with vector graphics',
            'Apply basic color theory',
        ],
        'estimated_duration': 180,
        'mcqs': [
            {
                'question_text': 'Which file format is best for a scalable logo?',
                'option_a': 'JPEG',
                'option_b': 'PNG',
                'option_c': 'SVG',
                'option_d': 'BMP',
                'correct_answer': 'C',
                'concept': 'Vector Formats',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What does CMYK stand for?',
                'option_a': 'Cyan, Magenta, Yellow, Key (Black)',
                'option_b': 'Color, Mix, Yellow, Key',
                'option_c': 'Cyan, Mix, Yellow, Khaki',
                'option_d': 'Color, Magenta, Yellow, Khaki',
                'correct_answer': 'A',
                'concept': 'Color Models',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which principle ensures visual balance in a logo?',
                'option_a': 'Contrast',
                'option_b': 'Symmetry / Balance',
                'option_c': 'Proximity',
                'option_d': 'Repetition',
                'correct_answer': 'B',
                'concept': 'Design Principles',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Create a Social Media Post Series',
        'description': (
            'Design a cohesive set of 5 Instagram posts for a fashion brand. '
            'Maintain consistent fonts, colors, and visual style. '
            'Include captions layout and use Canva or Photoshop.'
        ),
        'domain': 'Graphic Design',
        'difficulty': 'Intermediate',
        'task_type': 'Design',
        'required_skills': ['Adobe Photoshop', 'Canva', 'Visual Consistency', 'Typography'],
        'learning_outcomes': [
            'Build a consistent brand visual identity',
            'Design for social media dimensions',
            'Combine text and images effectively',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is the standard Instagram square post resolution?',
                'option_a': '1080 × 1080 px',
                'option_b': '720 × 720 px',
                'option_c': '1920 × 1080 px',
                'option_d': '800 × 600 px',
                'correct_answer': 'A',
                'concept': 'Social Media Dimensions',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a mood board used for in graphic design?',
                'option_a': 'Tracking project deadlines',
                'option_b': 'Collecting visual references to define style and tone',
                'option_c': 'Listing client feedback',
                'option_d': 'Calculating print costs',
                'correct_answer': 'B',
                'concept': 'Design Process',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which color scheme uses colors opposite each other on the color wheel?',
                'option_a': 'Analogous',
                'option_b': 'Monochromatic',
                'option_c': 'Complementary',
                'option_d': 'Triadic',
                'correct_answer': 'C',
                'concept': 'Color Theory',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Design a Complete Brand Identity Package',
        'description': (
            'Develop a full brand identity for a fictional company including: '
            'logo variants, color palette, typography guide, business card, '
            'letterhead, and a brand style guide PDF. Present as a professional portfolio piece.'
        ),
        'domain': 'Graphic Design',
        'difficulty': 'Advanced',
        'task_type': 'Design',
        'required_skills': ['Adobe Illustrator', 'Adobe InDesign', 'Brand Strategy', 'Typography', 'Color Theory'],
        'learning_outcomes': [
            'Create a professional brand style guide',
            'Design multi-format deliverables',
            'Apply advanced typography and layout principles',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What is a brand style guide?',
                'option_a': 'A list of company employees',
                'option_b': 'A document defining visual and verbal brand standards',
                'option_c': 'A social media content calendar',
                'option_d': 'A project timeline',
                'correct_answer': 'B',
                'concept': 'Brand Identity',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is the purpose of negative space in logo design?',
                'option_a': 'To fill unused areas with color',
                'option_b': 'To create visual interest and hidden meaning through empty space',
                'option_c': 'To add more text',
                'option_d': 'To reduce file size',
                'correct_answer': 'B',
                'concept': 'Logo Design',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'Which Adobe app is best for multi-page brand documents?',
                'option_a': 'Photoshop',
                'option_b': 'Illustrator',
                'option_c': 'InDesign',
                'option_d': 'Lightroom',
                'correct_answer': 'C',
                'concept': 'Design Tools',
                'difficulty_weight': 1.0,
            },
        ],
    },

    # ── CONTENT WRITING ─────────────────────────────────────────────────────
    {
        'title': 'Write a 500-Word SEO Blog Post',
        'description': (
            'Write an SEO-optimized blog post of at least 500 words on a topic '
            'of your choice. Include a compelling headline, meta description, '
            'proper use of H2/H3 headings, and natural keyword placement. '
            'Use Yoast SEO guidelines.'
        ),
        'domain': 'Content Writing',
        'difficulty': 'Beginner',
        'task_type': 'Content',
        'required_skills': ['SEO Writing', 'Grammar', 'Research'],
        'learning_outcomes': [
            'Structure an SEO-optimized article',
            'Write effective meta descriptions',
            'Use headings and keywords naturally',
        ],
        'estimated_duration': 120,
        'mcqs': [
            {
                'question_text': 'What is the ideal length for a blog post meta description?',
                'option_a': '50–80 characters',
                'option_b': '150–160 characters',
                'option_c': '300–400 characters',
                'option_d': '500+ characters',
                'correct_answer': 'B',
                'concept': 'SEO',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is keyword stuffing?',
                'option_a': 'Using keywords naturally in content',
                'option_b': 'Overusing keywords to manipulate search rankings',
                'option_c': 'Adding keywords to image alt text',
                'option_d': 'Placing keywords in the title only',
                'correct_answer': 'B',
                'concept': 'SEO Best Practices',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which heading tag should be used for the main article title?',
                'option_a': 'H2',
                'option_b': 'H3',
                'option_c': 'H1',
                'option_d': 'H4',
                'correct_answer': 'C',
                'concept': 'HTML Structure',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Create a 5-Email Drip Campaign',
        'description': (
            'Write a 5-email welcome/nurture drip campaign for a SaaS product. '
            'Each email should have a clear subject line, a single CTA, '
            'and progress logically from introduction to conversion. '
            'Focus on tone, clarity, and engagement.'
        ),
        'domain': 'Content Writing',
        'difficulty': 'Intermediate',
        'task_type': 'Content',
        'required_skills': ['Email Copywriting', 'CTA Writing', 'Customer Journey Mapping'],
        'learning_outcomes': [
            'Write persuasive email sequences',
            'Craft effective subject lines and CTAs',
            'Map content to customer journey stages',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is a drip campaign?',
                'option_a': 'A single promotional email blast',
                'option_b': 'A series of automated emails sent based on schedule or actions',
                'option_c': 'An email with multiple attachments',
                'option_d': 'A daily newsletter',
                'correct_answer': 'B',
                'concept': 'Email Marketing',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which element most impacts email open rates?',
                'option_a': 'Email body length',
                'option_b': 'Number of images',
                'option_c': 'Subject line',
                'option_d': 'Font size',
                'correct_answer': 'C',
                'concept': 'Email Copywriting',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What does a CTA in email marketing stand for?',
                'option_a': 'Content Tracking Analytics',
                'option_b': 'Call To Action',
                'option_c': 'Customer Transaction Agreement',
                'option_d': 'Content Transfer Agent',
                'correct_answer': 'B',
                'concept': 'Copywriting',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Develop a Full Content Strategy for a Brand',
        'description': (
            'Create a 30-day content strategy for a fictional brand. '
            'Include: audience persona, content pillars, editorial calendar, '
            'platform-specific guidelines (blog, Instagram, LinkedIn), '
            'KPIs to measure success, and 3 full sample pieces of content.'
        ),
        'domain': 'Content Writing',
        'difficulty': 'Advanced',
        'task_type': 'Content',
        'required_skills': ['Content Strategy', 'Audience Research', 'SEO', 'Copywriting', 'Analytics'],
        'learning_outcomes': [
            'Build a data-driven content strategy',
            'Define audience personas',
            'Plan multi-platform content calendars',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What is an audience persona?',
                'option_a': 'A real customer profile from CRM',
                'option_b': 'A fictional representation of your ideal customer',
                'option_c': 'A list of competitor customers',
                'option_d': 'A social media follower demographic report',
                'correct_answer': 'B',
                'concept': 'Content Strategy',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What are content pillars?',
                'option_a': 'The physical infrastructure of a website',
                'option_b': 'Core topics a brand consistently creates content around',
                'option_c': 'The most popular social media posts',
                'option_d': 'SEO keyword lists',
                'correct_answer': 'B',
                'concept': 'Content Planning',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'Which KPI best measures content engagement?',
                'option_a': 'Domain authority',
                'option_b': 'Time on page and scroll depth',
                'option_c': 'Server uptime',
                'option_d': 'Number of published posts',
                'correct_answer': 'B',
                'concept': 'Content Analytics',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── PROGRAMMING ─────────────────────────────────────────────────────────
    {
        'title': 'Build a Personal Portfolio Website',
        'description': (
            'Create a responsive personal portfolio website using HTML, CSS, and '
            'vanilla JavaScript. Include sections: About, Skills, Projects, Contact. '
            'Must be mobile-friendly using CSS Flexbox or Grid. '
            'Deploy on GitHub Pages or Netlify.'
        ),
        'domain': 'Programming',
        'difficulty': 'Beginner',
        'task_type': 'Development',
        'required_skills': ['HTML5', 'CSS3', 'JavaScript', 'Responsive Design'],
        'learning_outcomes': [
            'Build a responsive multi-section webpage',
            'Use Flexbox and CSS Grid for layout',
            'Deploy a static site online',
        ],
        'estimated_duration': 300,
        'mcqs': [
            {
                'question_text': 'Which CSS property makes a container use Flexbox?',
                'option_a': 'display: block',
                'option_b': 'display: flex',
                'option_c': 'position: relative',
                'option_d': 'float: left',
                'correct_answer': 'B',
                'concept': 'CSS Flexbox',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What does the viewport meta tag control?',
                'option_a': 'Page background color',
                'option_b': 'How the page scales on mobile devices',
                'option_c': 'JavaScript execution speed',
                'option_d': 'Image compression',
                'correct_answer': 'B',
                'concept': 'Responsive Design',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which HTML element links an external CSS file?',
                'option_a': '<style>',
                'option_b': '<script>',
                'option_c': '<link>',
                'option_d': '<css>',
                'correct_answer': 'C',
                'concept': 'HTML Basics',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Build a REST API with Django',
        'description': (
            'Create a Django REST Framework API for a simple task manager app. '
            'Include endpoints: user registration/login (JWT), CRUD for tasks, '
            'task filtering by status. Write basic unit tests. '
            'Document endpoints with comments or Postman collection.'
        ),
        'domain': 'Programming',
        'difficulty': 'Intermediate',
        'task_type': 'Development',
        'required_skills': ['Python', 'Django', 'Django REST Framework', 'JWT', 'PostgreSQL'],
        'learning_outcomes': [
            'Build a RESTful API with authentication',
            'Implement CRUD operations',
            'Write unit tests for API endpoints',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What does REST stand for?',
                'option_a': 'Remote Execution Standard Technology',
                'option_b': 'Representational State Transfer',
                'option_c': 'Rapid Enterprise Service Toolkit',
                'option_d': 'Resource State Transformation',
                'correct_answer': 'B',
                'concept': 'REST APIs',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which HTTP method is used to update a resource partially?',
                'option_a': 'PUT',
                'option_b': 'POST',
                'option_c': 'PATCH',
                'option_d': 'GET',
                'correct_answer': 'C',
                'concept': 'HTTP Methods',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is the purpose of JWT in a REST API?',
                'option_a': 'Database connection pooling',
                'option_b': 'Stateless authentication using signed tokens',
                'option_c': 'Caching API responses',
                'option_d': 'Rate limiting requests',
                'correct_answer': 'B',
                'concept': 'Authentication',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Build a Full-Stack React + Django Application',
        'description': (
            'Build a complete full-stack application: a React frontend consuming a '
            'Django REST API backend. Features: user auth, CRUD operations, '
            'real-time feedback, deployment on a VPS or cloud platform. '
            'Include Docker setup, CI/CD basics, and production-ready settings.'
        ),
        'domain': 'Programming',
        'difficulty': 'Advanced',
        'task_type': 'Development',
        'required_skills': ['React', 'Django', 'Docker', 'PostgreSQL', 'Nginx', 'CI/CD'],
        'learning_outcomes': [
            'Integrate React frontend with a Django backend',
            'Dockerize a full-stack application',
            'Apply production security settings',
        ],
        'estimated_duration': 720,
        'mcqs': [
            {
                'question_text': 'What is the main purpose of Docker in web development?',
                'option_a': 'To write faster Python code',
                'option_b': 'To package apps with their dependencies for consistent environments',
                'option_c': 'To manage DNS settings',
                'option_d': 'To compile JavaScript',
                'correct_answer': 'B',
                'concept': 'Docker',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What does CORS stand for?',
                'option_a': 'Cross-Origin Resource Sharing',
                'option_b': 'Common Object Routing System',
                'option_c': 'Centralized Origin Request Service',
                'option_d': 'Client-Origin Response Standard',
                'correct_answer': 'A',
                'concept': 'Web Security',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'In React, what hook is used to run side effects?',
                'option_a': 'useState',
                'option_b': 'useContext',
                'option_c': 'useEffect',
                'option_d': 'useReducer',
                'correct_answer': 'C',
                'concept': 'React Hooks',
                'difficulty_weight': 1.0,
            },
        ],
    },

    # ── FREELANCING ─────────────────────────────────────────────────────────
    {
        'title': 'Create an Upwork Profile and Submit 3 Proposals',
        'description': (
            'Set up a complete Upwork freelancer profile including: professional photo, '
            'compelling bio (300+ words), skills, portfolio samples, and hourly rate. '
            'Write 3 tailored proposals for real job listings in your niche. '
            'Document what you learned about proposal writing.'
        ),
        'domain': 'Freelancing',
        'difficulty': 'Beginner',
        'task_type': 'Other',
        'required_skills': ['Proposal Writing', 'Profile Optimization', 'Communication'],
        'learning_outcomes': [
            'Build a professional freelancer profile',
            'Write targeted job proposals',
            'Understand freelance platform dynamics',
        ],
        'estimated_duration': 180,
        'mcqs': [
            {
                'question_text': 'What should a freelance proposal always include?',
                'option_a': 'Only the price',
                'option_b': 'Understanding of the project, relevant experience, timeline, and price',
                'option_c': 'A copy of your resume',
                'option_d': 'Just a greeting',
                'correct_answer': 'B',
                'concept': 'Proposal Writing',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is the Job Success Score on Upwork?',
                'option_a': 'Your hourly rate ranking',
                'option_b': 'A metric reflecting client satisfaction from past contracts',
                'option_c': 'The number of proposals sent',
                'option_d': 'Your profile view count',
                'correct_answer': 'B',
                'concept': 'Freelance Platforms',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a niche in freelancing?',
                'option_a': 'A type of payment method',
                'option_b': 'A specialised area of expertise you focus on',
                'option_c': 'A platform fee structure',
                'option_d': 'A contract template',
                'correct_answer': 'B',
                'concept': 'Freelance Strategy',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Complete a Paid Freelance Project End-to-End',
        'description': (
            'Take on a real or simulated freelance project. Complete the full workflow: '
            'client brief intake, project scoping, milestone planning, delivery, '
            'revision handling, and final invoice. Document client communication '
            'and lessons learned in a 1-page retrospective.'
        ),
        'domain': 'Freelancing',
        'difficulty': 'Intermediate',
        'task_type': 'Other',
        'required_skills': ['Client Management', 'Project Scoping', 'Invoicing', 'Communication'],
        'learning_outcomes': [
            'Manage a complete freelance project lifecycle',
            'Write professional invoices and contracts',
            'Handle revisions and client feedback professionally',
        ],
        'estimated_duration': 360,
        'mcqs': [
            {
                'question_text': 'What is scope creep in freelancing?',
                'option_a': 'When a client pays late',
                'option_b': 'When project requirements expand beyond the original agreement',
                'option_c': 'When you miss a deadline',
                'option_d': 'When a client leaves a bad review',
                'correct_answer': 'B',
                'concept': 'Project Management',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a milestone payment?',
                'option_a': 'Full payment upfront',
                'option_b': 'Payment divided into stages based on project progress',
                'option_c': 'A bonus for early delivery',
                'option_d': 'A platform processing fee',
                'correct_answer': 'B',
                'concept': 'Freelance Payments',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What should you do if a client requests work outside the agreed scope?',
                'option_a': 'Do it for free to keep the client happy',
                'option_b': 'Ignore the request',
                'option_c': 'Discuss the additional scope and negotiate revised terms',
                'option_d': 'Cancel the project immediately',
                'correct_answer': 'C',
                'concept': 'Client Management',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Build a Freelance Business System',
        'description': (
            'Design a complete system for running a freelance business: '
            'client onboarding process, contract templates, pricing strategy, '
            'portfolio website, testimonial collection system, '
            'passive income stream (template/course), and a 6-month growth plan.'
        ),
        'domain': 'Freelancing',
        'difficulty': 'Advanced',
        'task_type': 'Other',
        'required_skills': ['Business Development', 'Contract Writing', 'Pricing Strategy', 'Marketing'],
        'learning_outcomes': [
            'Build scalable freelance business processes',
            'Create client onboarding and contract systems',
            'Develop a long-term freelance growth strategy',
        ],
        'estimated_duration': 600,
        'mcqs': [
            {
                'question_text': 'What is a retainer agreement in freelancing?',
                'option_a': 'A one-time payment for a project',
                'option_b': 'A recurring monthly payment for ongoing services',
                'option_c': 'A platform subscription fee',
                'option_d': 'A legal contract to protect your IP',
                'correct_answer': 'B',
                'concept': 'Freelance Business Models',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is value-based pricing?',
                'option_a': 'Charging based on hours worked',
                'option_b': 'Charging based on the value delivered to the client',
                'option_c': 'Using the lowest market rate',
                'option_d': 'Adding a fixed markup to your costs',
                'correct_answer': 'B',
                'concept': 'Pricing Strategy',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is passive income for a freelancer?',
                'option_a': 'Income from a full-time job',
                'option_b': 'Earnings from assets like templates or courses that sell without active work',
                'option_c': 'Payment received after 30 days',
                'option_d': 'Income from referral commissions',
                'correct_answer': 'B',
                'concept': 'Business Development',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── E-COMMERCE ──────────────────────────────────────────────────────────
    {
        'title': 'Set Up a Shopify Store',
        'description': (
            'Create a fully functional Shopify store for a fictional product niche. '
            'Configure: theme, homepage, product listing (5 products with photos/descriptions), '
            'payment gateway (test mode), shipping settings, and a basic about/contact page.'
        ),
        'domain': 'E-Commerce',
        'difficulty': 'Beginner',
        'task_type': 'Other',
        'required_skills': ['Shopify', 'Product Photography', 'Copywriting'],
        'learning_outcomes': [
            'Set up a complete e-commerce store',
            'Write product descriptions that convert',
            'Configure payments and shipping',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is a SKU?',
                'option_a': 'Standard Keeping Unit',
                'option_b': 'Stock Keeping Unit',
                'option_c': 'Shop Key Utility',
                'option_d': 'Sales Knowledge Update',
                'correct_answer': 'B',
                'concept': 'E-Commerce Basics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is dropshipping?',
                'option_a': 'Delivering products by drone',
                'option_b': 'Selling products without holding inventory; supplier ships directly',
                'option_c': 'A discount pricing strategy',
                'option_d': 'A type of e-commerce subscription',
                'correct_answer': 'B',
                'concept': 'E-Commerce Models',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a conversion rate in e-commerce?',
                'option_a': 'The speed of the website',
                'option_b': 'Percentage of visitors who complete a purchase',
                'option_c': 'The currency exchange rate',
                'option_d': 'The number of products listed',
                'correct_answer': 'B',
                'concept': 'E-Commerce Metrics',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Run a Product Launch Campaign',
        'description': (
            'Plan and execute a product launch for an e-commerce item. '
            'Include: pre-launch email sequence (3 emails), social media posts, '
            'paid ads plan (Facebook/Instagram), launch day strategy, '
            'and post-launch analysis report with metrics.'
        ),
        'domain': 'E-Commerce',
        'difficulty': 'Intermediate',
        'task_type': 'Marketing',
        'required_skills': ['Email Marketing', 'Social Media Ads', 'Copywriting', 'Analytics'],
        'learning_outcomes': [
            'Plan a full product launch campaign',
            'Write pre-launch email sequences',
            'Analyze launch campaign performance',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What is cart abandonment in e-commerce?',
                'option_a': 'When a store runs out of stock',
                'option_b': 'When a customer adds items but leaves without purchasing',
                'option_c': 'When a product is returned',
                'option_d': 'When a payment fails',
                'correct_answer': 'B',
                'concept': 'E-Commerce Metrics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is ROAS?',
                'option_a': 'Return On Ad Spend',
                'option_b': 'Rate Of Ad Sales',
                'option_c': 'Revenue On Acquisition Score',
                'option_d': 'Reach Of Ad Subscribers',
                'correct_answer': 'A',
                'concept': 'Paid Advertising',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is customer lifetime value (LTV)?',
                'option_a': 'Total revenue from all customers in a year',
                'option_b': 'Predicted total revenue from a single customer over their relationship with the brand',
                'option_c': 'Average order value',
                'option_d': 'Number of repeat purchases in a month',
                'correct_answer': 'B',
                'concept': 'E-Commerce Analytics',
                'difficulty_weight': 1.5,
            },
        ],
    },
    {
        'title': 'Scale an E-Commerce Business to 6 Figures',
        'description': (
            'Create a scaling roadmap for an e-commerce store. '
            'Include: product research methodology, supplier negotiation strategy, '
            'paid ads scaling plan, email automation flows, influencer marketing plan, '
            'customer retention strategy, and financial projections for 12 months.'
        ),
        'domain': 'E-Commerce',
        'difficulty': 'Advanced',
        'task_type': 'Analysis',
        'required_skills': ['Business Strategy', 'Paid Advertising', 'Email Automation', 'Financial Modeling'],
        'learning_outcomes': [
            'Develop a data-driven e-commerce growth strategy',
            'Build automated marketing funnels',
            'Create financial projections for e-commerce',
        ],
        'estimated_duration': 600,
        'mcqs': [
            {
                'question_text': 'What is a marketing funnel?',
                'option_a': 'A tool to pour liquids in warehouses',
                'option_b': 'The journey customers take from awareness to purchase',
                'option_c': 'A type of email template',
                'option_d': 'A product pricing strategy',
                'correct_answer': 'B',
                'concept': 'Marketing Strategy',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a lookalike audience in Facebook Ads?',
                'option_a': 'People who look similar in profile photos',
                'option_b': 'An audience that shares traits with your existing customers',
                'option_c': 'A remarketing list of website visitors',
                'option_d': 'A demographic age group',
                'correct_answer': 'B',
                'concept': 'Paid Advertising',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What does AOV stand for in e-commerce?',
                'option_a': 'Annual Order Volume',
                'option_b': 'Average Order Value',
                'option_c': 'Automatic Order Verification',
                'option_d': 'Ad Optimization Value',
                'correct_answer': 'B',
                'concept': 'E-Commerce KPIs',
                'difficulty_weight': 1.2,
            },
        ],
    },

    # ── DIGITAL MARKETING ───────────────────────────────────────────────────
    {
        'title': 'Run a Google Ads Campaign',
        'description': (
            'Set up a Google Search Ads campaign for a fictional business. '
            'Include: keyword research (20+ keywords), ad copy (3 ad variations), '
            'bidding strategy selection, audience targeting, and a budget plan. '
            'Document expected KPIs: CTR, CPC, conversion rate.'
        ),
        'domain': 'Digital Marketing',
        'difficulty': 'Beginner',
        'task_type': 'Marketing',
        'required_skills': ['Google Ads', 'Keyword Research', 'Copywriting'],
        'learning_outcomes': [
            'Set up and configure a Google Search campaign',
            'Research and select relevant keywords',
            'Write high-performing ad copy',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is Quality Score in Google Ads?',
                'option_a': 'The number of clicks your ad received',
                'option_b': "Google's rating of your ad's relevance and landing page experience",
                'option_c': 'Your monthly ad budget',
                'option_d': 'The position of your ad on the page',
                'correct_answer': 'B',
                'concept': 'Google Ads',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What does CTR stand for?',
                'option_a': 'Customer Tracking Rate',
                'option_b': 'Click-Through Rate',
                'option_c': 'Campaign Traffic Report',
                'option_d': 'Cost To Reach',
                'correct_answer': 'B',
                'concept': 'Digital Marketing Metrics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a negative keyword in Google Ads?',
                'option_a': 'A keyword with low search volume',
                'option_b': 'A keyword that prevents your ad from showing for irrelevant searches',
                'option_c': 'A keyword your competitor is bidding on',
                'option_d': 'A keyword removed from your campaign',
                'correct_answer': 'B',
                'concept': 'Google Ads',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Build and Execute a Social Media Marketing Strategy',
        'description': (
            'Develop a 30-day social media marketing strategy for a brand on '
            'two platforms (Instagram + LinkedIn). Include: content calendar, '
            '15 post drafts with captions, hashtag strategy, growth tactics, '
            'engagement plan, and KPI tracking spreadsheet.'
        ),
        'domain': 'Digital Marketing',
        'difficulty': 'Intermediate',
        'task_type': 'Marketing',
        'required_skills': ['Social Media Marketing', 'Content Creation', 'Analytics', 'Copywriting'],
        'learning_outcomes': [
            'Build a complete social media strategy',
            'Create platform-specific content',
            'Track and analyze social media KPIs',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What is organic reach on social media?',
                'option_a': 'Reach achieved through paid promotions',
                'option_b': 'The number of people who see content without paid promotion',
                'option_c': 'Total number of followers',
                'option_d': 'Engagement rate percentage',
                'correct_answer': 'B',
                'concept': 'Social Media Marketing',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is A/B testing in digital marketing?',
                'option_a': 'Testing website loading speed',
                'option_b': 'Comparing two content versions to find which performs better',
                'option_c': 'Running ads on two platforms simultaneously',
                'option_d': 'Testing two payment gateways',
                'correct_answer': 'B',
                'concept': 'Marketing Optimization',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What does engagement rate measure on social media?',
                'option_a': 'Total number of posts published',
                'option_b': 'Interactions (likes, comments, shares) relative to reach or followers',
                'option_c': 'Number of paid ad clicks',
                'option_d': 'Profile visit count',
                'correct_answer': 'B',
                'concept': 'Social Media Metrics',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Full Digital Marketing Funnel with Analytics',
        'description': (
            'Design and document a complete digital marketing funnel: '
            'awareness (SEO + social), consideration (email nurture + retargeting), '
            'conversion (landing page + CRO), retention (loyalty program). '
            'Include Google Analytics 4 setup, conversion tracking, and a '
            'monthly reporting dashboard template.'
        ),
        'domain': 'Digital Marketing',
        'difficulty': 'Advanced',
        'task_type': 'Analysis',
        'required_skills': ['Google Analytics 4', 'SEO', 'Email Marketing', 'CRO', 'Paid Ads'],
        'learning_outcomes': [
            'Design a full multi-channel marketing funnel',
            'Set up GA4 and conversion tracking',
            'Optimise each funnel stage for conversions',
        ],
        'estimated_duration': 600,
        'mcqs': [
            {
                'question_text': 'What is CRO in digital marketing?',
                'option_a': 'Content Revenue Optimization',
                'option_b': 'Conversion Rate Optimization — improving the percentage of visitors who convert',
                'option_c': 'Cost Reduction Operations',
                'option_d': 'Campaign ROI Overview',
                'correct_answer': 'B',
                'concept': 'CRO',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is retargeting in digital advertising?',
                'option_a': 'Targeting a new audience segment',
                'option_b': 'Showing ads to people who previously visited your website',
                'option_c': 'Increasing your ad budget',
                'option_d': 'Changing your target demographics',
                'correct_answer': 'B',
                'concept': 'Paid Advertising',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is the marketing attribution model that gives all credit to the first touchpoint?',
                'option_a': 'Last-click attribution',
                'option_b': 'Linear attribution',
                'option_c': 'First-click attribution',
                'option_d': 'Time-decay attribution',
                'correct_answer': 'C',
                'concept': 'Marketing Analytics',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── WORDPRESS ───────────────────────────────────────────────────────────
    {
        'title': 'Build a WordPress Blog',
        'description': (
            'Install WordPress (local or live hosting) and create a blog. '
            'Configure: theme (free), 5 blog posts, categories, tags, '
            'Yoast SEO plugin, contact form (Contact Form 7), '
            'and basic security (Wordfence). Make the site mobile-responsive.'
        ),
        'domain': 'WordPress',
        'difficulty': 'Beginner',
        'task_type': 'Development',
        'required_skills': ['WordPress', 'SEO Plugins', 'Basic PHP', 'Hosting'],
        'learning_outcomes': [
            'Install and configure WordPress',
            'Customize themes and add plugins',
            'Apply basic SEO to a WordPress site',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What file contains WordPress database configuration?',
                'option_a': 'functions.php',
                'option_b': 'style.css',
                'option_c': 'wp-config.php',
                'option_d': 'index.php',
                'correct_answer': 'C',
                'concept': 'WordPress Setup',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is the purpose of functions.php in a WordPress theme?',
                'option_a': 'Store media files',
                'option_b': 'Add custom PHP functions and features to the theme',
                'option_c': 'Define CSS styles',
                'option_d': 'Configure the database connection',
                'correct_answer': 'B',
                'concept': 'WordPress Development',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a WordPress child theme?',
                'option_a': 'A theme for children\'s websites',
                'option_b': 'A theme inheriting from a parent theme, allowing safe customizations',
                'option_c': 'A backup copy of a theme',
                'option_d': 'A smaller version of a theme',
                'correct_answer': 'B',
                'concept': 'WordPress Themes',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Build a WooCommerce Store',
        'description': (
            'Create a complete e-commerce store using WordPress + WooCommerce. '
            'Include: product catalog (10 products), category pages, cart/checkout, '
            'payment gateway (test), shipping zones, coupon system, '
            'and an order confirmation email template.'
        ),
        'domain': 'WordPress',
        'difficulty': 'Intermediate',
        'task_type': 'Development',
        'required_skills': ['WooCommerce', 'WordPress', 'PHP', 'Payment Gateways'],
        'learning_outcomes': [
            'Build a functional WooCommerce store',
            'Configure products, payments, and shipping',
            'Customize WooCommerce email templates',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What is WooCommerce?',
                'option_a': 'A WordPress security plugin',
                'option_b': 'A WordPress plugin for building e-commerce stores',
                'option_c': 'A WordPress hosting service',
                'option_d': 'A WordPress theme',
                'correct_answer': 'B',
                'concept': 'WooCommerce',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which hook is commonly used in WooCommerce to add content after the product description?',
                'option_a': 'woocommerce_before_main_content',
                'option_b': 'woocommerce_after_single_product_summary',
                'option_c': 'woocommerce_cart_contents',
                'option_d': 'woocommerce_checkout_fields',
                'correct_answer': 'B',
                'concept': 'WooCommerce Development',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is a WordPress shortcode?',
                'option_a': 'A compressed PHP file',
                'option_b': 'A simple tag that outputs dynamic content in posts/pages',
                'option_c': 'A database query',
                'option_d': 'A URL slug',
                'correct_answer': 'B',
                'concept': 'WordPress Development',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Build a Custom WordPress Theme from Scratch',
        'description': (
            'Develop a fully custom WordPress theme from scratch (no page builder). '
            'Include: custom post types, custom fields (ACF), custom widgets, '
            'REST API integration, performance optimization (caching, lazy loading), '
            'and WCAG accessibility compliance.'
        ),
        'domain': 'WordPress',
        'difficulty': 'Advanced',
        'task_type': 'Development',
        'required_skills': ['PHP', 'WordPress Theme Development', 'ACF', 'REST API', 'Performance Optimization'],
        'learning_outcomes': [
            'Build a custom WordPress theme without page builders',
            'Create custom post types and fields',
            'Optimize WordPress for speed and accessibility',
        ],
        'estimated_duration': 720,
        'mcqs': [
            {
                'question_text': 'What is the WordPress Loop?',
                'option_a': 'An infinite loading animation',
                'option_b': 'The PHP code that WordPress uses to display posts',
                'option_c': 'A type of CSS animation',
                'option_d': 'A database backup process',
                'correct_answer': 'B',
                'concept': 'WordPress Theme Development',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What does ACF stand for in WordPress development?',
                'option_a': 'Automatic Content Formatting',
                'option_b': 'Advanced Custom Fields',
                'option_c': 'Admin Control Framework',
                'option_d': 'Ajax Content Fetcher',
                'correct_answer': 'B',
                'concept': 'WordPress Plugins',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is the wp_enqueue_scripts action used for?',
                'option_a': 'Running database migrations',
                'option_b': 'Properly loading CSS and JS files in WordPress',
                'option_c': 'Registering custom post types',
                'option_d': 'Creating admin menus',
                'correct_answer': 'B',
                'concept': 'WordPress Development',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── DATA ANALYTICS ──────────────────────────────────────────────────────
    {
        'title': 'Analyze a Sales Dataset with Excel',
        'description': (
            'Download a public sales dataset (e.g., from Kaggle). '
            'Perform analysis in Excel: clean data, create pivot tables, '
            'build charts (bar, line, pie), calculate KPIs (total revenue, '
            'top products, monthly trends). Present findings in a 1-page report.'
        ),
        'domain': 'Data Analytics',
        'difficulty': 'Beginner',
        'task_type': 'Analysis',
        'required_skills': ['Microsoft Excel', 'Pivot Tables', 'Data Cleaning', 'Charts'],
        'learning_outcomes': [
            'Clean and structure raw data in Excel',
            'Create meaningful pivot tables and charts',
            'Extract actionable business insights from data',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is a pivot table used for?',
                'option_a': 'Creating presentations',
                'option_b': 'Summarizing and analyzing large datasets quickly',
                'option_c': 'Designing web pages',
                'option_d': 'Writing macros',
                'correct_answer': 'B',
                'concept': 'Excel Analytics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a null value in a dataset?',
                'option_a': 'A value of zero',
                'option_b': 'A missing or undefined value',
                'option_c': 'A negative number',
                'option_d': 'A text string in a numeric column',
                'correct_answer': 'B',
                'concept': 'Data Cleaning',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which chart type is best for showing trends over time?',
                'option_a': 'Pie chart',
                'option_b': 'Bar chart',
                'option_c': 'Line chart',
                'option_d': 'Scatter plot',
                'correct_answer': 'C',
                'concept': 'Data Visualization',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Build a Business Intelligence Dashboard in Python',
        'description': (
            'Use Python (Pandas + Matplotlib/Seaborn or Plotly) to analyze a '
            'real-world dataset. Perform EDA, clean data, identify trends, '
            'and create an interactive dashboard using Plotly Dash or Streamlit. '
            'Include at least 5 visualizations and a written insights summary.'
        ),
        'domain': 'Data Analytics',
        'difficulty': 'Intermediate',
        'task_type': 'Analysis',
        'required_skills': ['Python', 'Pandas', 'Matplotlib', 'Plotly', 'Streamlit'],
        'learning_outcomes': [
            'Perform exploratory data analysis with Pandas',
            'Build interactive dashboards with Streamlit or Plotly Dash',
            'Communicate data insights visually',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What does EDA stand for in data analytics?',
                'option_a': 'Enhanced Data Architecture',
                'option_b': 'Exploratory Data Analysis',
                'option_c': 'External Data Aggregation',
                'option_d': 'Encrypted Data Access',
                'correct_answer': 'B',
                'concept': 'Data Analytics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'Which Pandas function shows basic dataset statistics (mean, std, min, max)?',
                'option_a': 'df.info()',
                'option_b': 'df.head()',
                'option_c': 'df.describe()',
                'option_d': 'df.shape()',
                'correct_answer': 'C',
                'concept': 'Pandas',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is a correlation heatmap used for?',
                'option_a': 'Displaying geographic data',
                'option_b': 'Showing relationships and correlations between numeric variables',
                'option_c': 'Visualizing time series trends',
                'option_d': 'Comparing category distributions',
                'correct_answer': 'B',
                'concept': 'Data Visualization',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'End-to-End Machine Learning Pipeline',
        'description': (
            'Build a complete ML pipeline on a business dataset: '
            'data collection, cleaning, feature engineering, model training '
            '(compare 3 algorithms), hyperparameter tuning, evaluation (F1, AUC), '
            'and model deployment as a REST API using FastAPI or Flask. '
            'Include a technical report documenting methodology and findings.'
        ),
        'domain': 'Data Analytics',
        'difficulty': 'Advanced',
        'task_type': 'Development',
        'required_skills': ['Python', 'scikit-learn', 'Feature Engineering', 'FastAPI', 'Model Deployment'],
        'learning_outcomes': [
            'Build an end-to-end ML pipeline',
            'Evaluate and compare ML models',
            'Deploy a trained model as an API',
        ],
        'estimated_duration': 720,
        'mcqs': [
            {
                'question_text': 'What is overfitting in machine learning?',
                'option_a': 'When a model performs poorly on training data',
                'option_b': 'When a model learns training data too well and performs poorly on new data',
                'option_c': 'When a model trains too slowly',
                'option_d': 'When a dataset has too many features',
                'correct_answer': 'B',
                'concept': 'Machine Learning',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What does cross-validation help prevent?',
                'option_a': 'Data leakage',
                'option_b': 'Overfitting by evaluating the model on multiple train/test splits',
                'option_c': 'Slow model training',
                'option_d': 'Missing values in the dataset',
                'correct_answer': 'B',
                'concept': 'Model Evaluation',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is feature engineering?',
                'option_a': 'Selecting which ML algorithm to use',
                'option_b': 'Creating or transforming variables to improve model performance',
                'option_c': 'Deploying a model to production',
                'option_d': 'Visualizing model predictions',
                'correct_answer': 'B',
                'concept': 'Feature Engineering',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── QUICKBOOKS ──────────────────────────────────────────────────────────
    {
        'title': 'Set Up a Company in QuickBooks Online',
        'description': (
            'Create a new company in QuickBooks Online (free trial). '
            'Configure: chart of accounts, company details, opening balances, '
            'first 10 transactions (income + expenses), run a Profit & Loss report '
            'and a Balance Sheet. Document each step with screenshots.'
        ),
        'domain': 'QuickBooks',
        'difficulty': 'Beginner',
        'task_type': 'Other',
        'required_skills': ['QuickBooks Online', 'Bookkeeping Basics', 'Chart of Accounts'],
        'learning_outcomes': [
            'Set up a new company in QuickBooks Online',
            'Record income and expense transactions',
            'Generate basic financial reports',
        ],
        'estimated_duration': 240,
        'mcqs': [
            {
                'question_text': 'What is a Chart of Accounts?',
                'option_a': 'A visual chart showing sales trends',
                'option_b': 'A list of all financial accounts used by a business',
                'option_c': 'A customer invoice template',
                'option_d': 'A payroll schedule',
                'correct_answer': 'B',
                'concept': 'Accounting Basics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What does bank reconciliation mean?',
                'option_a': 'Transferring money between accounts',
                'option_b': 'Matching your QuickBooks records with your bank statement',
                'option_c': 'Creating a new bank account',
                'option_d': 'Running payroll',
                'correct_answer': 'B',
                'concept': 'QuickBooks',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What is accounts receivable?',
                'option_a': 'Money the business owes to suppliers',
                'option_b': 'Money owed to the business by customers',
                'option_c': 'Employee payroll',
                'option_d': 'Bank loan balance',
                'correct_answer': 'B',
                'concept': 'Accounting',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Manage Payroll and Invoicing in QuickBooks',
        'description': (
            'Using QuickBooks Online, set up payroll for 3 employees, '
            'process a monthly payroll run, create and send 5 client invoices, '
            'record customer payments, manage accounts payable (3 vendor bills), '
            'and produce an Accounts Receivable Aging report.'
        ),
        'domain': 'QuickBooks',
        'difficulty': 'Intermediate',
        'task_type': 'Other',
        'required_skills': ['QuickBooks Payroll', 'Invoicing', 'Accounts Payable', 'Financial Reporting'],
        'learning_outcomes': [
            'Process payroll in QuickBooks',
            'Manage invoicing and payments',
            'Generate and interpret AR aging reports',
        ],
        'estimated_duration': 360,
        'mcqs': [
            {
                'question_text': 'What is an accounts payable aging report?',
                'option_a': 'A list of overdue customer invoices',
                'option_b': 'A report showing how long vendor bills have been outstanding',
                'option_c': 'A summary of employee salaries',
                'option_d': 'A bank statement comparison',
                'correct_answer': 'B',
                'concept': 'Financial Reporting',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is a journal entry in QuickBooks?',
                'option_a': 'A daily business diary',
                'option_b': 'A manual financial transaction recorded to adjust account balances',
                'option_c': 'An automated payment',
                'option_d': 'A tax form',
                'correct_answer': 'B',
                'concept': 'Accounting',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What does double-entry bookkeeping mean?',
                'option_a': 'Entering data twice for backup',
                'option_b': 'Every transaction affects at least two accounts (debit and credit)',
                'option_c': 'Using two accounting software programs',
                'option_d': 'Having two accountants review all records',
                'correct_answer': 'B',
                'concept': 'Bookkeeping',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Full-Year Financial Close in QuickBooks',
        'description': (
            'Simulate a full-year financial close for a small business in QuickBooks. '
            'Tasks: reconcile all accounts, adjust depreciation entries, '
            'calculate tax provisions, generate audited financial statements '
            '(P&L, Balance Sheet, Cash Flow), identify discrepancies, '
            'and prepare a management summary report.'
        ),
        'domain': 'QuickBooks',
        'difficulty': 'Advanced',
        'task_type': 'Analysis',
        'required_skills': ['QuickBooks Advanced', 'Financial Statements', 'Depreciation', 'Tax Accounting'],
        'learning_outcomes': [
            'Perform a complete year-end financial close',
            'Prepare all three core financial statements',
            'Identify and correct accounting discrepancies',
        ],
        'estimated_duration': 600,
        'mcqs': [
            {
                'question_text': 'What is depreciation in accounting?',
                'option_a': 'An increase in asset value',
                'option_b': 'The gradual reduction in value of a long-term asset over time',
                'option_c': 'A type of business loan',
                'option_d': 'A tax refund',
                'correct_answer': 'B',
                'concept': 'Accounting',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is the cash flow statement used for?',
                'option_a': 'Showing employee salaries',
                'option_b': 'Tracking actual cash inflows and outflows in a period',
                'option_c': 'Listing all company assets',
                'option_d': 'Comparing revenue to industry benchmarks',
                'correct_answer': 'B',
                'concept': 'Financial Statements',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What is the accrual accounting method?',
                'option_a': 'Recording transactions only when cash is received or paid',
                'option_b': 'Recording revenue and expenses when they are earned/incurred, regardless of cash',
                'option_c': 'Tracking only payroll expenses',
                'option_d': 'Using estimated values for all transactions',
                'correct_answer': 'B',
                'concept': 'Accounting Methods',
                'difficulty_weight': 1.5,
            },
        ],
    },

    # ── AUTOCAD ─────────────────────────────────────────────────────────────
    {
        'title': 'Draw a Floor Plan in AutoCAD',
        'description': (
            'Create a 2D floor plan of a 3-bedroom apartment in AutoCAD. '
            'Include: walls, doors, windows, room labels, and dimensions. '
            'Use layers for different elements (walls, doors, text, dimensions). '
            'Print to PDF at a standard architectural scale (1:100).'
        ),
        'domain': 'AutoCAD',
        'difficulty': 'Beginner',
        'task_type': 'Design',
        'required_skills': ['AutoCAD 2D', 'Layers', 'Dimensioning', 'Architectural Drawing'],
        'learning_outcomes': [
            'Create accurate 2D technical drawings',
            'Use layers to organise drawing elements',
            'Apply architectural scales and dimensioning',
        ],
        'estimated_duration': 300,
        'mcqs': [
            {
                'question_text': 'What is a layer in AutoCAD?',
                'option_a': 'A type of 3D solid',
                'option_b': 'An organizational tool to group and control drawing elements',
                'option_c': 'A printing setting',
                'option_d': 'A file format',
                'correct_answer': 'B',
                'concept': 'AutoCAD Basics',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What does the TRIM command do in AutoCAD?',
                'option_a': 'Copies an object',
                'option_b': 'Removes portions of objects that cross a cutting edge',
                'option_c': 'Rotates an object',
                'option_d': 'Changes object color',
                'correct_answer': 'B',
                'concept': 'AutoCAD Commands',
                'difficulty_weight': 1.0,
            },
            {
                'question_text': 'What file extension does AutoCAD use for drawings?',
                'option_a': '.pdf',
                'option_b': '.dwg',
                'option_c': '.psd',
                'option_d': '.dxf',
                'correct_answer': 'B',
                'concept': 'AutoCAD Files',
                'difficulty_weight': 1.0,
            },
        ],
    },
    {
        'title': 'Create a Mechanical Part Drawing with Tolerances',
        'description': (
            'Design a mechanical part (bracket or shaft) in AutoCAD 2D. '
            'Include: multiple views (front, top, side), GD&T tolerances, '
            'surface finish symbols, bill of materials table, '
            'and a title block following ISO standards. Export as PDF and DWG.'
        ),
        'domain': 'AutoCAD',
        'difficulty': 'Intermediate',
        'task_type': 'Design',
        'required_skills': ['AutoCAD 2D', 'GD&T', 'Engineering Drawing Standards', 'Dimensioning'],
        'learning_outcomes': [
            'Create engineering drawings with tolerances',
            'Apply GD&T symbols and standards',
            'Produce ISO-compliant title blocks',
        ],
        'estimated_duration': 480,
        'mcqs': [
            {
                'question_text': 'What does GD&T stand for?',
                'option_a': 'General Drawing & Tolerance',
                'option_b': 'Geometric Dimensioning and Tolerancing',
                'option_c': 'Grid Design and Technique',
                'option_d': 'Global Drawing Template',
                'correct_answer': 'B',
                'concept': 'Engineering Drawing',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is the OFFSET command used for in AutoCAD?',
                'option_a': 'Moving an object to a new location',
                'option_b': 'Creating a parallel copy of an object at a specified distance',
                'option_c': 'Rotating an object',
                'option_d': 'Scaling an object',
                'correct_answer': 'B',
                'concept': 'AutoCAD Commands',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is a viewport in AutoCAD paper space?',
                'option_a': 'A 3D camera view',
                'option_b': 'A window that displays model space drawings within a layout for printing',
                'option_c': 'A zoom level setting',
                'option_d': 'A layer visibility toggle',
                'correct_answer': 'B',
                'concept': 'AutoCAD Layout',
                'difficulty_weight': 1.2,
            },
        ],
    },
    {
        'title': 'Design a 3D Building Model in AutoCAD',
        'description': (
            'Create a 3D model of a small commercial building using AutoCAD 3D tools. '
            'Model: exterior walls, roof, doors, windows, and basic interior layout. '
            'Apply materials/renders, produce elevation drawings from the 3D model, '
            'and export a walkthrough presentation.'
        ),
        'domain': 'AutoCAD',
        'difficulty': 'Advanced',
        'task_type': 'Design',
        'required_skills': ['AutoCAD 3D', '3D Modeling', 'Rendering', 'Architectural Design'],
        'learning_outcomes': [
            'Build 3D architectural models in AutoCAD',
            'Generate 2D drawings from 3D models',
            'Apply rendering and presentation techniques',
        ],
        'estimated_duration': 720,
        'mcqs': [
            {
                'question_text': 'What is the EXTRUDE command used for in AutoCAD 3D?',
                'option_a': 'Printing a drawing',
                'option_b': 'Converting a 2D shape into a 3D solid by adding height',
                'option_c': 'Trimming lines',
                'option_d': 'Creating a mirror image',
                'correct_answer': 'B',
                'concept': 'AutoCAD 3D',
                'difficulty_weight': 1.5,
            },
            {
                'question_text': 'What does UCS stand for in AutoCAD?',
                'option_a': 'Universal Coordinate System',
                'option_b': 'User Coordinate System',
                'option_c': 'Unified CAD Standard',
                'option_d': 'Unit Conversion Scale',
                'correct_answer': 'B',
                'concept': 'AutoCAD 3D',
                'difficulty_weight': 1.2,
            },
            {
                'question_text': 'What is a Boolean operation in 3D CAD modeling?',
                'option_a': 'A conditional statement in AutoLISP',
                'option_b': 'Combining or subtracting 3D solids (Union, Subtract, Intersect)',
                'option_c': 'A layer management operation',
                'option_d': 'A rendering technique',
                'correct_answer': 'B',
                'concept': 'AutoCAD 3D',
                'difficulty_weight': 1.5,
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with internship tasks and MCQ questions for all 10 domains.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove all existing tasks before seeding.',
        )

    def handle(self, *args, **options):
        from apps.tasks.models import Task, TaskMCQ

        if options['clear']:
            count = Task.objects.count()
            Task.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing tasks.'))

        # Try to assign tasks to the first admin/mentor user found
        creator = (
            User.objects.filter(role='admin').first()
            or User.objects.filter(role='mentor').first()
        )
        if creator:
            self.stdout.write(f'Creating tasks as: {creator.email}')
        else:
            self.stdout.write(self.style.WARNING(
                'No admin or mentor user found — tasks will have no creator. '
                'Run create_admin first for best results.'
            ))

        created_tasks = 0
        created_mcqs = 0

        for data in SEED_TASKS:
            mcqs_data = data.pop('mcqs')

            task, created = Task.objects.get_or_create(
                title=data['title'],
                defaults={**data, 'created_by': creator},
            )

            if created:
                created_tasks += 1
                for order, mcq in enumerate(mcqs_data):
                    # Remove fields not on the TaskMCQ model
                    mcq_fields = {
                        k: v for k, v in mcq.items()
                        if k not in ('concept', 'difficulty_weight')
                    }
                    TaskMCQ.objects.create(task=task, order=order, **mcq_fields)
                    created_mcqs += 1
                self.stdout.write(
                    f'  ✓ [{task.domain}] {task.title} ({task.difficulty})'
                )
            else:
                self.stdout.write(
                    f'  – [{task.domain}] {task.title} already exists, skipping.'
                )

            data['mcqs'] = mcqs_data  # restore for potential re-run

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete: {created_tasks} tasks, {created_mcqs} MCQ questions created.'
        ))
