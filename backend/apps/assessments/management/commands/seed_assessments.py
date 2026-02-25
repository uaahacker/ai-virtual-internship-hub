"""
Management command: seed_assessments
Creates sample assessments and MCQ questions for the prototype.

Usage:
    python manage.py seed_assessments
    python manage.py seed_assessments --clear   (removes existing then re-seeds)
"""

from django.core.management.base import BaseCommand
from apps.assessments.models import Assessment, Question


SEED_DATA = [
    {
        'title': 'Web Development Fundamentals',
        'domain': 'Programming',
        'description': 'Test your knowledge of HTML, CSS, JavaScript, and web development concepts.',
        'time_limit': 15,
        'questions': [
            {
                'text': 'What does HTML stand for?',
                'option_a': 'Hyper Text Markup Language',
                'option_b': 'High Tech Modern Language',
                'option_c': 'Hyper Transfer Markup Language',
                'option_d': 'Home Tool Markup Language',
                'correct_option': 'A',
            },
            {
                'text': 'Which CSS property is used to change the text color?',
                'option_a': 'font-color',
                'option_b': 'text-color',
                'option_c': 'color',
                'option_d': 'text-style',
                'correct_option': 'C',
            },
            {
                'text': 'Which of the following is a JavaScript framework?',
                'option_a': 'Django',
                'option_b': 'React',
                'option_c': 'Laravel',
                'option_d': 'Flask',
                'correct_option': 'B',
            },
            {
                'text': 'What does CSS stand for?',
                'option_a': 'Computer Style Sheets',
                'option_b': 'Creative Style System',
                'option_c': 'Cascading Style Sheets',
                'option_d': 'Colorful Style Sheets',
                'correct_option': 'C',
            },
            {
                'text': 'Which HTML tag is used for the largest heading?',
                'option_a': '<heading>',
                'option_b': '<h6>',
                'option_c': '<head>',
                'option_d': '<h1>',
                'correct_option': 'D',
            },
            {
                'text': 'What is the correct syntax for referring to an external script called "app.js"?',
                'option_a': '<script href="app.js">',
                'option_b': '<script name="app.js">',
                'option_c': '<script src="app.js">',
                'option_d': '<script file="app.js">',
                'correct_option': 'C',
            },
            {
                'text': 'Which operator is used for strict equality in JavaScript?',
                'option_a': '==',
                'option_b': '===',
                'option_c': '!=',
                'option_d': '=',
                'correct_option': 'B',
            },
            {
                'text': 'What does the "box model" in CSS consist of?',
                'option_a': 'Content, Padding, Border, Margin',
                'option_b': 'Header, Body, Footer, Sidebar',
                'option_c': 'Width, Height, Color, Font',
                'option_d': 'Display, Position, Float, Clear',
                'correct_option': 'A',
            },
            {
                'text': 'Which method is used to add an element at the end of an array in JavaScript?',
                'option_a': 'append()',
                'option_b': 'push()',
                'option_c': 'add()',
                'option_d': 'insert()',
                'correct_option': 'B',
            },
            {
                'text': 'What does REST stand for in web APIs?',
                'option_a': 'Representational State Transfer',
                'option_b': 'Remote Execution Standard Technology',
                'option_c': 'Rapid Enterprise Service Toolkit',
                'option_d': 'Resource State Transformation',
                'correct_option': 'A',
            },
            {
                'text': 'Which HTTP method is used to update an existing resource?',
                'option_a': 'GET',
                'option_b': 'POST',
                'option_c': 'PUT',
                'option_d': 'DELETE',
                'correct_option': 'C',
            },
            {
                'text': 'What is the purpose of the "alt" attribute in an <img> tag?',
                'option_a': 'To provide a link to another image',
                'option_b': 'To specify alternative text for the image',
                'option_c': 'To set the image alignment',
                'option_d': 'To define the image size',
                'correct_option': 'B',
            },
        ],
    },
    {
        'title': 'Content Writing Skills Assessment',
        'domain': 'Content Writing',
        'description': 'Evaluate your content writing, grammar, SEO, and copywriting knowledge.',
        'time_limit': 12,
        'questions': [
            {
                'text': 'What does SEO stand for?',
                'option_a': 'Search Engine Optimization',
                'option_b': 'Social Engagement Outreach',
                'option_c': 'Search Entry Operation',
                'option_d': 'Site Enhancement Organization',
                'correct_option': 'A',
            },
            {
                'text': 'Which of the following is the ideal length for a meta description?',
                'option_a': '50–60 characters',
                'option_b': '150–160 characters',
                'option_c': '250–300 characters',
                'option_d': '500+ characters',
                'correct_option': 'B',
            },
            {
                'text': 'What is "CTA" in content writing?',
                'option_a': 'Central Text Alignment',
                'option_b': 'Call To Action',
                'option_c': 'Content Tracking Analytics',
                'option_d': 'Creative Text Arrangement',
                'correct_option': 'B',
            },
            {
                'text': 'Which sentence is grammatically correct?',
                'option_a': 'Their going to the store.',
                'option_b': 'There going to the store.',
                'option_c': 'They\'re going to the store.',
                'option_d': 'Theyre going to the store.',
                'correct_option': 'C',
            },
            {
                'text': 'What is a "hook" in content writing?',
                'option_a': 'A paragraph at the end of an article',
                'option_b': 'An attention-grabbing opening sentence',
                'option_c': 'A citation from another source',
                'option_d': 'A keyword repeated throughout the text',
                'correct_option': 'B',
            },
            {
                'text': 'Which tool is commonly used for checking plagiarism?',
                'option_a': 'Photoshop',
                'option_b': 'Turnitin',
                'option_c': 'Slack',
                'option_d': 'Trello',
                'correct_option': 'B',
            },
            {
                'text': 'What is keyword density?',
                'option_a': 'The total number of words in a document',
                'option_b': 'The percentage of times a keyword appears relative to total word count',
                'option_c': 'The font weight of keywords in an article',
                'option_d': 'The spacing between keywords',
                'correct_option': 'B',
            },
            {
                'text': 'Which writing style is best for a professional blog post?',
                'option_a': 'Academic and formal',
                'option_b': 'Casual and conversational yet informative',
                'option_c': 'Technical jargon only',
                'option_d': 'Poetic and metaphorical',
                'correct_option': 'B',
            },
            {
                'text': 'What is "white space" in content formatting?',
                'option_a': 'Text highlighted in white',
                'option_b': 'Empty space around text elements that improves readability',
                'option_c': 'A white background color',
                'option_d': 'Hidden text on a page',
                'correct_option': 'B',
            },
            {
                'text': 'Which of the following makes a headline effective?',
                'option_a': 'Using all capital letters',
                'option_b': 'Being vague and mysterious',
                'option_c': 'Being clear, specific, and promising a benefit',
                'option_d': 'Making it as long as possible',
                'correct_option': 'C',
            },
            {
                'text': 'What is the purpose of an editorial calendar?',
                'option_a': 'To track website visitors',
                'option_b': 'To schedule and plan content publication dates',
                'option_c': 'To calculate word count',
                'option_d': 'To manage email subscriptions',
                'correct_option': 'B',
            },
            {
                'text': 'What does "evergreen content" mean?',
                'option_a': 'Content about gardening and nature',
                'option_b': 'Content that remains relevant and useful over a long period',
                'option_c': 'Content written in green font',
                'option_d': 'Content published only in spring',
                'correct_option': 'B',
            },
        ],
    },
    {
        'title': 'Graphic Design Fundamentals',
        'domain': 'Graphic Design',
        'description': 'Test your knowledge of design principles, tools, and visual communication.',
        'time_limit': 12,
        'questions': [
            {
                'text': 'What does RGB stand for in digital design?',
                'option_a': 'Red, Green, Blue',
                'option_b': 'Red, Gray, Black',
                'option_c': 'Real Graphic Blend',
                'option_d': 'Raster Grid Base',
                'correct_option': 'A',
            },
            {
                'text': 'Which file format supports transparency?',
                'option_a': 'JPEG',
                'option_b': 'PNG',
                'option_c': 'BMP',
                'option_d': 'TIFF',
                'correct_option': 'B',
            },
            {
                'text': 'What is the standard resolution for print design?',
                'option_a': '72 DPI',
                'option_b': '150 DPI',
                'option_c': '300 DPI',
                'option_d': '600 DPI',
                'correct_option': 'C',
            },
            {
                'text': 'Which principle of design refers to the arrangement of elements to create visual stability?',
                'option_a': 'Contrast',
                'option_b': 'Balance',
                'option_c': 'Repetition',
                'option_d': 'Proximity',
                'correct_option': 'B',
            },
            {
                'text': 'Which Adobe tool is primarily used for vector graphics?',
                'option_a': 'Photoshop',
                'option_b': 'Lightroom',
                'option_c': 'Illustrator',
                'option_d': 'Premiere Pro',
                'correct_option': 'C',
            },
            {
                'text': 'What is kerning in typography?',
                'option_a': 'The space between lines of text',
                'option_b': 'The space between individual characters',
                'option_c': 'The thickness of a font',
                'option_d': 'The size of a font',
                'correct_option': 'B',
            },
            {
                'text': 'Which color model is used for printing?',
                'option_a': 'RGB',
                'option_b': 'HSL',
                'option_c': 'CMYK',
                'option_d': 'HEX',
                'correct_option': 'C',
            },
            {
                'text': 'What is a mockup in graphic design?',
                'option_a': 'A finished product',
                'option_b': 'A realistic preview of how a design will look in context',
                'option_c': 'A wireframe without colors',
                'option_d': 'A font style',
                'correct_option': 'B',
            },
            {
                'text': 'Which design element is used to guide the viewer\'s eye through a composition?',
                'option_a': 'Texture',
                'option_b': 'Line',
                'option_c': 'Shape',
                'option_d': 'Visual hierarchy',
                'correct_option': 'D',
            },
            {
                'text': 'What is the difference between raster and vector graphics?',
                'option_a': 'Raster uses pixels; vector uses mathematical paths',
                'option_b': 'They are the same',
                'option_c': 'Vector uses pixels; raster uses paths',
                'option_d': 'Raster is for web only; vector is for print only',
                'correct_option': 'A',
            },
        ],
    },
    {
        'title': 'Freelancing Essentials',
        'domain': 'Freelancing',
        'description': 'Assess your understanding of freelancing platforms, client management, and business skills.',
        'time_limit': 10,
        'questions': [
            {
                'text': 'Which platform is most popular for freelance work worldwide?',
                'option_a': 'LinkedIn',
                'option_b': 'Upwork',
                'option_c': 'Facebook',
                'option_d': 'Instagram',
                'correct_option': 'B',
            },
            {
                'text': 'What should a freelancer include in their proposal?',
                'option_a': 'Only the price',
                'option_b': 'Understanding of the project, relevant skills, timeline, and price',
                'option_c': 'A copy of their resume only',
                'option_d': 'Just a greeting message',
                'correct_option': 'B',
            },
            {
                'text': 'What is a portfolio in freelancing?',
                'option_a': 'A financial investment document',
                'option_b': 'A collection of work samples showcasing your skills',
                'option_c': 'A client database',
                'option_d': 'A contract template',
                'correct_option': 'B',
            },
            {
                'text': 'What does "milestone payment" mean?',
                'option_a': 'Full payment upfront',
                'option_b': 'Payment divided into stages based on project progress',
                'option_c': 'Payment only at the end',
                'option_d': 'Bonus payment',
                'correct_option': 'B',
            },
            {
                'text': 'Which skill is most important for freelancer-client communication?',
                'option_a': 'Speed typing',
                'option_b': 'Clear and professional written communication',
                'option_c': 'Using emojis',
                'option_d': 'Speaking multiple languages',
                'correct_option': 'B',
            },
            {
                'text': 'What is the best practice when a client requests work outside the agreed scope?',
                'option_a': 'Do it for free to maintain the relationship',
                'option_b': 'Ignore the request',
                'option_c': 'Discuss the additional scope and negotiate revised terms',
                'option_d': 'Cancel the project',
                'correct_option': 'C',
            },
            {
                'text': 'Which is a DigiSkills.pk training program area?',
                'option_a': 'Cooking',
                'option_b': 'E-Commerce Management',
                'option_c': 'Fashion Design',
                'option_d': 'Architecture',
                'correct_option': 'B',
            },
            {
                'text': 'Why is niche specialization important in freelancing?',
                'option_a': 'It limits your options',
                'option_b': 'It helps you stand out and charge higher rates',
                'option_c': 'It is not important at all',
                'option_d': 'It makes you work less',
                'correct_option': 'B',
            },
            {
                'text': 'What is a Non-Disclosure Agreement (NDA)?',
                'option_a': 'A payment receipt',
                'option_b': 'A legal contract to protect confidential information',
                'option_c': 'A project proposal',
                'option_d': 'A freelancing platform policy',
                'correct_option': 'B',
            },
            {
                'text': 'What is the biggest advantage of freelancing?',
                'option_a': 'Guaranteed fixed salary',
                'option_b': 'Flexibility in choosing projects, clients, and schedule',
                'option_c': 'Company-provided equipment',
                'option_d': 'Paid vacation days',
                'correct_option': 'B',
            },
        ],
    },
    {
        'title': 'E-Commerce Knowledge Test',
        'domain': 'E-Commerce',
        'description': 'Test your understanding of online selling, platforms, and digital business.',
        'time_limit': 10,
        'questions': [
            {
                'text': 'What does B2C stand for in e-commerce?',
                'option_a': 'Business to Customer',
                'option_b': 'Business to Company',
                'option_c': 'Brand to Consumer',
                'option_d': 'Buy to Cart',
                'correct_option': 'A',
            },
            {
                'text': 'Which platform is commonly used for creating an online store?',
                'option_a': 'WordPress',
                'option_b': 'Shopify',
                'option_c': 'Slack',
                'option_d': 'Zoom',
                'correct_option': 'B',
            },
            {
                'text': 'What is dropshipping?',
                'option_a': 'Delivering products by drone',
                'option_b': 'Selling products without holding inventory; supplier ships directly',
                'option_c': 'A type of e-commerce website',
                'option_d': 'Discount selling strategy',
                'correct_option': 'B',
            },
            {
                'text': 'What is a "conversion rate" in e-commerce?',
                'option_a': 'The speed of the website',
                'option_b': 'Percentage of visitors who complete a desired action (purchase)',
                'option_c': 'The exchange rate of currency',
                'option_d': 'The number of products listed',
                'correct_option': 'B',
            },
            {
                'text': 'Which payment gateway is widely used in Pakistan for e-commerce?',
                'option_a': 'Stripe',
                'option_b': 'JazzCash / EasyPaisa',
                'option_c': 'Venmo',
                'option_d': 'Apple Pay',
                'correct_option': 'B',
            },
            {
                'text': 'What is SEO in the context of an e-commerce store?',
                'option_a': 'Selling Everything Online',
                'option_b': 'Search Engine Optimization to improve store visibility',
                'option_c': 'Standard E-commerce Operation',
                'option_d': 'Shipping and Export Office',
                'correct_option': 'B',
            },
            {
                'text': 'What does "SKU" stand for?',
                'option_a': 'Standard Keeping Unit',
                'option_b': 'Stock Keeping Unit',
                'option_c': 'Shop Key Utility',
                'option_d': 'Sales Knowledge Update',
                'correct_option': 'B',
            },
            {
                'text': 'What is the purpose of product photography in e-commerce?',
                'option_a': 'To make the website load slower',
                'option_b': 'To visually showcase products and increase sales',
                'option_c': 'To fill empty space on the page',
                'option_d': 'For social media only',
                'correct_option': 'B',
            },
            {
                'text': 'Which metric measures how often customers return to buy again?',
                'option_a': 'Bounce rate',
                'option_b': 'Customer retention rate',
                'option_c': 'Page views',
                'option_d': 'Click-through rate',
                'correct_option': 'B',
            },
            {
                'text': 'What is a shopping cart abandonment?',
                'option_a': 'When a store runs out of stock',
                'option_b': 'When a customer adds items to cart but leaves without purchasing',
                'option_c': 'When a cart is physically abandoned',
                'option_d': 'When a product is returned',
                'correct_option': 'B',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with sample assessments and MCQ questions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Remove existing assessments and questions before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Assessment.objects.count()
            Assessment.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing assessments.'))

        created_assessments = 0
        created_questions = 0

        for data in SEED_DATA:
            questions_data = data.pop('questions')

            assessment, created = Assessment.objects.get_or_create(
                title=data['title'],
                defaults=data,
            )
            if created:
                created_assessments += 1
                for idx, q in enumerate(questions_data, start=1):
                    Question.objects.create(
                        assessment=assessment,
                        order=idx,
                        **q,
                    )
                    created_questions += 1
                self.stdout.write(f'  ✓ {assessment.title} ({len(questions_data)} questions)')
            else:
                self.stdout.write(f'  – {assessment.title} already exists, skipping.')

            # Restore questions_data for potential re-run
            data['questions'] = questions_data

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete: {created_assessments} assessments, {created_questions} questions created.'
        ))
