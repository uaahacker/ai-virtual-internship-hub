"""
PDF Export Service for Student Portfolios.

Generates a professional, multi-page portfolio/CV-style PDF using
ReportLab Platypus (pure Python — no system font or binary deps required).

Design language: clean modern CV — deep-blue branded header, score colour
coding, two-column overview, one-card-per-task project section, analytics
highlights, and a page-number footer.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable,
)

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
C_PRIMARY   = HexColor('#2563EB')   # blue-600
C_PRIMARY_D = HexColor('#1D4ED8')   # blue-700
C_ACCENT    = HexColor('#7C3AED')   # purple-600
C_GREEN     = HexColor('#16A34A')
C_YELLOW    = HexColor('#D97706')
C_RED       = HexColor('#DC2626')
C_BG_LIGHT  = HexColor('#F8FAFC')
C_BORDER    = HexColor('#CBD5E1')
C_DIVIDER   = HexColor('#E2E8F0')
C_TEXT      = HexColor('#0F172A')   # slate-900
C_TEXT_MED  = HexColor('#475569')   # slate-600
C_TEXT_SOFT = HexColor('#94A3B8')   # slate-400
C_HEADER_BG = HexColor('#1E3A8A')   # blue-900
C_HEADER_ACCENT = HexColor('#3B82F6')  # blue-500

# Page geometry
PW, PH = A4
LEFT_M  = 18 * mm
RIGHT_M = 18 * mm
TOP_M   = 22 * mm
BOT_M   = 20 * mm
CONTENT_W = PW - LEFT_M - RIGHT_M


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GRADE_MAP = [
    (90, 'Distinction'),
    (80, 'A'),
    (70, 'B'),
    (60, 'C'),
    (0,  'D'),
]

_GRADE_COLORS = {
    'Distinction': C_ACCENT,
    'A':           C_GREEN,
    'B':           C_PRIMARY,
    'C':           C_YELLOW,
    'D':           C_RED,
}


def _score_grade(score):
    """Return grade letter for a 0-100 score."""
    for threshold, grade in _GRADE_MAP:
        if score >= threshold:
            return grade
    return 'D'


def _score_color(score):
    return _GRADE_COLORS.get(_score_grade(score), C_TEXT_MED)


def _fmt_date(dt):
    if not dt:
        return ''
    return dt.strftime('%b %d, %Y')


# ---------------------------------------------------------------------------
# Style registry
# ---------------------------------------------------------------------------

def _build_styles():
    S = {}

    def ps(name, **kw):
        S[name] = ParagraphStyle(name, **kw)

    ps('cover_name',
       fontName='Helvetica-Bold', fontSize=26,
       textColor=white, spaceAfter=3)

    ps('cover_sub',
       fontName='Helvetica', fontSize=11,
       textColor=HexColor('#BFDBFE'), spaceAfter=2)

    ps('cover_meta',
       fontName='Helvetica', fontSize=9,
       textColor=HexColor('#93C5FD'))

    ps('section_label',
       fontName='Helvetica-Bold', fontSize=7.5,
       textColor=C_PRIMARY, spaceAfter=4, spaceBefore=2)

    ps('h2',
       fontName='Helvetica-Bold', fontSize=13,
       textColor=C_TEXT, spaceAfter=5, spaceBefore=8)

    ps('body',
       fontName='Helvetica', fontSize=9.5,
       textColor=C_TEXT_MED, leading=14, spaceAfter=5)

    ps('body_sm',
       fontName='Helvetica', fontSize=8.5,
       textColor=C_TEXT_MED, leading=13, spaceAfter=3)

    ps('task_title',
       fontName='Helvetica-Bold', fontSize=11,
       textColor=C_TEXT, spaceAfter=2)

    ps('task_meta',
       fontName='Helvetica', fontSize=8,
       textColor=C_TEXT_SOFT, spaceAfter=2)

    ps('feedback_italic',
       fontName='Helvetica-Oblique', fontSize=8.5,
       textColor=C_TEXT_MED, leading=13,
       leftIndent=6, spaceAfter=3)

    ps('stat_val',
       fontName='Helvetica-Bold', fontSize=18,
       textColor=C_PRIMARY, alignment=TA_CENTER)

    ps('stat_lbl',
       fontName='Helvetica', fontSize=7.5,
       textColor=C_TEXT_SOFT, alignment=TA_CENTER, spaceAfter=0)

    ps('col_head',
       fontName='Helvetica-Bold', fontSize=9,
       textColor=C_TEXT, spaceAfter=3)

    return S


# ---------------------------------------------------------------------------
# Main exporter
# ---------------------------------------------------------------------------

class PortfolioPDFExporter:

    def __init__(self, portfolio, stats, overview):
        self.portfolio = portfolio
        self.stats     = stats
        self.overview  = overview
        self.student   = portfolio.user
        self.name      = getattr(self.student, 'name', None) or self.student.email
        self.items     = list(portfolio.items.order_by('-completion_date'))
        self.S         = _build_styles()

    # ── Footer drawn on every page ──────────────────────────────────────────

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(C_TEXT_SOFT)
        canvas.drawString(LEFT_M, 12 * mm,
                          'Virtual Internship Hub  |  Confidential Student Portfolio')
        canvas.drawRightString(PW - RIGHT_M, 12 * mm,
                               f'Page {doc.page}')
        canvas.setStrokeColor(C_DIVIDER)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT_M, 14.5 * mm, PW - RIGHT_M, 14.5 * mm)
        canvas.restoreState()

    # ── Cover / header block ─────────────────────────────────────────────────

    def _cover(self):
        story = []
        S = self.S
        gen_date   = datetime.now().strftime('%B %d, %Y')
        total      = self.overview.get('total_items', 0)
        avg        = self.overview.get('average_score', 0.0)
        best       = self.stats.get('max_score', 0)
        n_domains  = len(self.stats.get('by_domain', {}))
        summary    = self.overview.get('summary_sentence', '')

        # --- Dark-blue header band -------------------------------------------
        header_inner = [
            [Paragraph(self.name, S['cover_name'])],
            [Paragraph('Student Portfolio  |  Virtual Internship Hub', S['cover_sub'])],
            [Spacer(1, 2 * mm)],
            [Paragraph(f'Generated on {gen_date}', S['cover_meta'])],
        ]
        header_tbl = Table(header_inner, colWidths=[CONTENT_W])
        header_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), C_HEADER_BG),
            ('TOPPADDING',    (0, 0), (0, 0),   8 * mm),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6 * mm),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8 * mm),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8 * mm),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 4 * mm))

        # --- Four-stat row ---------------------------------------------------
        col_w = CONTENT_W / 4
        stat_data = [[
            Paragraph(str(total),          S['stat_val']),
            Paragraph(f'{avg:.1f}%',       S['stat_val']),
            Paragraph(f'{best:.1f}%' if best else '—', S['stat_val']),
            Paragraph(str(n_domains),      S['stat_val']),
        ], [
            Paragraph('Tasks Completed',   S['stat_lbl']),
            Paragraph('Average Score',     S['stat_lbl']),
            Paragraph('Best Score',        S['stat_lbl']),
            Paragraph('Domains',           S['stat_lbl']),
        ]]
        stat_tbl = Table(stat_data, colWidths=[col_w] * 4,
                         rowHeights=[8 * mm, 5 * mm])
        stat_tbl.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), C_BG_LIGHT),
            ('BOX',          (0, 0), (-1, -1), 0.5, C_BORDER),
            ('LINEAFTER',    (0, 0), (2, 1),   0.5, C_BORDER),
            ('TOPPADDING',   (0, 0), (-1, -1), 3 * mm),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 3 * mm),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(stat_tbl)
        story.append(Spacer(1, 4 * mm))

        if summary:
            story.append(Paragraph(summary, S['body']))

        return story

    # ── Skills & Strengths overview ──────────────────────────────────────────

    def _overview_section(self):
        story = []
        S = self.S
        top_domains = self.overview.get('top_domains', [])
        all_skills  = self.overview.get('all_skills', [])
        strengths   = self.overview.get('strengths_list', [])

        story.append(HRFlowable(width=CONTENT_W, thickness=1.2,
                                color=C_PRIMARY, spaceAfter=3 * mm))
        story.append(Paragraph('SKILLS &amp; STRENGTHS', S['section_label']))
        story.append(Spacer(1, 1 * mm))

        # Left column — top domains
        left = [Paragraph('<b>Top Domains</b>', S['col_head'])]
        for d in top_domains:
            left.append(Paragraph(
                f'&bull; {d["domain"]} — {d["count"]} '
                f'task{"s" if d["count"] != 1 else ""}, avg {d["avg_score"]:.1f}%',
                S['body_sm']
            ))
        if not top_domains:
            left.append(Paragraph('No domain data yet.', S['body_sm']))

        # Right column — skills + strengths
        right = []
        if all_skills:
            right.append(Paragraph('<b>Key Skills</b>', S['col_head']))
            skill_text = '  ·  '.join(s['skill'] for s in all_skills[:12])
            right.append(Paragraph(skill_text, S['body_sm']))
            right.append(Spacer(1, 3 * mm))
        if strengths:
            right.append(Paragraph('<b>Demonstrated Strengths</b>', S['col_head']))
            for s in strengths[:5]:
                right.append(Paragraph(f'+ {s}', S['body_sm']))

        half = CONTENT_W / 2 - 3 * mm
        two_col = Table([[left, right]], colWidths=[half, half])
        two_col.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 4 * mm),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEAFTER',     (0, 0), (0, -1),  0.5, C_BORDER),
        ]))
        story.append(two_col)
        story.append(Spacer(1, 4 * mm))
        return story

    # ── Performance highlights ───────────────────────────────────────────────

    def _analytics_section(self):
        story = []
        S = self.S
        grade_dist = self.stats.get('grade_distribution', {})
        trend      = self.overview.get('improvement_trend', [])

        story.append(HRFlowable(width=CONTENT_W, thickness=1.2,
                                color=C_PRIMARY, spaceAfter=3 * mm))
        story.append(Paragraph('PERFORMANCE HIGHLIGHTS', S['section_label']))
        story.append(Spacer(1, 1 * mm))

        # --- Grade distribution side-by-side with trend text ----------------
        left = [Paragraph('<b>Grade Distribution</b>', S['col_head'])]
        for grade, color in _GRADE_COLORS.items():
            count = grade_dist.get(grade, 0)
            if count:
                left.append(Paragraph(
                    f'<b>{grade}</b>  {count} task{"s" if count != 1 else ""}',
                    S['body_sm']
                ))

        right = []
        if trend and len(trend) >= 2:
            right.append(Paragraph('<b>Score Trend</b>', S['col_head']))
            first_s = trend[0]['score']
            last_s  = trend[-1]['score']
            delta   = last_s - first_s
            direction = 'improved' if delta > 0 else 'declined' if delta < 0 else 'maintained'
            right.append(Paragraph(
                f'Performance has <b>{direction}</b> from {first_s:.1f}%'
                f' to {last_s:.1f}% over {len(trend)} task{"s" if len(trend) != 1 else ""}.',
                S['body_sm']
            ))
            right.append(Spacer(1, 3 * mm))

        # top skills
        top_skills = self.stats.get('top_skills', [])
        if top_skills:
            right.append(Paragraph('<b>Most-Used Skills</b>', S['col_head']))
            right.append(Paragraph(
                '  ·  '.join(s['skill'] for s in top_skills[:6]),
                S['body_sm']
            ))

        half = CONTENT_W / 2 - 3 * mm
        two_col = Table([[left, right]], colWidths=[half, half])
        two_col.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 4 * mm),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEAFTER',     (0, 0), (0, -1),  0.5, C_BORDER),
        ]))
        story.append(two_col)
        story.append(Spacer(1, 4 * mm))
        return story

    # ── Single task card ─────────────────────────────────────────────────────

    def _task_card(self, item):
        S = self.S
        grade       = _score_grade(item.final_score)
        grade_color = _GRADE_COLORS.get(grade, C_TEXT_MED)
        score_color = _score_color(item.final_score)
        date_str    = _fmt_date(item.completion_date)

        elements = []

        # Row 1: title | grade | score
        title_data = [[
            Paragraph(item.task_title or 'Untitled Task', S['task_title']),
            Paragraph(
                f'<b>{grade}</b>',
                ParagraphStyle('gc', fontName='Helvetica-Bold', fontSize=9,
                               textColor=grade_color, alignment=TA_RIGHT)
            ),
            Paragraph(
                f'<b>{item.final_score:.1f}%</b>',
                ParagraphStyle('sc', fontName='Helvetica-Bold', fontSize=13,
                               textColor=score_color, alignment=TA_RIGHT)
            ),
        ]]
        title_tbl = Table(title_data,
                          colWidths=[CONTENT_W - 28 * mm - 20 * mm, 28 * mm, 20 * mm])
        title_tbl.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1 * mm),
        ]))
        elements.append(title_tbl)

        # Row 2: domain · difficulty · type · date
        meta_parts = [x for x in [
            item.task_domain, item.task_difficulty,
            item.task_type, date_str
        ] if x]
        if meta_parts:
            elements.append(Paragraph('  |  '.join(meta_parts), S['task_meta']))

        # Row 3: component scores
        score_parts = []
        if item.mcq_score is not None:
            score_parts.append(f'MCQ: {item.mcq_score:.1f}%')
        if item.mentor_score is not None:
            score_parts.append(f'Mentor: {item.mentor_score:.1f}%')
        if score_parts:
            elements.append(Paragraph(
                '  |  '.join(score_parts),
                ParagraphStyle('sp', fontName='Helvetica', fontSize=8,
                               textColor=C_TEXT_MED, spaceAfter=2)
            ))

        # Row 4: skills
        if item.skills_demonstrated:
            skills_text = '  ·  '.join(item.skills_demonstrated[:8])
            elements.append(Paragraph(
                f'<i>Skills:</i>  {skills_text}',
                ParagraphStyle('sk', fontName='Helvetica', fontSize=8,
                               textColor=C_TEXT_MED, spaceAfter=2)
            ))

        # Row 5: project summary
        if item.project_summary:
            elements.append(Paragraph(item.project_summary, S['body_sm']))

        # Row 6: mentor feedback quote
        if item.mentor_feedback_summary:
            elements.append(Paragraph(
                f'<i>&quot;{item.mentor_feedback_summary}&quot;</i>',
                S['feedback_italic']
            ))

        # Divider
        elements.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                                   color=C_DIVIDER,
                                   spaceBefore=3 * mm, spaceAfter=3 * mm))

        return KeepTogether(elements)

    # ── Completed projects section ───────────────────────────────────────────

    def _tasks_section(self):
        story = []
        story.append(HRFlowable(width=CONTENT_W, thickness=1.2,
                                color=C_PRIMARY, spaceAfter=3 * mm))
        story.append(Paragraph('COMPLETED PROJECTS', self.S['section_label']))
        story.append(Spacer(1, 2 * mm))

        for item in self.items:
            story.append(self._task_card(item))

        return story

    # ── Assemble document ────────────────────────────────────────────────────

    def generate(self) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=LEFT_M,
            rightMargin=RIGHT_M,
            topMargin=TOP_M,
            bottomMargin=BOT_M,
            title=f'{self.name} — Portfolio',
            author='Virtual Internship Hub',
            subject='Student Portfolio Report',
        )

        story = []
        story += self._cover()
        story.append(Spacer(1, 3 * mm))
        story += self._overview_section()
        story += self._analytics_section()
        story += self._tasks_section()

        doc.build(
            story,
            onFirstPage=self._draw_footer,
            onLaterPages=self._draw_footer,
        )
        buf.seek(0)
        return buf.read()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_portfolio_pdf(portfolio) -> bytes:
    """
    Generate a professional portfolio PDF for the given Portfolio instance.

    Args:
        portfolio: Portfolio model instance (with related items pre-fetchable)

    Returns:
        bytes: Raw PDF data ready to be sent as an HTTP response.
    """
    from .portfolio_service import PortfolioService
    stats    = PortfolioService.get_portfolio_stats(portfolio)
    overview = PortfolioService.generate_portfolio_overview(portfolio)
    return PortfolioPDFExporter(portfolio, stats, overview).generate()
