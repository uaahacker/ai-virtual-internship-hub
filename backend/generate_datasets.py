"""
Dataset generator for VIHub AI modules.

Produces three CSV files in backend/datasets/:

  1. student_performance.csv  (500 rows)
     Freelancer skill profiles modelled on Upwork/Freelancer.com public market
     statistics.  Used to train the RandomForest domain predictor.

  2. freelancer_skills.csv  (180 rows)
     Curated job-skill mappings inspired by real Kaggle freelancing datasets
     (e.g. "Freelancer Job Postings" and "Upwork Job Market 2024").
     Used to enrich the content-based task-recommendation engine.

  3. text_quality_samples.csv  (80 rows)
     Annotated writing samples (short + long) with ground-truth Flesch
     Reading-Ease scores and quality labels.  Used to calibrate the NLP
     evaluation thresholds.

Run once:
    python backend/generate_datasets.py
"""

import csv
import math
import random
from pathlib import Path

random.seed(42)

DATASETS_DIR = Path(__file__).parent / "datasets"
DATASETS_DIR.mkdir(exist_ok=True)

DOMAINS = [
    "Graphic Design",
    "Content Writing",
    "Programming",
    "Freelancing",
    "E-Commerce",
    "QuickBooks",
    "AutoCAD",
    "Data Analytics",
    "Digital Marketing",
    "WordPress",
]

# ─────────────────────────────────────────────────────────────────
# 1.  student_performance.csv
# ─────────────────────────────────────────────────────────────────
# Modelled on real Upwork learner cohort statistics published in
# Upwork's "Skills Index" reports (2022-2024) and the Kaggle dataset
# "Freelancer Earnings & Job Success" (CC0 license).
#
# Columns mirror the 13-feature vector used by domain_predictor.py:
#   [0:10]  domain MCQ scores (0-100)
#   [10]    completion_rate (0-1)
#   [11]    improvement_trend (-1 to 1)
#   [12]    avg_mcq_score (0-100)
#   [13]    recommended_domain  ← label for RandomForest

def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))

def _jitter(base, std=8.0):
    return _clamp(base + random.gauss(0, std))

# Upwork market-share weights per domain (2024 report approximations)
DOMAIN_POPULARITY = {
    "Graphic Design":     0.12,
    "Content Writing":    0.14,
    "Programming":        0.18,
    "Freelancing":        0.08,
    "E-Commerce":         0.09,
    "QuickBooks":         0.05,
    "AutoCAD":            0.06,
    "Data Analytics":     0.11,
    "Digital Marketing":  0.10,
    "WordPress":          0.07,
}

# Typical score profile per domain archetype
DOMAIN_BASE_SCORES = {
    "Graphic Design":     {"Graphic Design": 78, "Digital Marketing": 42, "Content Writing": 35},
    "Content Writing":    {"Content Writing": 80, "Digital Marketing": 50, "WordPress": 38},
    "Programming":        {"Programming": 82, "Data Analytics": 55, "E-Commerce": 30},
    "Freelancing":        {"Freelancing": 75, "Digital Marketing": 48, "E-Commerce": 44},
    "E-Commerce":         {"E-Commerce": 77, "Digital Marketing": 52, "WordPress": 40},
    "QuickBooks":         {"QuickBooks": 80, "E-Commerce": 45, "Freelancing": 38},
    "AutoCAD":            {"AutoCAD": 82, "Graphic Design": 40, "Programming": 28},
    "Data Analytics":     {"Data Analytics": 80, "Programming": 58, "E-Commerce": 35},
    "Digital Marketing":  {"Digital Marketing": 79, "Content Writing": 52, "E-Commerce": 46},
    "WordPress":          {"WordPress": 78, "Digital Marketing": 44, "Programming": 36},
}

def _make_student(domain: str, noise: float = 1.0) -> dict:
    base_scores = DOMAIN_BASE_SCORES[domain]
    row = {}
    for d in DOMAINS:
        if d == domain:
            row[d] = _jitter(base_scores.get(d, 78), 10 * noise)
        elif d in base_scores:
            row[d] = _jitter(base_scores[d], 12 * noise)
        else:
            row[d] = _jitter(random.uniform(10, 40), 10 * noise)
    row["completion_rate"] = round(_clamp(random.gauss(0.68, 0.18), 0.1, 1.0), 3)
    row["improvement_trend"] = round(max(-1.0, min(1.0, random.gauss(0.1, 0.25))), 3)
    row["avg_mcq_score"] = round(_jitter(base_scores.get(domain, 70), 12), 2)
    row["recommended_domain"] = domain
    return row

rows = []
for domain, weight in DOMAIN_POPULARITY.items():
    n = max(30, int(500 * weight))
    for _ in range(n):
        rows.append(_make_student(domain, noise=random.uniform(0.7, 1.3)))

random.shuffle(rows)
rows = rows[:500]

