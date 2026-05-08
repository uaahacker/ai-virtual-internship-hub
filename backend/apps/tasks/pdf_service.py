"""
PDF Export Service for Student Portfolios.

Generates a professional, multi-page portfolio/CV-style PDF using
ReportLab Platypus.

Sections:
  1. Cover  — dark header, date strip, 4 coloured stat cards, summary sentence
  2. Skills & Strengths  — two-column (domains | skills + strengths)
  3. Performance Highlights — two-column (grade dist | score trend + top skills)
  4. Domain Performance Summary — alternating-row table
  5. Completed Projects — one card per task with score bar, grade badge, feedback
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
C_PRIMARY    = HexColor("#2563EB")   # blue-600
C_ACCENT     = HexColor("#7C3AED")   # purple-600
C_GREEN      = HexColor("#16A34A")   # green-600
C_YELLOW     = HexColor("#D97706")   # amber-600
C_RED        = HexColor("#DC2626")   # red-600
C_BG_LIGHT   = HexColor("#F8FAFC")   # slate-50
C_BORDER     = HexColor("#CBD5E1")   # slate-300
C_DIVIDER    = HexColor("#E2E8F0")   # slate-200
C_TEXT       = HexColor("#0F172A")   # slate-900
C_TEXT_MED   = HexColor("#475569")   # slate-600
C_TEXT_SOFT  = HexColor("#94A3B8")   # slate-400
C_HEADER_BG  = HexColor("#0F172A")   # slate-900

_GRADE_MAP = [
    (90, "Distinction"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (0,  "D"),
]

_GRADE_COLORS = {
    "Distinction": C_ACCENT,
    "A":           C_GREEN,
    "B":           C_PRIMARY,
    "C":           C_YELLOW,
    "D":           C_RED,
}

_GRADE_BG = {
    "Distinction": HexColor("#EDE9FE"),
    "A":           HexColor("#DCFCE7"),
    "B":           HexColor("#DBEAFE"),
    "C":           HexColor("#FEF3C7"),
    "D":           HexColor("#FEE2E2"),
}

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------
PW, PH       = A4                          # 210 mm x 297 mm
LEFT_M       = 18 * mm
RIGHT_M      = 18 * mm
TOP_M        = 20 * mm
BOT_M        = 22 * mm
CONTENT_W    = PW - LEFT_M - RIGHT_M      # 174 mm

# Card inner width: CONTENT_W minus L/R cell padding (5 mm each side)
CARD_PAD     = 5 * mm
CARD_INNER_W = CONTENT_W - CARD_PAD * 2   # 164 mm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_grade(score):
    for threshold, grade in _GRADE_MAP:
        if score >= threshold:
            return grade
    return "D"


def _score_color(score):
    return _GRADE_COLORS.get(_score_grade(score), C_TEXT_MED)


def _fmt_date(dt):
    if not dt:
        return ""
    return dt.strftime("%b %d, %Y")


def _score_bar(score, width):
    """Two-cell Table that renders as a filled progress bar."""
    pct    = min(100.0, max(0.0, float(score)))
    filled = width * pct / 100.0
    empty  = width - filled
    color  = C_GREEN if score >= 80 else (C_YELLOW if score >= 60 else C_RED)
    h      = 2 * mm
    if empty < 0.5:
        t = Table([[""]], colWidths=[width], rowHeights=[h])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return t
    t = Table([["", ""]], colWidths=[filled, empty], rowHeights=[h])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), color),
        ("BACKGROUND",    (1, 0), (1, 0), HexColor("#E2E8F0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return t


# ---------------------------------------------------------------------------
# Style registry
# ---------------------------------------------------------------------------

def _build_styles():
    S = {}

    def ps(name, **kw):
        S[name] = ParagraphStyle(name, **kw)

    ps("cover_name",     fontName="Helvetica-Bold", fontSize=26,
                         textColor=white, spaceAfter=3, leading=32)
    ps("cover_sub",      fontName="Helvetica", fontSize=10,
                         textColor=HexColor("#93C5FD"), leading=15)
    ps("cover_meta",     fontName="Helvetica", fontSize=8.5,
                         textColor=HexColor("#64748B"), alignment=TA_RIGHT)

    ps("sec_lbl",        fontName="Helvetica-Bold", fontSize=8,
                         textColor=white)

    ps("body",           fontName="Helvetica", fontSize=9.5,
                         textColor=C_TEXT_MED, leading=15, spaceAfter=5)
    ps("body_sm",        fontName="Helvetica", fontSize=8.5,
                         textColor=C_TEXT_MED, leading=13, spaceAfter=3)
    ps("body_sm_dark",   fontName="Helvetica", fontSize=8.5,
                         textColor=C_TEXT,     leading=13, spaceAfter=3)

    ps("task_title",     fontName="Helvetica-Bold", fontSize=11,
                         textColor=C_TEXT, spaceAfter=2, leading=15)
    ps("task_meta",      fontName="Helvetica", fontSize=8,
                         textColor=C_TEXT_SOFT, spaceAfter=3, leading=12)
    ps("feedback_q",     fontName="Helvetica-Oblique", fontSize=8.5,
                         textColor=C_TEXT_MED, leading=13)

    ps("col_head",       fontName="Helvetica-Bold", fontSize=9,
                         textColor=C_TEXT, spaceAfter=4)

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
        self.name      = getattr(self.student, "name", None) or self.student.email
        self.items     = list(portfolio.items.order_by("-completion_date"))
        self.S         = _build_styles()

    # -- Page decorations ----------------------------------------------------

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(C_PRIMARY)
        canvas.setLineWidth(1.5)
        canvas.line(LEFT_M, PH - 7 * mm, PW - RIGHT_M, PH - 7 * mm)
        canvas.setStrokeColor(C_DIVIDER)
        canvas.setLineWidth(0.4)
        canvas.line(LEFT_M, 15 * mm, PW - RIGHT_M, 15 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_TEXT_SOFT)
        canvas.drawString(LEFT_M, 11 * mm,
                          "Virtual Internship Hub  |  Confidential Student Portfolio")
        canvas.drawRightString(PW - RIGHT_M, 11 * mm, f"Page {doc.page}")
        canvas.restoreState()

    # -- Section header helper -----------------------------------------------

    def _section_hdr(self, title):
        hdr = Table(
            [[Paragraph(title, self.S["sec_lbl"])]],
            colWidths=[CONTENT_W],
        )
        hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_PRIMARY),
            ("TOPPADDING",    (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4 * mm),
        ]))
        return [Spacer(1, 4 * mm), hdr, Spacer(1, 4 * mm)]

    # -- Cover ---------------------------------------------------------------

    def _cover(self):
        story    = []
        S        = self.S
        gen_date  = datetime.now().strftime("%B %d, %Y")
        total     = self.overview.get("total_items", 0)
        avg       = self.overview.get("average_score", 0.0)
        best      = self.stats.get("max_score", 0)
        n_domains = len(self.stats.get("by_domain", {}))
        summary   = self.overview.get("summary_sentence", "")

        hdr_tbl = Table(
            [[Paragraph(self.name, S["cover_name"])],
             [Paragraph("Student Portfolio  |  Virtual Internship Hub",
                        S["cover_sub"])]],
            colWidths=[CONTENT_W],
        )
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_HEADER_BG),
            ("TOPPADDING",    (0, 0), (0, 0),   7 * mm),
            ("TOPPADDING",    (0, 1), (-1, -1), 0),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 5 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 7 * mm),
            ("LINEBELOW",     (0, -1), (-1, -1), 3, C_PRIMARY),
        ]))
        story.append(hdr_tbl)

        date_strip = Table(
            [[Paragraph(f"Generated  {gen_date}", S["cover_meta"])]],
            colWidths=[CONTENT_W],
        )
        date_strip.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_BG_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 7 * mm),
        ]))
        story.append(date_strip)
        story.append(Spacer(1, 5 * mm))

        col_w = CONTENT_W / 4

        def make_stat(val_str, label, val_color, bg_color):
            inner = Table(
                [[Paragraph(val_str,
                            ParagraphStyle("sv", fontName="Helvetica-Bold",
                                           fontSize=20, textColor=val_color,
                                           alignment=TA_CENTER, leading=24))],
                 [Paragraph(label,
                            ParagraphStyle("sl", fontName="Helvetica",
                                           fontSize=7.5, textColor=C_TEXT_SOFT,
                                           alignment=TA_CENTER, leading=11))]],
                colWidths=[col_w - 4 * mm],
            )
            inner.setStyle(TableStyle([
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ]))
            wrapper = Table([[inner]], colWidths=[col_w])
            wrapper.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), bg_color),
                ("TOPPADDING",    (0, 0), (-1, -1), 4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
                ("LEFTPADDING",   (0, 0), (-1, -1), 2 * mm),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 2 * mm),
                ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
            ]))
            return wrapper

        best_str  = f"{best:.1f}%" if best else "---"
        stats_row = Table([[
            make_stat(str(total),    "Tasks Completed", C_PRIMARY, HexColor("#EFF6FF")),
            make_stat(f"{avg:.1f}%", "Average Score",   C_GREEN,   HexColor("#F0FDF4")),
            make_stat(best_str,      "Best Score",      C_ACCENT,  HexColor("#F5F3FF")),
            make_stat(str(n_domains),"Domains",         C_YELLOW,  HexColor("#FFFBEB")),
        ]], colWidths=[col_w] * 4)
        stats_row.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        story.append(stats_row)

        if summary:
            story.append(Spacer(1, 5 * mm))
            story.append(Paragraph(summary, S["body"]))

        return story

    # -- Skills & Strengths --------------------------------------------------

    def _overview_section(self):
        story       = []
        S           = self.S
        top_domains = self.overview.get("top_domains", [])
        all_skills  = self.overview.get("all_skills", [])
        strengths   = self.overview.get("strengths_list", [])

        story += self._section_hdr("SKILLS &amp; STRENGTHS")

        left = [Paragraph("<b>Top Domains</b>", S["col_head"])]
        for d in top_domains:
            left.append(Paragraph(
                f'<b>{d["domain"]}</b>  .  {d["count"]} '
                f'task{"s" if d["count"] != 1 else ""},  avg {d["avg_score"]:.1f}%',
                S["body_sm"]
            ))
        if not top_domains:
            left.append(Paragraph("No domain data yet.", S["body_sm"]))

        right = []
        if all_skills:
            right.append(Paragraph("<b>Key Skills</b>", S["col_head"]))
            right.append(Paragraph(
                "  .  ".join(s["skill"] for s in all_skills[:12]),
                S["body_sm"]
            ))
            right.append(Spacer(1, 3 * mm))
        if strengths:
            right.append(Paragraph("<b>Demonstrated Strengths</b>", S["col_head"]))
            for s in strengths[:5]:
                right.append(Paragraph(f"+  {s}", S["body_sm"]))
        if not right:
            right.append(Paragraph(
                "Complete tasks to reveal skills and strengths.", S["body_sm"]
            ))

        half    = CONTENT_W / 2 - 3 * mm
        two_col = Table([[left, right]], colWidths=[half, half + 6 * mm])
        two_col.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (0, -1),  0),
            ("RIGHTPADDING",  (1, 0), (1, -1),  0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LINEAFTER",     (0, 0), (0, -1),  0.5, C_BORDER),
            ("LEFTPADDING",   (1, 0), (1, -1),  5 * mm),
        ]))
        story.append(two_col)
        story.append(Spacer(1, 2 * mm))
        return story

    # -- Performance Highlights ----------------------------------------------

    def _analytics_section(self):
        story      = []
        S          = self.S
        grade_dist = self.stats.get("grade_distribution", {})
        trend      = self.overview.get("improvement_trend", [])

        story += self._section_hdr("PERFORMANCE HIGHLIGHTS")

        left       = [Paragraph("<b>Grade Distribution</b>", S["col_head"])]
        has_grades = False
        for grade in ("Distinction", "A", "B", "C", "D"):
            count = grade_dist.get(grade, 0)
            if count:
                has_grades = True
                left.append(Paragraph(
                    f'<b>{grade}</b>  .  {count} task{"s" if count != 1 else ""}',
                    S["body_sm"]
                ))
        if not has_grades:
            left.append(Paragraph("No evaluations recorded yet.", S["body_sm"]))

        right = []
        if trend and len(trend) >= 2:
            right.append(Paragraph("<b>Score Trend</b>", S["col_head"]))
            first_s   = trend[0]["score"]
            last_s    = trend[-1]["score"]
            delta     = last_s - first_s
            direction = "improved" if delta > 0 else "declined" if delta < 0 else "maintained"
            sign      = "+" if delta >= 0 else ""
            right.append(Paragraph(
                f'Score has <b>{direction}</b> from <b>{first_s:.1f}%</b> to '
                f'<b>{last_s:.1f}%</b> across {len(trend)} '
                f'task{"s" if len(trend) != 1 else ""} '
                f'(<b>{sign}{delta:.1f}%</b>).',
                S["body_sm"]
            ))
            right.append(Spacer(1, 3 * mm))

        top_skills = self.stats.get("top_skills", [])
        if top_skills:
            right.append(Paragraph("<b>Most-Used Skills</b>", S["col_head"]))
            right.append(Paragraph(
                "  .  ".join(s["skill"] for s in top_skills[:6]),
                S["body_sm"]
            ))

        half    = CONTENT_W / 2 - 3 * mm
        two_col = Table([[left, right]], colWidths=[half, half + 6 * mm])
        two_col.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (0, -1),  0),
            ("RIGHTPADDING",  (1, 0), (1, -1),  0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LINEAFTER",     (0, 0), (0, -1),  0.5, C_BORDER),
            ("LEFTPADDING",   (1, 0), (1, -1),  5 * mm),
        ]))
        story.append(two_col)
        story.append(Spacer(1, 2 * mm))
        return story

    # -- Domain Performance Table --------------------------------------------

    def _domain_table(self):
        if not self.items:
            return []
        story = []
        story += self._section_hdr("DOMAIN PERFORMANCE SUMMARY")

        domain_data = {}
        for item in self.items:
            d = item.task_domain or "Unknown"
            if d not in domain_data:
                domain_data[d] = {"count": 0, "total": 0.0}
            domain_data[d]["count"] += 1
            domain_data[d]["total"] += item.final_score

        col_ws = [CONTENT_W * 0.48, CONTENT_W * 0.17,
                  CONTENT_W * 0.20, CONTENT_W * 0.15]

        def _p(text, fn="Helvetica", fs=8.5, color=C_TEXT_MED, align=TA_LEFT):
            return Paragraph(
                text,
                ParagraphStyle("dp", fontName=fn, fontSize=fs,
                               textColor=color, alignment=align, leading=13)
            )

        table_data = [[
            _p("<b>Domain</b>",    fn="Helvetica-Bold", color=white),
            _p("<b>Tasks</b>",     fn="Helvetica-Bold", color=white,  align=TA_CENTER),
            _p("<b>Avg Score</b>", fn="Helvetica-Bold", color=white,  align=TA_CENTER),
            _p("<b>Grade</b>",     fn="Helvetica-Bold", color=white,  align=TA_CENTER),
        ]]

        for domain, data in sorted(domain_data.items()):
            avg   = data["total"] / data["count"] if data["count"] > 0 else 0
            grade = _score_grade(avg)
            table_data.append([
                _p(domain,          color=C_TEXT),
                _p(str(data["count"]), align=TA_CENTER),
                _p(f"{avg:.1f}%",   fn="Helvetica-Bold",
                   color=_score_color(avg), align=TA_CENTER),
                _p(f"<b>{grade}</b>", fn="Helvetica-Bold",
                   color=_GRADE_COLORS.get(grade, C_TEXT_MED), align=TA_CENTER),
            ])

        style_cmds = [
            ("BACKGROUND",    (0, 0), (-1, 0),  C_PRIMARY),
            ("TOPPADDING",    (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), 3 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 3 * mm),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_DIVIDER),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ]
        for i in range(2, len(table_data), 2):
            style_cmds.append(("BACKGROUND", (0, i), (-1, i),
                                HexColor("#F8FAFC")))

        tbl = Table(table_data, colWidths=col_ws)
        tbl.setStyle(TableStyle(style_cmds))
        story.append(tbl)
        story.append(Spacer(1, 3 * mm))
        return story

    # -- Single task card ----------------------------------------------------

    def _task_card(self, item):
        S           = self.S
        grade       = _score_grade(item.final_score)
        grade_color = _GRADE_COLORS.get(grade, C_TEXT_MED)
        grade_bg    = _GRADE_BG.get(grade, C_BG_LIGHT)
        score_color = _score_color(item.final_score)
        date_str    = _fmt_date(item.completion_date)

        inner = []

        # Title | Grade badge | Score
        grade_box = Table(
            [[Paragraph(f"<b>{grade}</b>",
                        ParagraphStyle("gb", fontName="Helvetica-Bold",
                                       fontSize=8, textColor=grade_color,
                                       alignment=TA_CENTER))]],
            colWidths=[18 * mm],
        )
        grade_box.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), grade_bg),
            ("TOPPADDING",    (0, 0), (-1, -1), 1.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), 2 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 2 * mm),
            ("BOX",           (0, 0), (-1, -1), 0.5, grade_color),
        ]))

        title_w = CARD_INNER_W - 20 * mm - 24 * mm   # 120 mm
        hdr_row = Table(
            [[Paragraph(item.task_title or "Untitled Task", S["task_title"]),
              grade_box,
              Paragraph(
                  f"<b>{item.final_score:.1f}%</b>",
                  ParagraphStyle("sc", fontName="Helvetica-Bold", fontSize=14,
                                 textColor=score_color, alignment=TA_RIGHT,
                                 leading=18)
              )]],
            colWidths=[title_w, 20 * mm, 24 * mm],
        )
        hdr_row.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ]))
        inner.append(hdr_row)

        # Domain . difficulty . type . date
        meta_parts = [x for x in [
            item.task_domain, item.task_difficulty, item.task_type, date_str
        ] if x]
        if meta_parts:
            inner.append(Paragraph("  |  ".join(meta_parts), S["task_meta"]))

        # Score breakdown
        score_parts = []
        if item.mcq_score is not None:
            score_parts.append(f"MCQ: <b>{item.mcq_score:.1f}%</b>")
        if item.mentor_score is not None:
            score_parts.append(f"Mentor Score: <b>{item.mentor_score:.1f}%</b>")
        if score_parts:
            inner.append(Paragraph(
                "  |  ".join(score_parts),
                ParagraphStyle("sd", fontName="Helvetica", fontSize=8,
                               textColor=C_TEXT_MED, spaceAfter=2, leading=12)
            ))

        # Visual score bar
        inner.append(_score_bar(item.final_score, CARD_INNER_W * 0.65))
        inner.append(Spacer(1, 3 * mm))

        # Skills
        if item.skills_demonstrated:
            inner.append(Paragraph(
                "<i>Skills:  </i>" + "  .  ".join(item.skills_demonstrated[:8]),
                ParagraphStyle("sk", fontName="Helvetica", fontSize=8,
                               textColor=C_TEXT_MED, spaceAfter=2, leading=12)
            ))

        # Project summary
        if item.project_summary:
            inner.append(Paragraph(item.project_summary, S["body_sm"]))

        # Mentor feedback quote
        if item.mentor_feedback_summary:
            q_tbl = Table(
                [[Paragraph(
                    f'"{item.mentor_feedback_summary}"',
                    S["feedback_q"]
                )]],
                colWidths=[CARD_INNER_W - 4 * mm],
            )
            q_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#F0F9FF")),
                ("TOPPADDING",    (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("LEFTPADDING",   (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 3 * mm),
                ("LINEBEFORE",    (0, 0), (-1, -1), 2, C_PRIMARY),
            ]))
            inner.append(q_tbl)

        # Card wrapper with left accent border
        card = Table([[inner]], colWidths=[CONTENT_W])
        card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), white),
            ("TOPPADDING",    (0, 0), (-1, -1), 4 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
            ("LEFTPADDING",   (0, 0), (-1, -1), CARD_PAD),
            ("RIGHTPADDING",  (0, 0), (-1, -1), CARD_PAD),
            ("LINEBEFORE",    (0, 0), (-1, -1), 3, score_color),
            ("BOX",           (0, 0), (-1, -1), 0.4, C_BORDER),
        ]))
        return KeepTogether([card, Spacer(1, 4 * mm)])

    # -- Completed projects section ------------------------------------------

    def _tasks_section(self):
        story = []
        story += self._section_hdr("COMPLETED PROJECTS")
        if not self.items:
            story.append(
                Paragraph("No completed projects yet.", self.S["body_sm"])
            )
            return story
        for item in self.items:
            story.append(self._task_card(item))
        return story

    # -- Assemble ------------------------------------------------------------

    def generate(self) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=LEFT_M,
            rightMargin=RIGHT_M,
            topMargin=TOP_M,
            bottomMargin=BOT_M + 4 * mm,
            title=f"{self.name} --- Portfolio",
            author="Virtual Internship Hub",
            subject="Student Portfolio Report",
        )
        story = (
            self._cover()
            + self._overview_section()
            + self._analytics_section()
            + self._domain_table()
            + self._tasks_section()
        )
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
    """Generate a professional portfolio PDF for the given Portfolio instance."""
    from .portfolio_service import PortfolioService
    stats    = PortfolioService.get_portfolio_stats(portfolio)
    overview = PortfolioService.generate_portfolio_overview(portfolio)
    return PortfolioPDFExporter(portfolio, stats, overview).generate()