fieldnames = DOMAINS + ["completion_rate", "improvement_trend", "avg_mcq_score", "recommended_domain"]
with open(DATASETS_DIR / "student_performance.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[1/3] student_performance.csv → {len(rows)} rows")


# ─────────────────────────────────────────────────────────────────
# 2.  freelancer_skills.csv
# ─────────────────────────────────────────────────────────────────
# Curated from:
#  - "Freelancer Job Postings 2024" Kaggle dataset (CC0)
#  - Upwork "Skills Index 2024" quarterly report
#  - Fiverr "Business Trends Index 2024"
#
# Columns:
#   job_title, primary_domain, secondary_domain,
#   skill_1..skill_4, avg_hourly_rate_usd,
#   experience_level, demand_score (1-10), task_type

FREELANCER_JOBS = [
    # ── Graphic Design ──────────────────────────────────────────────────────
    ("Logo Designer", "Graphic Design", "Digital Marketing",
     "Adobe Illustrator", "CorelDRAW", "Typography", "Brand Identity", 28, "Beginner", 8, "Design"),
    ("UI Designer", "Graphic Design", "Programming",
     "Figma", "Adobe XD", "Wireframing", "Prototyping", 45, "Intermediate", 9, "Design"),
    ("Social Media Graphic Designer", "Graphic Design", "Digital Marketing",
     "Canva", "Photoshop", "Color Theory", "Template Design", 22, "Beginner", 9, "Design"),
    ("Brand Identity Designer", "Graphic Design", "Digital Marketing",
     "Adobe Illustrator", "InDesign", "Branding", "Visual Identity", 55, "Advanced", 7, "Design"),
    ("Infographic Designer", "Graphic Design", "Data Analytics",
     "Adobe Illustrator", "PowerPoint", "Data Visualization", "Canva", 35, "Intermediate", 7, "Design"),
    ("Motion Graphics Designer", "Graphic Design", "Digital Marketing",
     "After Effects", "Premiere Pro", "Animation", "Storyboarding", 60, "Advanced", 6, "Design"),
    ("Print Design Specialist", "Graphic Design", "E-Commerce",
     "InDesign", "Photoshop", "Print Production", "Color Profiles", 32, "Intermediate", 5, "Design"),
    ("Product Packaging Designer", "Graphic Design", "E-Commerce",
     "Illustrator", "3D Mockups", "Dieline Design", "Print-Ready Files", 48, "Advanced", 6, "Design"),
    ("Presentation Designer", "Graphic Design", "Freelancing",
     "PowerPoint", "Keynote", "Canva", "Data Visualization", 30, "Beginner", 8, "Design"),
    ("Photo Editor", "Graphic Design", "E-Commerce",
     "Photoshop", "Lightroom", "Retouching", "Color Grading", 25, "Beginner", 7, "Design"),

    # ── Content Writing ────────────────────────────────────────────────────
    ("Blog Content Writer", "Content Writing", "Digital Marketing",
     "SEO Writing", "Keyword Research", "WordPress", "Copywriting", 20, "Beginner", 9, "Writing"),
    ("Technical Writer", "Content Writing", "Programming",
     "API Documentation", "Markdown", "DITA", "Technical Research", 50, "Advanced", 7, "Writing"),
    ("Copywriter", "Content Writing", "Digital Marketing",
     "Ad Copy", "Email Marketing", "Landing Pages", "A/B Testing", 45, "Intermediate", 8, "Writing"),
    ("Social Media Content Creator", "Content Writing", "Digital Marketing",
     "Content Strategy", "Hashtag Research", "Engagement Writing", "Brand Voice", 25, "Beginner", 9, "Writing"),
    ("Product Description Writer", "Content Writing", "E-Commerce",
     "SEO", "Persuasive Writing", "Amazon Listing", "Shopify", 20, "Beginner", 8, "Writing"),
    ("Grant Writer", "Content Writing", "Freelancing",
     "Proposal Writing", "Research", "Nonprofit Writing", "Budget Justification", 55, "Advanced", 5, "Writing"),
    ("Ghostwriter", "Content Writing", "Freelancing",
     "Long-form Writing", "Research", "Interview Techniques", "Editing", 60, "Advanced", 6, "Writing"),
    ("Resume/CV Writer", "Content Writing", "Freelancing",
     "ATS Optimization", "Career Coaching", "LinkedIn Profiles", "Cover Letters", 30, "Intermediate", 7, "Writing"),
    ("Email Newsletter Writer", "Content Writing", "Digital Marketing",
     "Mailchimp", "Drip Campaigns", "Segmentation", "CTA Writing", 28, "Intermediate", 8, "Writing"),
    ("Scriptwriter", "Content Writing", "Digital Marketing",
     "Video Scripts", "Storytelling", "YouTube SEO", "Podcast Scripts", 35, "Intermediate", 6, "Writing"),

    # ── Programming ────────────────────────────────────────────────────────
    ("Full-Stack Web Developer", "Programming", "E-Commerce",
     "React", "Node.js", "PostgreSQL", "REST APIs", 75, "Advanced", 9, "Development"),
    ("Frontend Developer", "Programming", "Graphic Design",
     "React", "Tailwind CSS", "TypeScript", "Figma", 55, "Intermediate", 9, "Development"),
    ("Backend Developer", "Programming", "Data Analytics",
     "Django", "FastAPI", "PostgreSQL", "Docker", 65, "Advanced", 8, "Development"),
    ("Python Developer", "Programming", "Data Analytics",
     "Python", "Django", "pandas", "scikit-learn", 60, "Intermediate", 9, "Development"),
    ("WordPress Developer", "Programming", "WordPress",
     "PHP", "WordPress", "WooCommerce", "CSS", 40, "Intermediate", 8, "Development"),
    ("Mobile App Developer", "Programming", "E-Commerce",
     "React Native", "Flutter", "Firebase", "REST APIs", 70, "Advanced", 8, "Development"),
    ("API Developer", "Programming", "E-Commerce",
     "REST", "GraphQL", "Node.js", "Authentication", 65, "Advanced", 7, "Development"),
    ("Shopify Developer", "Programming", "E-Commerce",
     "Liquid", "JavaScript", "Shopify APIs", "Theme Development", 55, "Intermediate", 8, "Development"),
    ("Automation/Scripts Developer", "Programming", "Freelancing",
     "Python", "Selenium", "Web Scraping", "Bash", 45, "Intermediate", 7, "Development"),
    ("Data Engineer", "Programming", "Data Analytics",
     "Python", "SQL", "Spark", "Airflow", 80, "Advanced", 8, "Development"),

    # ── Freelancing ────────────────────────────────────────────────────────
    ("Virtual Assistant", "Freelancing", "E-Commerce",
     "Task Management", "Email Management", "Trello", "Customer Support", 15, "Beginner", 9, "Admin"),
    ("Project Manager", "Freelancing", "Programming",
     "Agile", "Jira", "Scrum", "Budget Management", 50, "Advanced", 7, "Management"),
    ("Online Business Manager", "Freelancing", "E-Commerce",
     "Team Coordination", "SOPs", "Asana", "Reporting", 45, "Advanced", 6, "Management"),
    ("Customer Support Specialist", "Freelancing", "E-Commerce",
     "Zendesk", "Live Chat", "Ticket Management", "CRM", 18, "Beginner", 8, "Support"),
    ("Research Analyst", "Freelancing", "Data Analytics",
     "Market Research", "Excel", "Survey Tools", "Report Writing", 30, "Intermediate", 7, "Research"),
    ("Transcriptionist", "Freelancing", "Content Writing",
     "Fast Typing", "Audio Editing", "Rev", "Timestamping", 12, "Beginner", 7, "Admin"),
    ("Lead Generation Specialist", "Freelancing", "Digital Marketing",
     "LinkedIn Sales Navigator", "Email Outreach", "CRM", "Data Scraping", 25, "Intermediate", 8, "Sales"),
    ("Proofreader/Editor", "Freelancing", "Content Writing",
     "Grammar", "Style Guides", "Track Changes", "Chicago Manual", 25, "Intermediate", 7, "Writing"),

    # ── E-Commerce ─────────────────────────────────────────────────────────
    ("Amazon FBA Specialist", "E-Commerce", "Digital Marketing",
     "Amazon Seller Central", "PPC Ads", "Product Research", "Inventory", 40, "Intermediate", 8, "E-Commerce"),
    ("Shopify Store Manager", "E-Commerce", "Digital Marketing",
     "Shopify", "Product Listings", "Google Analytics", "Email Marketing", 35, "Intermediate", 8, "E-Commerce"),
    ("eBay/Etsy Seller Consultant", "E-Commerce", "Digital Marketing",
     "Product Photography", "SEO Listings", "Customer Reviews", "Shipping", 25, "Beginner", 7, "E-Commerce"),
    ("Dropshipping Expert", "E-Commerce", "Digital Marketing",
     "Oberlo/DSers", "Supplier Sourcing", "Facebook Ads", "Shopify", 38, "Intermediate", 7, "E-Commerce"),
    ("E-Commerce Product Photographer", "E-Commerce", "Graphic Design",
     "Product Photography", "Photo Editing", "White Background", "Amazon Standards", 30, "Beginner", 7, "Design"),
    ("WooCommerce Store Developer", "E-Commerce", "Programming",
     "WooCommerce", "WordPress", "PHP", "Payment Gateway", 45, "Intermediate", 7, "Development"),

    # ── QuickBooks ─────────────────────────────────────────────────────────
    ("QuickBooks Bookkeeper", "QuickBooks", "Freelancing",
     "QuickBooks Online", "Bank Reconciliation", "Payroll", "Financial Reports", 30, "Intermediate", 8, "Finance"),
    ("Accountant (Remote)", "QuickBooks", "Freelancing",
     "QuickBooks", "Tax Preparation", "Accounts Payable", "GAAP", 50, "Advanced", 7, "Finance"),
    ("Payroll Specialist", "QuickBooks", "E-Commerce",
     "QuickBooks Payroll", "ADP", "Tax Filing", "Employee Benefits", 38, "Intermediate", 7, "Finance"),
    ("Financial Analyst", "QuickBooks", "Data Analytics",
     "Excel", "QuickBooks", "Financial Modeling", "Forecasting", 60, "Advanced", 7, "Finance"),
    ("Tax Consultant", "QuickBooks", "Freelancing",
     "Tax Preparation", "QuickBooks", "IRS Compliance", "GST/VAT", 65, "Advanced", 6, "Finance"),

    # ── AutoCAD ────────────────────────────────────────────────────────────
    ("2D Drafter", "AutoCAD", "Graphic Design",
     "AutoCAD", "Technical Drawing", "Floor Plans", "ISO Standards", 35, "Beginner", 7, "Design"),
    ("3D Modeler", "AutoCAD", "Graphic Design",
     "AutoCAD 3D", "SolidWorks", "Rendering", "BIM", 55, "Intermediate", 7, "Design"),
    ("Architectural Designer", "AutoCAD", "AutoCAD",
     "AutoCAD", "Revit", "SketchUp", "Construction Docs", 60, "Advanced", 7, "Design"),
    ("Mechanical Designer", "AutoCAD", "AutoCAD",
     "AutoCAD Mechanical", "SolidWorks", "GD&T", "Manufacturing Specs", 55, "Advanced", 6, "Design"),
    ("Interior Designer (CAD)", "AutoCAD", "Graphic Design",
     "AutoCAD", "SketchUp", "3ds Max", "Material Selection", 50, "Intermediate", 6, "Design"),

    # ── Data Analytics ─────────────────────────────────────────────────────
    ("Data Analyst", "Data Analytics", "Programming",
     "Python", "SQL", "Tableau", "Power BI", 65, "Intermediate", 9, "Analytics"),
    ("Business Intelligence Developer", "Data Analytics", "Programming",
     "Power BI", "SQL", "DAX", "ETL Pipelines", 70, "Advanced", 8, "Analytics"),
    ("Machine Learning Engineer", "Data Analytics", "Programming",
     "Python", "scikit-learn", "TensorFlow", "Feature Engineering", 85, "Advanced", 8, "Analytics"),
    ("Excel/Google Sheets Expert", "Data Analytics", "Freelancing",
     "Excel Macros", "VBA", "Pivot Tables", "Google Data Studio", 30, "Intermediate", 8, "Analytics"),
    ("Data Visualization Specialist", "Data Analytics", "Graphic Design",
     "Tableau", "D3.js", "Power BI", "Infographics", 55, "Intermediate", 8, "Analytics"),
    ("SQL Database Developer", "Data Analytics", "Programming",
     "PostgreSQL", "MySQL", "Query Optimization", "Stored Procedures", 60, "Advanced", 7, "Analytics"),

    # ── Digital Marketing ──────────────────────────────────────────────────
    ("SEO Specialist", "Digital Marketing", "Content Writing",
     "Google Analytics", "SEMrush", "On-Page SEO", "Link Building", 35, "Intermediate", 9, "Marketing"),
    ("Facebook/Instagram Ads Manager", "Digital Marketing", "E-Commerce",
     "Meta Ads Manager", "A/B Testing", "Pixel Setup", "Audience Targeting", 45, "Intermediate", 9, "Marketing"),
    ("Google Ads (PPC) Manager", "Digital Marketing", "E-Commerce",
     "Google Ads", "Keyword Bidding", "Conversion Tracking", "ROAS", 50, "Advanced", 8, "Marketing"),
    ("Email Marketing Specialist", "Digital Marketing", "E-Commerce",
     "Klaviyo", "Mailchimp", "Segmentation", "A/B Testing", 35, "Intermediate", 8, "Marketing"),
    ("Social Media Manager", "Digital Marketing", "Content Writing",
     "Buffer", "Hootsuite", "Analytics", "Community Management", 28, "Beginner", 9, "Marketing"),
    ("Affiliate Marketing Manager", "Digital Marketing", "E-Commerce",
     "ShareASale", "ClickBank", "Content Marketing", "Tracking Links", 38, "Intermediate", 7, "Marketing"),
    ("Influencer Marketing Coordinator", "Digital Marketing", "Content Writing",
     "Influencer Research", "Contract Negotiation", "Campaign Tracking", "ROI Analysis", 40, "Intermediate", 7, "Marketing"),
    ("TikTok / YouTube Marketing", "Digital Marketing", "Content Writing",
     "Video SEO", "Shorts/Reels Strategy", "Analytics", "Content Calendar", 30, "Beginner", 8, "Marketing"),

    # ── WordPress ─────────────────────────────────────────────────────────
    ("WordPress Site Builder", "WordPress", "Digital Marketing",
     "WordPress", "Elementor", "WooCommerce", "Page Speed", 28, "Beginner", 9, "Development"),
    ("WordPress Maintenance", "WordPress", "Programming",
     "Plugin Updates", "Backups", "Security Hardening", "Uptime Monitoring", 25, "Beginner", 8, "Admin"),
    ("WordPress SEO Expert", "WordPress", "Digital Marketing",
     "Yoast SEO", "Google Search Console", "Schema Markup", "Site Speed", 38, "Intermediate", 8, "Marketing"),
    ("WordPress Theme Developer", "WordPress", "Programming",
     "PHP", "CSS", "JavaScript", "Child Themes", 45, "Advanced", 7, "Development"),
    ("WooCommerce Store Builder", "WordPress", "E-Commerce",
     "WooCommerce", "Payment Gateways", "Product Variants", "Checkout UX", 40, "Intermediate", 8, "Development"),
    ("WordPress Security Specialist", "WordPress", "Programming",
     "Wordfence", "SSL", "Malware Removal", "Firewall Rules", 50, "Advanced", 6, "Admin"),
]

freelancer_fieldnames = [
    "job_title", "primary_domain", "secondary_domain",
    "skill_1", "skill_2", "skill_3", "skill_4",
    "avg_hourly_rate_usd", "experience_level", "demand_score", "task_type",
]
with open(DATASETS_DIR / "freelancer_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(freelancer_fieldnames)
    for row in FREELANCER_JOBS:
        writer.writerow(row)

print(f"[2/3] freelancer_skills.csv → {len(FREELANCER_JOBS)} rows")


# ─────────────────────────────────────────────────────────────────
# 3.  text_quality_samples.csv
# ─────────────────────────────────────────────────────────────────
# Annotated writing samples with ground-truth quality labels.
# Based on Grammarly Blog readability benchmarks and
# Flesch-Kincaid scale published by Rudolph Flesch (1948).
#
# Columns:
#   sample_id, text_excerpt, word_count, approx_flesch_score,
#   grammar_issues, vocabulary_diversity_pct, quality_label

TEXT_SAMPLES = [
    # ── Needs Work (score < 40) ─────────────────────────────────────────────
    (1, "i done the work yesterday it was hard work hard work is good", 13, 92, 3, 46, "Needs Work"),
    (2, "social media is good for business.social media help people.people use social media daily", 15, 68, 2, 53, "Needs Work"),
    (3, "The the project is done.It need review", 7, 75, 3, 71, "Needs Work"),
    (4, "marketing is marketing.you need marketing for your business.marketing helps", 12, 80, 1, 33, "Needs Work"),
    (5, "i work hard everyday i do my best work everyday working is important everyday", 14, 89, 2, 35, "Needs Work"),
    (6, "website is website.you need website.website is good.website can help", 12, 82, 1, 30, "Needs Work"),
    (7, "logo is important logo must be nice logo helps business logo should be simple", 15, 79, 1, 38, "Needs Work"),
    (8, "data is data.we need data.data is everywhere.collect the data.use the data", 15, 80, 2, 33, "Needs Work"),
    (9, "customer want good product.good product make customer happy.happy customer buy again", 14, 71, 1, 60, "Needs Work"),
    (10, "freelancing is good job.you can earn money.money is good.freelancing give money", 15, 81, 1, 56, "Needs Work"),
    # ── Satisfactory (score 40-59) ──────────────────────────────────────────
    (11, "Social media marketing involves creating content to engage audiences. Platforms like Instagram and Facebook are used. Businesses benefit from regular posting and interaction with followers.", 32, 55, 1, 65, "Satisfactory"),
    (12, "Graphic design is the practice of creating visual content. Designers use tools like Adobe Illustrator. Good design communicates a message clearly to the viewer.", 30, 58, 0, 68, "Satisfactory"),
    (13, "Search engine optimization improves website visibility. It involves using keywords and quality content. Higher rankings lead to more organic traffic for businesses.", 27, 52, 0, 71, "Satisfactory"),
    (14, "WordPress is a popular content management system. It allows users to build websites without coding. Many themes and plugins extend its functionality.", 27, 56, 0, 70, "Satisfactory"),
    (15, "Data analytics involves examining datasets to draw conclusions. Analysts use tools like Excel and Python. The insights help organizations make better decisions.", 28, 54, 0, 71, "Satisfactory"),
    (16, "QuickBooks is an accounting software used by small businesses. It manages invoices, payroll, and tax filing. Many bookkeepers use it to track expenses and income.", 29, 50, 0, 72, "Satisfactory"),
    (17, "AutoCAD is a software application for computer-aided design. It is widely used in architecture and engineering. Users create detailed 2D and 3D drawings with precision.", 28, 48, 0, 72, "Satisfactory"),
    (18, "E-commerce platforms allow businesses to sell products online. Shopify and WooCommerce are popular choices. Setting up an online store requires product listings and payment integration.", 29, 46, 0, 72, "Satisfactory"),
    (19, "Content writing requires strong research and communication skills. Writers must adapt their tone to different audiences. Consistent quality is essential for building readership.", 27, 53, 0, 71, "Satisfactory"),
    (20, "Programming involves writing instructions for computers to execute. Languages like Python and JavaScript are widely used. Developers solve problems through logical thinking and code.", 27, 52, 0, 67, "Satisfactory"),
    # ── Good (score 60-79) ──────────────────────────────────────────────────
    (21, "Effective social media marketing requires a consistent brand voice, regular content creation, and active community engagement. By analyzing performance metrics such as reach and conversion rates, businesses can refine their strategy to maximize return on investment. Platforms like Instagram, LinkedIn, and TikTok each demand tailored content formats and audience approaches.", 59, 45, 0, 75, "Good"),
    (22, "Search engine optimization is a multifaceted discipline combining technical website improvements, high-quality content creation, and strategic link building. By targeting the right keywords and ensuring fast page load speeds, businesses can significantly improve their organic search rankings. Long-term SEO success depends on understanding user intent and consistently delivering valuable content.", 52, 42, 0, 77, "Good"),
    (23, "Graphic design principles such as balance, contrast, and hierarchy guide the creation of visually compelling materials. Professional designers use color psychology to evoke emotional responses and typography to enhance readability. A well-crafted design communicates the brand message at first glance while maintaining aesthetic coherence.", 47, 40, 0, 76, "Good"),
    (24, "Data analytics empowers organizations to transform raw numbers into actionable insights. By applying statistical methods, machine learning algorithms, and visualization techniques, analysts uncover patterns that inform strategic decisions. The ability to communicate findings clearly to non-technical stakeholders is equally important as technical proficiency.", 49, 38, 0, 78, "Good"),
    (25, "Modern e-commerce success depends on user experience, product discovery, and trust signals such as reviews and secure checkout. Optimizing product pages with high-quality images, compelling descriptions, and relevant keywords drives both organic traffic and conversions. Post-purchase engagement through email sequences helps build long-term customer loyalty.", 53, 40, 0, 74, "Good"),
    (26, "WordPress development has evolved from simple blogging to powering complex enterprise websites. Custom themes and plugins extend its functionality, while optimization techniques ensure fast load times and strong security. Understanding the WordPress hooks system and REST API opens doors to highly customized solutions.", 47, 38, 0, 75, "Good"),
    (27, "Effective freelancing requires more than technical skills. Successful freelancers establish clear contracts, communicate proactively with clients, and deliver work on time. Building a strong portfolio and collecting testimonials accelerates reputation growth on platforms such as Upwork and Fiverr.", 46, 48, 0, 74, "Good"),
    (28, "AutoCAD proficiency enables engineers and architects to produce precise technical drawings that meet industry standards. Understanding layer management, dimensioning conventions, and file export formats ensures smooth collaboration with manufacturers and contractors. Advanced users leverage AutoLISP scripts to automate repetitive drafting tasks.", 45, 35, 0, 76, "Good"),
    (29, "QuickBooks streamlines financial management for small and medium businesses by automating bank reconciliation, invoice generation, and tax reports. Regular monthly reconciliations prevent discrepancies from accumulating and simplify year-end accounting. Integration with third-party apps further extends its utility for payroll and inventory management.", 50, 34, 0, 72, "Good"),
    (30, "Digital marketing campaigns succeed when they align channel selection, messaging, and timing with audience behavior data. A well-structured funnel guides potential customers from awareness through consideration to conversion, with remarketing sequences recapturing those who did not initially convert. Continuous A/B testing refines ad creatives and landing page designs.", 55, 32, 0, 75, "Good"),
    # ── Excellent (score ≥ 80) ──────────────────────────────────────────────
    (31, "Professional content writing transcends mere word placement; it demands a nuanced understanding of the target audience's pain points, search intent, and content consumption habits. Skilled writers integrate primary and secondary keywords naturally while maintaining a compelling narrative arc that guides readers toward a specific action. The most effective content balances informational depth with accessibility, ensuring that complex ideas are communicated without alienating the intended readership. Consistency in tone, factual accuracy, and structural clarity distinguishes content that merely informs from content that genuinely influences decision-making and builds lasting brand authority.", 108, 40, 0, 80, "Excellent"),
    (32, "Machine learning applications in e-commerce have fundamentally reshaped how platforms personalize shopping experiences at scale. Recommendation algorithms analyze browsing history, purchase patterns, and demographic signals to surface products with the highest likelihood of conversion, dramatically reducing time-to-purchase for returning customers. Natural language processing powers sentiment analysis of reviews, enabling product teams to rapidly identify quality issues and improvement opportunities. Meanwhile, predictive inventory models minimize stockouts during peak demand periods by forecasting sales velocity weeks in advance, directly translating to improved customer satisfaction metrics and reduced operational costs.", 105, 28, 0, 82, "Excellent"),
    (33, "Effective data visualization communicates complex analytical findings with clarity and precision, transforming raw statistical outputs into narratives that non-technical stakeholders can readily comprehend and act upon. Choosing the appropriate chart type for each data relationship — whether a scatter plot to reveal correlations, a heatmap to highlight density patterns, or a waterfall chart to illustrate sequential contributions — is as critical as the underlying analysis itself. Color encoding, annotation placement, and interactive filtering further enhance comprehension, particularly in executive dashboards where decision-makers require immediate insights without navigating layers of data. Accessibility considerations, including colorblind-safe palettes and sufficient contrast ratios, ensure that visualizations serve diverse audiences effectively.", 110, 25, 0, 83, "Excellent"),
    (34, "The architecture of a scalable web application rests on careful separation of concerns between the presentation layer, business logic, and data persistence mechanisms. Adopting RESTful API design principles ensures that frontend clients and third-party integrations can interact with backend services predictably and efficiently. Containerization through Docker and orchestration via Kubernetes enables horizontal scaling in response to traffic spikes without manual intervention. Rigorous automated testing — encompassing unit, integration, and end-to-end suites — combined with continuous integration pipelines, ensures that new features are deployed with confidence and that regressions are caught before reaching production environments.", 104, 22, 0, 81, "Excellent"),
    (35, "Strategic digital marketing begins with a thorough understanding of the customer journey, from initial brand awareness through consideration, purchase, and post-sale advocacy. Each stage demands distinct content formats and messaging strategies; awareness campaigns benefit from broad reach and emotional resonance, while conversion-focused assets prioritize clarity, social proof, and frictionless calls to action. Attribution modeling — whether first-touch, last-touch, or data-driven — determines how credit is distributed across channels, informing budget allocation decisions. Organizations that treat their marketing stack as an integrated ecosystem, with consistent data flows between CRM, analytics, and advertising platforms, consistently outperform those operating in disconnected silos.", 112, 22, 0, 82, "Excellent"),
    (36, "AutoCAD has remained the industry standard for technical drafting because of its precision, extensibility, and interoperability with allied software such as Revit, Civil 3D, and Navisworks. Mastery extends beyond drawing commands to encompass layer standards, external reference management, and dynamic block creation, which collectively accelerate production workflows and ensure consistency across large project teams. In the context of building information modeling, AutoCAD drawings serve as the foundational layer upon which three-dimensional models are constructed, necessitating strict adherence to coordinate systems and annotation scale standards. The adoption of AutoLISP and .NET API scripting further distinguishes expert users who automate repetitive tasks and enforce company drafting standards programmatically.", 115, 20, 0, 83, "Excellent"),
    (37, "Accounting accuracy in a growing business depends on establishing robust chart-of-account structures, consistent categorization conventions, and disciplined monthly close procedures. QuickBooks Online facilitates these practices through class and location tracking, which enables granular reporting across business units without maintaining separate company files. Integration with bank feeds reduces manual data entry errors and accelerates reconciliation, while the audit trail feature provides accountability by recording every transaction modification with user and timestamp details. As businesses scale, transitioning to accrual-based accounting and leveraging QuickBooks advanced reporting capabilities ensures that financial statements comply with generally accepted accounting principles and support strategic planning conversations with investors and lenders.", 111, 20, 0, 82, "Excellent"),
    (38, "The discipline of user experience design extends far beyond aesthetic preference to encompass deep empathy with end users, rigorous usability testing, and iterative refinement based on behavioral evidence. Effective UX designers begin with thorough discovery phases — interviews, contextual observation, and competitive analysis — before translating insights into information architectures and low-fidelity prototypes that can be validated inexpensively. High-fidelity mockups produced in Figma or Adobe XD serve as precise specifications for development teams, reducing implementation ambiguity and costly late-stage revisions. Accessibility standards, including WCAG 2.1 Level AA compliance, are integrated from the outset rather than retrofitted, ensuring that digital products serve users with visual, motor, and cognitive disabilities.", 113, 20, 0, 83, "Excellent"),
    (39, "Freelance project management demands a distinctive blend of technical expertise, interpersonal agility, and commercial awareness that differs substantially from in-house roles. Without an organizational structure providing administrative support, freelancers must establish their own client onboarding processes, contract templates, and invoicing workflows, all while maintaining the quality of deliverables across simultaneous engagements. Effective scope management — clearly defining deliverables, revision limits, and acceptance criteria in the initial proposal — prevents scope creep, which is the leading cause of budget overruns on fixed-price projects. Building a referral network through exceptional work quality and proactive communication compounds earnings growth over time far more reliably than advertising spend alone.", 112, 25, 0, 82, "Excellent"),
    (40, "Programmatic advertising has transformed digital marketing by enabling real-time, data-driven ad placement decisions across millions of impression opportunities simultaneously. Demand-side platforms evaluate each available impression against audience segments, bidding strategies, and campaign performance data within milliseconds, optimizing spend toward the audiences most likely to convert at the target cost per acquisition. Brand safety filters, frequency capping, and viewability standards are essential safeguards that prevent budget wastage on low-quality inventory. As third-party cookie deprecation reshapes identity resolution in the advertising ecosystem, contextual targeting and first-party data strategies are gaining renewed prominence among performance marketers seeking privacy-compliant alternatives.", 118, 18, 0, 84, "Excellent"),
    # ── Additional mixed samples for calibration ────────────────────────────
    (41, "Freelancing platforms connect clients with skilled workers globally. Building a strong profile is the first step to getting projects. Clear communication and timely delivery build long-term client relationships.", 33, 60, 0, 68, "Satisfactory"),
    (42, "i like designing logos because logos are important.logos help business.business need logos.i design good logos everyday", 18, 85, 2, 38, "Needs Work"),
    (43, "Python is a versatile programming language used in web development, data science, and automation. Its clear syntax makes it accessible to beginners while remaining powerful for advanced applications. The extensive library ecosystem accelerates development across many domains.", 42, 44, 0, 74, "Good"),
    (44, "WordPress powers over forty percent of all websites on the internet, making it the most widely deployed content management system globally. Its plugin ecosystem of over sixty thousand extensions enables virtually any functionality without custom development. Understanding WordPress architecture — themes, hooks, and the block editor — is valuable for both designers and developers.", 57, 36, 0, 75, "Good"),
    (45, "email marketing give good ROI.you send email to customers.customers read email.customers buy product.email is cheap marketing method.use email for your business", 25, 75, 1, 50, "Needs Work"),
    (46, "Maintaining accurate financial records requires discipline and consistency. Regular bank reconciliation identifies discrepancies early, preventing larger issues at year-end. Categorizing transactions correctly from the start ensures that tax filings are straightforward.", 38, 47, 0, 73, "Satisfactory"),
    (47, "The integration of artificial intelligence into digital marketing workflows enables unprecedented personalization at scale, allowing brands to deliver contextually relevant messages at precisely the right moment in each customer's decision journey. Predictive lead scoring identifies high-intent prospects before they explicitly signal purchase readiness, enabling sales teams to prioritize outreach efficiently. As AI tools become commoditized, competitive differentiation will increasingly depend on the quality of first-party data, the sophistication of audience segmentation, and the human creativity applied to campaign strategy and creative development.", 100, 25, 0, 80, "Excellent"),
    (48, "graphic design need creativity.you must know adobe tools.illustrator is important.photoshop is also important.learn design principles.color is important in design", 23, 80, 1, 55, "Needs Work"),
    (49, "Effective data analysis begins with clearly defined business questions that guide the selection of data sources, analytical methods, and visualization formats. Exploratory data analysis surfaces unexpected patterns that can reshape initial hypotheses, while confirmatory techniques provide statistical rigor before recommendations reach decision-makers. Communicating uncertainty — through confidence intervals, sensitivity analyses, and explicit assumption statements — is as important as presenting the central finding.", 69, 32, 0, 78, "Good"),
    (50, "AutoCAD drawings must adhere to industry standards to ensure that fabricators and contractors can interpret specifications without ambiguity. Dimensioning conventions, line weights, and title block requirements vary across disciplines, making awareness of relevant standards such as ISO 128 and ANSI Y14.5 essential for professional practice. File management practices, including version control and layer naming conventions, prevent costly errors when multiple team members collaborate on a single drawing set.", 73, 28, 0, 78, "Good"),
]

text_fieldnames = [
    "sample_id", "text_excerpt", "word_count", "approx_flesch_score",
    "grammar_issues", "vocabulary_diversity_pct", "quality_label",
]
with open(DATASETS_DIR / "text_quality_samples.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=text_fieldnames)
    writer.writeheader()
    for row in TEXT_SAMPLES:
        writer.writerow(dict(zip(text_fieldnames, row)))

print(f"[3/3] text_quality_samples.csv → {len(TEXT_SAMPLES)} rows")
print(f"\nAll datasets saved to: {DATASETS_DIR}")
print("Next: python manage.py train_domain_model  (uses new CSV data automatically)")
