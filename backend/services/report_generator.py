"""
Professional ESG Report Generator — ReportLab Edition
Generates publication-quality PDF reports inspired by institutional sustainability reports.
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether, PageBreak,
    Flowable, CondPageBreak
)
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors

from backend.core.config import REPORTS_DIR, ORGANIZATION, REPORT_YEAR, setup_logging

logger = setup_logging(__name__)

# ============================================================================
# COLOR PALETTE
# ============================================================================
GREEN_DARK   = HexColor("#1a472a")
GREEN_MID    = HexColor("#2d6a4f")
GREEN_LIGHT  = HexColor("#52b788")
GREEN_PALE   = HexColor("#e8f5e9")
ACCENT       = HexColor("#f4a261")
TEXT_DARK    = HexColor("#1a1a2e")
TEXT_MID     = HexColor("#374151")
TEXT_LIGHT   = HexColor("#6b7280")
BG_LIGHT     = HexColor("#f8fafb")
BORDER_CLR   = HexColor("#e5e7eb")
RED_LIGHT    = HexColor("#fee2e2")
RED_DARK     = HexColor("#991b1b")
AMBER_LIGHT  = HexColor("#fef3c7")
AMBER_DARK   = HexColor("#92400e")

PAGE_W, PAGE_H = A4


# ============================================================================
# HELPER FLOWABLES
# ============================================================================

class ColoredLine(Flowable):
    """A horizontal line with a gradient-like color."""
    def __init__(self, width, color=GREEN_LIGHT, thickness=1.5):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = thickness + 2

    def draw(self):
        c = self._doc.canv if hasattr(self, '_doc') else None
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.height / 2, self.width, self.height / 2)


class AccentBar(Flowable):
    """A left-aligned color accent bar."""
    def __init__(self, width, color=GREEN_LIGHT, height=4):
        super().__init__()
        self.width = width
        self.color = color
        self.height = height

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


class CoverPage(Flowable):
    """Full-bleed cover page drawn directly on canvas."""
    def __init__(self, org, year, topic, stats, page_w=PAGE_W, page_h=PAGE_H):
        super().__init__()
        self.org = org
        self.year = year
        self.topic = topic
        self.stats = stats
        self.width = page_w
        self.height = page_h

    def draw(self):
        c = self.canv

        # ── Green top section (60% of page) ──
        top_h = self.height * 0.60
        c.setFillColor(GREEN_DARK)
        c.rect(0, self.height - top_h, self.width, top_h, fill=1, stroke=0)

        # Decorative circles
        c.setFillColor(HexColor("#ffffff15"))
        c.circle(self.width - 25*mm, self.height - 10*mm, 55*mm, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff10"))
        c.circle(self.width - 30*mm, self.height - 50*mm, 35*mm, fill=1, stroke=0)

        # Accent bar below green section
        c.setFillColor(ACCENT)
        c.rect(0, self.height - top_h - 5, self.width, 5, fill=1, stroke=0)

        # ── Tag line ──
        c.setFillColor(HexColor("#ffffff66"))
        c.setStrokeColor(HexColor("#ffffff44"))
        c.roundRect(18*mm, self.height - 38*mm, 50*mm, 8*mm, 2, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(21*mm, self.height - 33.2*mm, "ESG SUSTAINABILITY REPORT")

        # ── Main title ──
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 28)
        title_lines = self._wrap_text(self.topic, 28, self.width - 36*mm)
        y = self.height - 55*mm
        for line in title_lines[:3]:
            c.drawString(18*mm, y, line)
            y -= 11*mm

        # ── Org name ──
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#ffffffcc"))
        c.drawString(18*mm, y - 4*mm, self.org)

        # ── Year ──
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#ffffff88"))
        c.drawString(18*mm, y - 14*mm, f"Fiscal Period: {self.year}")

        # ── Divider line ──
        c.setStrokeColor(ACCENT)
        c.setLineWidth(3)
        c.line(18*mm, y - 20*mm, 38*mm, y - 20*mm)

        # ── Bottom white section — KPI stats ──
        stats_y = self.height * 0.38
        kpis_extracted = self.stats.get("kpis_extracted", 0)
        kpis_total = self.stats.get("kpis_requested", 14)
        frameworks = self.stats.get("frameworks_count", 3)

        stat_items = [
            (str(kpis_extracted), "KPIs Extracted"),
            (str(kpis_total), "KPIs Assessed"),
            (str(frameworks), "Frameworks Mapped"),
            (str(self.year), "Reporting Period"),
        ]

        box_w = (self.width - 36*mm) / 4
        x = 18*mm
        for val, label in stat_items:
            # Left accent line
            c.setFillColor(GREEN_LIGHT)
            c.rect(x, stats_y, 3, 28, fill=1, stroke=0)

            c.setFillColor(GREEN_DARK)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(x + 6*mm, stats_y + 12, val)

            c.setFillColor(TEXT_LIGHT)
            c.setFont("Helvetica", 7)
            c.drawString(x + 6*mm, stats_y + 3, label.upper())

            x += box_w + 2*mm

        # ── Footer bar ──
        footer_y = 18*mm
        c.setStrokeColor(BORDER_CLR)
        c.setLineWidth(0.5)
        c.line(18*mm, footer_y, self.width - 18*mm, footer_y)

        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(18*mm, footer_y - 7*mm, self.org)

        date_str = datetime.now().strftime("%B %d, %Y")
        c.setFillColor(TEXT_LIGHT)
        c.setFont("Helvetica", 8)
        c.drawRightString(self.width - 18*mm, footer_y - 7*mm, f"Generated: {date_str}  |  Confidential")

    def _wrap_text(self, text, font_size, max_width):
        """Simple word-wrap for canvas text."""
        words = text.split()
        lines = []
        current = ""
        # Approximate char width
        char_w = font_size * 0.55
        max_chars = int(max_width / char_w)
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = (current + " " + word).strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


# ============================================================================
# PAGE NUMBER CANVAS
# ============================================================================
class NumberedCanvas(pdf_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        page = self._pageNumber
        if page <= 2:
            return  # Skip cover and TOC

        # Header bar
        self.setFillColor(BG_LIGHT)
        self.rect(0, PAGE_H - 18*mm, PAGE_W, 18*mm, fill=1, stroke=0)

        self.setStrokeColor(GREEN_LIGHT)
        self.setLineWidth(1.5)
        self.line(18*mm, PAGE_H - 18*mm, PAGE_W - 18*mm, PAGE_H - 18*mm)

        # Footer
        self.setFillColor(BG_LIGHT)
        self.rect(0, 0, PAGE_W, 15*mm, fill=1, stroke=0)

        self.setStrokeColor(BORDER_CLR)
        self.setLineWidth(0.5)
        self.line(18*mm, 15*mm, PAGE_W - 18*mm, 15*mm)

        self.setFillColor(TEXT_LIGHT)
        self.setFont("Helvetica", 7)
        self.drawString(18*mm, 9*mm, f"ESG Sustainability Report — {ORGANIZATION}")

        self.setFillColor(GREEN_MID)
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(PAGE_W - 18*mm, 9*mm, str(page - 2))  # page count starting from content


# ============================================================================
# STYLE SHEET
# ============================================================================
def build_styles():
    styles = getSampleStyleSheet()

    custom = {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=GREEN_DARK,
            spaceAfter=6,
            leading=24,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=TEXT_DARK,
            spaceBefore=16,
            spaceAfter=6,
            leading=16,
            leftIndent=8,
            borderPad=4,
            # We'll add a left border manually
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=GREEN_MID,
            spaceBefore=10,
            spaceAfter=4,
            leading=12,
            textTransform="uppercase",
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT_MID,
            spaceAfter=7,
            leading=14,
            alignment=TA_JUSTIFY,
        ),
        "body_bold": ParagraphStyle(
            "body_bold",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=TEXT_DARK,
            spaceAfter=5,
            leading=14,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="Helvetica",
            fontSize=8,
            textColor=TEXT_LIGHT,
            spaceAfter=4,
            leading=11,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            textColor=TEXT_LIGHT,
            spaceAfter=3,
            leading=10,
            alignment=TA_CENTER,
        ),
        "exec_summary": ParagraphStyle(
            "exec_summary",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=TEXT_DARK,
            spaceAfter=6,
            leading=15,
            alignment=TA_JUSTIFY,
        ),
        "toc_item": ParagraphStyle(
            "toc_item",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=TEXT_DARK,
            spaceBefore=4,
            spaceAfter=4,
            leading=13,
        ),
        "toc_num": ParagraphStyle(
            "toc_num",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=GREEN_MID,
            spaceBefore=4,
            spaceAfter=4,
        ),
        "page_label": ParagraphStyle(
            "page_label",
            fontName="Helvetica-Bold",
            fontSize=7,
            textColor=GREEN_MID,
            letterSpacing=2,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=GREEN_DARK,
            leading=20,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=TEXT_LIGHT,
            leading=10,
            alignment=TA_CENTER,
        ),
        "badge_found": ParagraphStyle(
            "badge_found",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            textColor=HexColor("#065f46"),
            alignment=TA_CENTER,
        ),
        "badge_missing": ParagraphStyle(
            "badge_missing",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            textColor=RED_DARK,
            alignment=TA_CENTER,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            textColor=white,
            leading=10,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=8,
            textColor=TEXT_MID,
            leading=11,
        ),
        "table_cell_bold": ParagraphStyle(
            "table_cell_bold",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=GREEN_DARK,
            leading=11,
        ),
        "callout_title": ParagraphStyle(
            "callout_title",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=TEXT_DARK,
            spaceAfter=4,
        ),
        "callout_body": ParagraphStyle(
            "callout_body",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=TEXT_MID,
            leading=12,
        ),
        "attestation": ParagraphStyle(
            "attestation",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=TEXT_MID,
            leading=13,
            alignment=TA_JUSTIFY,
        ),
    }

    return custom


# ============================================================================
# CONTENT BUILDERS
# ============================================================================

def build_toc(toc_sections: list, styles: dict) -> list:
    story = []

    story.append(Paragraph("TABLE OF CONTENTS", ParagraphStyle(
        "toc_section_label",
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=GREEN_MID,
        letterSpacing=3,
        spaceAfter=6,
    )))
    story.append(Paragraph("In This Report", ParagraphStyle(
        "toc_main_title",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=TEXT_DARK,
        spaceAfter=14,
        leading=26,
    )))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN_LIGHT, spaceAfter=16))

    for i, section in enumerate(toc_sections, 1):
        row_data = [
            [Paragraph(f"<b>{i:02d}</b>", styles["toc_num"]),
             Paragraph(section["title"], styles["toc_item"]),
             Paragraph(str(i + 2), ParagraphStyle("p_num", fontName="Helvetica-Bold",
                                                   fontSize=9, textColor=TEXT_LIGHT,
                                                   alignment=TA_RIGHT))]
        ]
        t = Table(row_data, colWidths=[18*mm, None, 15*mm])
        t.setStyle(TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER_CLR),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)

    return story


def build_exec_summary(report_markdown: str, org: str, styles: dict) -> list:
    story = []

    story.append(Paragraph("EXECUTIVE OVERVIEW", ParagraphStyle(
        "section_tag",
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=GREEN_MID,
        letterSpacing=3,
        spaceAfter=5,
    )))
    story.append(Paragraph("Executive Summary", styles["title"]))
    story.append(AccentBar(100*mm, GREEN_LIGHT, 3))
    story.append(Spacer(1, 10))

    # Extract executive summary text from markdown
    lines = report_markdown.split('\n')
    summary_paras = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^#{1,3}\s*(executive summary|management review)', stripped, re.I):
            in_section = True
            continue
        if in_section:
            if re.match(r'^#{1,3}\s', stripped) and stripped != lines[0].strip():
                break
            if stripped and not stripped.startswith('#'):
                summary_paras.append(stripped)

    if not summary_paras:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 40:
                summary_paras.append(stripped)
            if len(summary_paras) >= 3:
                break

    # Green callout box
    box_content = "\n".join(summary_paras[:2]) if summary_paras else \
        f"This report presents the ESG performance data for {org}. All data has been extracted from institutional documents and audited for compliance against GRI, SASB, and ESRS standards."

    # Callout table with green left border
    callout_data = [[Paragraph(box_content, styles["exec_summary"])]]
    callout_t = Table(callout_data, colWidths=[PAGE_W - 36*mm])
    callout_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GREEN_PALE),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEBEFORE', (0, 0), (-1, -1), 4, GREEN_MID),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
    ]))
    story.append(callout_t)
    story.append(Spacer(1, 10))

    # Remaining summary paragraphs
    for para in summary_paras[2:5]:
        story.append(Paragraph(para, styles["body"]))

    # Scope callout
    scope_data = [[
        Paragraph("✔ Report Scope", styles["callout_title"]),
    ], [
        Paragraph(
            f"This report covers ESG performance data across Environmental, Social and Governance "
            f"dimensions for <b>{org}</b>. All data has been extracted from disclosed institutional "
            f"documents and assessed for compliance against GRI Standards, SASB framework, and ESRS. "
            f"AI-powered multi-agent extraction and audit methods were applied throughout.",
            styles["callout_body"]
        ),
    ]]
    scope_t = Table(scope_data, colWidths=[PAGE_W - 36*mm])
    scope_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor("#f0fdf4")),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBEFORE', (0, 0), (-1, -1), 4, GREEN_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor("#a7f3d0")),
    ]))
    story.append(scope_t)

    return story


def build_kpi_cards_row(audited_results: list, styles: dict) -> list:
    story = []
    story.append(Spacer(1, 16))
    story.append(Paragraph("KPI PERFORMANCE AT A GLANCE", ParagraphStyle(
        "kpi_glance_label",
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=GREEN_MID,
        letterSpacing=2,
        spaceAfter=8,
    )))

    total = len(audited_results)
    found = sum(1 for r in audited_results if r.get('audit', {}).get('is_compliant'))
    rate = round(found / total * 100) if total > 0 else 0

    stat_items = [
        (str(total), "Metrics\nAssessed"),
        (str(found), "Data Points\nDisclosed"),
        (f"{rate}%", "Data\nAvailability"),
    ]

    # Max available width is PAGE_W - 36mm
    # Distribute over 3 cards
    cell_w = (PAGE_W - 36*mm) / len(stat_items)
    row = []
    for val, label in stat_items:
        cell = [
            Paragraph(val, styles["kpi_value"]),
            Paragraph(label, styles["kpi_label"]),
        ]
        row.append(cell)

    cards_t = Table([row], colWidths=[cell_w] * len(stat_items))
    cards_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), white),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 0), (-1, 0), 3, GREEN_MID),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(cards_t)
    story.append(Spacer(1, 10))

    return story


def build_kpi_table(extraction_details: dict, audited_results: list, styles: dict) -> list:
    story = []
    story.append(PageBreak())
    story.append(Paragraph("KPI DATA TABLE", ParagraphStyle(
        "section_tag2",
        fontName="Helvetica-Bold",
        fontSize=7, textColor=GREEN_MID,
        letterSpacing=3, spaceAfter=5,
    )))
    story.append(Paragraph("ESG Performance Data", styles["title"]))
    story.append(AccentBar(100*mm, GREEN_LIGHT, 3))
    story.append(Spacer(1, 12))

    extractions = extraction_details.get('extractions', [])
    audit_map = {r['question']: r.get('audit', {}) for r in audited_results}

    # Table headers
    headers = [
        Paragraph("#", styles["table_header"]),
        Paragraph("ESG Metric", styles["table_header"]),
        Paragraph("Status", styles["table_header"]),
        Paragraph("Value & Unit", styles["table_header"]),
        Paragraph("Year", styles["table_header"]),
        Paragraph("Source", styles["table_header"]),
    ]

    rows = [headers]
    # Sum must be <= 174mm (PAGE_W - 36*mm). 8+60+25+30+15+30 = 168mm
    col_widths = [8*mm, 60*mm, 25*mm, 30*mm, 15*mm, 30*mm]

    for i, item in enumerate(extractions, 1):
        q = item.get('question', f'KPI {i}')
        ext = item.get('extraction', {})
        aud = audit_map.get(q, {})

        status = ext.get('status', 'not_found')
        value = str(ext.get('value', '—'))
        unit = ext.get('unit', '') or ''
        year_val = str(ext.get('year', '—'))
        source = str(ext.get('source', '—'))
        score = aud.get('score', 0) or 0

        short_q = q[:60] + "…" if len(q) > 60 else q
        short_src = source[:25] + "…" if len(source) > 25 else source

        if status == 'success':
            status_para = Paragraph("✓ Disclosed", ParagraphStyle(
                "badge_f", fontName="Helvetica-Bold", fontSize=7.5,
                textColor=HexColor("#065f46"), alignment=TA_CENTER))
            status_bg = HexColor("#d1fae5")
        else:
            status_para = Paragraph("○ In Development", ParagraphStyle(
                "badge_m", fontName="Helvetica", fontSize=7.5,
                textColor=HexColor("#475569"), alignment=TA_CENTER))
            status_bg = HexColor("#f1f5f9")

        val_unit = f"{value} {unit}".strip() if value != '—' else '—'

        row = [
            Paragraph(f"<b>{i:02d}</b>", styles["table_cell_bold"]),
            Paragraph(short_q, styles["table_cell"]),
            status_para,
            Paragraph(val_unit, styles["table_cell"]),
            Paragraph(year_val, styles["table_cell"]),
            Paragraph(short_src, styles["table_cell"]),
        ]
        rows.append(row)

    kpi_table = Table(rows, colWidths=col_widths, repeatRows=1)

    # Build row-level background colors
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), GREEN_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7.5),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, BORDER_CLR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, BG_LIGHT]),
    ]

    # Add status cell backgrounds
    for i, item in enumerate(extractions, 1):
        ext = item.get('extraction', {})
        status_bg = HexColor("#d1fae5") if ext.get('status') == 'success' else HexColor("#f1f5f9")
        style_cmds.append(('BACKGROUND', (2, i), (2, i), status_bg))

    kpi_table.setStyle(TableStyle(style_cmds))
    story.append(kpi_table)
    story.append(Paragraph(
        "Table: Comprehensive extraction of primary institutional ESG metric data.",
        styles["caption"]
    ))

    return story


def build_compliance_section(audited_results: list, styles: dict) -> list:
    story = []
    story.append(PageBreak())
    story.append(Paragraph("COMPLIANCE MAPPING", ParagraphStyle(
        "section_tag3",
        fontName="Helvetica-Bold",
        fontSize=7, textColor=GREEN_MID,
        letterSpacing=3, spaceAfter=5,
    )))
    story.append(Paragraph("Framework Alignment", styles["title"]))
    story.append(AccentBar(100*mm, GREEN_LIGHT, 3))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The following table maps disclosed KPIs against three principal international frameworks: "
        "<b>GRI Standards</b>, <b>SASB</b>, and <b>ESRS</b>. Disclosure rates reflect the proportion "
        "of KPIs in each pillar with confirmed data points.",
        styles["body"]
    ))
    story.append(Spacer(1, 10))

    env_kw = ['electr', 'energy', 'ghg', 'carbon', 'emiss', 'water', 'waste', 'solar', 'renew', 'co2', 'green']
    soc_kw = ['employee', 'health', 'safety', 'training', 'gender', 'diversity', 'community']
    gov_kw = ['board', 'governance', 'corrupt', 'ethics', 'integrity', 'compliance']

    env_kpis = [r for r in audited_results if any(k in r['question'].lower() for k in env_kw)]
    soc_kpis = [r for r in audited_results if any(k in r['question'].lower() for k in soc_kw)]
    gov_kpis = [r for r in audited_results if any(k in r['question'].lower() for k in gov_kw)]

    def disclosure_rate(kpis):
        if not kpis:
            return 0
        found = sum(1 for r in kpis if r.get('audit', {}).get('is_compliant'))
        return round(found / len(kpis) * 100)

    def rate_badge(rate):
        if rate >= 70:
            return HexColor("#d1fae5"), HexColor("#065f46"), "Aligned"
        elif rate >= 40:
            return HexColor("#fef3c7"), HexColor("#92400e"), "Progressing"
        else:
            return HexColor("#f1f5f9"), HexColor("#64748b"), "Developing"

    frameworks_data = [
        ("Environmental", env_kpis, "GRI 302/303/305/306", "SASB — Operations", "ESRS E1–E5", disclosure_rate(env_kpis)),
        ("Social", soc_kpis, "GRI 401/403/404", "SASB — Human Capital", "ESRS S1", disclosure_rate(soc_kpis)),
        ("Governance", gov_kpis, "GRI 2-9/205", "SASB — Leadership", "ESRS G1", disclosure_rate(gov_kpis)),
    ]

    fw_headers = [
        Paragraph("ESG Pillar", styles["table_header"]),
        Paragraph("GRI Standards", styles["table_header"]),
        Paragraph("SASB", styles["table_header"]),
        Paragraph("ESRS", styles["table_header"]),
        Paragraph("KPIs", styles["table_header"]),
        Paragraph("Disclosure Rate", styles["table_header"]),
        Paragraph("Status", styles["table_header"]),
    ]

    fw_rows = [fw_headers]
    for theme, kpis, gri, sasb, esrs, rate in frameworks_data:
        bg, fg, status_text = rate_badge(rate)
        fw_rows.append([
            Paragraph(f"<b>{theme}</b>", styles["table_cell"]),
            Paragraph(gri, styles["table_cell"]),
            Paragraph(sasb, styles["table_cell"]),
            Paragraph(esrs, styles["table_cell"]),
            Paragraph(str(len(kpis)), ParagraphStyle("center_cell", fontName="Helvetica",
                                                       fontSize=8, alignment=TA_CENTER)),
            Paragraph(f"{rate}%", ParagraphStyle("rate_cell", fontName="Helvetica-Bold",
                                                  fontSize=9, textColor=fg, alignment=TA_CENTER)),
            Paragraph(status_text, ParagraphStyle("status_cell", fontName="Helvetica-Bold",
                                                   fontSize=7.5, textColor=fg, alignment=TA_CENTER)),
        ])

    fw_t = Table(fw_rows, colWidths=[28*mm, 32*mm, 30*mm, 22*mm, 12*mm, 22*mm, 22*mm], repeatRows=1)

    fw_style = [
        ('BACKGROUND', (0, 0), (-1, 0), GREEN_MID),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, BORDER_CLR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, BG_LIGHT]),
    ]

    for i, (theme, kpis, gri, sasb, esrs, rate) in enumerate(frameworks_data, 1):
        bg, fg, _ = rate_badge(rate)
        fw_style.append(('BACKGROUND', (5, i), (6, i), bg))

    fw_t.setStyle(TableStyle(fw_style))
    story.append(fw_t)
    story.append(Spacer(1, 14))

    # Framework note callout
    note_data = [
        [Paragraph("⚠ Framework Alignment Note", styles["callout_title"])],
        [Paragraph(
            "ESRS mandatory disclosure requirements were introduced under EU CSRD (effective 2024). "
            "Organizations are encouraged to prioritize ESRS E1 (Climate Change) and S1 (Own Workforce) "
            "alignment in future reporting cycles. SASB sector-specific standards applicable to this "
            "organization type have been considered in the overall quality assessment.",
            styles["callout_body"]
        )],
    ]
    note_t = Table(note_data, colWidths=[PAGE_W - 36*mm])
    note_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor("#fff7ed")),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBEFORE', (0, 0), (-1, -1), 4, ACCENT),
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor("#fed7aa")),
    ]))
    story.append(note_t)

    return story


def build_narrative_section(report_markdown: str, styles: dict) -> list:
    """Parse the LLM markdown and convert to styled ReportLab paragraphs."""
    story = []
    story.append(PageBreak())
    story.append(Paragraph("PERFORMANCE ANALYSIS", ParagraphStyle(
        "section_tag4",
        fontName="Helvetica-Bold",
        fontSize=7, textColor=GREEN_MID,
        letterSpacing=3, spaceAfter=5,
    )))
    story.append(Paragraph("Detailed ESG Narrative", styles["title"]))
    story.append(AccentBar(100*mm, GREEN_LIGHT, 3))
    story.append(Spacer(1, 10))

    lines = report_markdown.split('\n')
    in_table = False
    table_rows = []
    skip_first_exec = True
    first_h2_seen = False

    def flush_table(rows):
        if len(rows) < 2:
            return []
        items = []
        # Parse markdown table
        parsed_rows = []
        for row in rows:
            parts = [c.strip() for c in row.strip('|').split('|')]
            parsed_rows.append(parts)

        if not parsed_rows:
            return []

        # Determine column count
        max_cols = max(len(r) for r in parsed_rows)

        # Filter separator rows
        data_rows = [r for r in parsed_rows if not all(re.match(r'^-+$', c.strip('-').replace(':', '')) for c in r)]

        if not data_rows:
            return []

        header = data_rows[0]
        body = data_rows[1:]

        def cell_para(text, is_header=False):
            s = ParagraphStyle("tc", fontName="Helvetica-Bold" if is_header else "Helvetica",
                               fontSize=7.5, textColor=white if is_header else TEXT_MID, leading=11)
            return Paragraph(str(text)[:60], s)

        tbl_data = [[cell_para(c, True) for c in header]] + \
                   [[cell_para(c) for c in (r + [''] * (max_cols - len(r)))] for r in body]

        # Add safety margin for the total width
        col_w = (PAGE_W - 40*mm) / max_cols
        tbl = Table(tbl_data, colWidths=[col_w] * max_cols, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN_DARK),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.3, BORDER_CLR),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        items.append(tbl)
        items.append(Spacer(1, 8))
        return items

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_table:
                story.extend(flush_table(table_rows))
                table_rows = []
                in_table = False
            story.append(Spacer(1, 4))
            continue

        # Detect table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            story.extend(flush_table(table_rows))
            table_rows = []
            in_table = False

        # Skip duplicate h1
        if stripped.startswith('# ') and skip_first_exec:
            skip_first_exec = False
            continue

        if re.match(r'^#{1,2}\s', stripped):
            level = 2 if stripped.startswith('## ') else 1
            text = re.sub(r'^#{1,6}\s+', '', stripped)
            if level == 2:
                if not first_h2_seen:
                    first_h2_seen = True
                story.append(Spacer(1, 8))
                # Left-accented heading
                h_data = [[
                    Table([[Paragraph("", ParagraphStyle("dot", fontSize=1))]],
                          colWidths=[3*mm],
                          style=[('BACKGROUND', (0, 0), (-1, -1), GREEN_LIGHT),
                                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0)]),
                    Paragraph(text, styles["h2"]),
                ]]
                h_t = Table(h_data, colWidths=[5*mm, PAGE_W - 41*mm])
                h_t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), white),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(h_t)
            else:
                story.append(Paragraph(text, styles["h3"]))
        elif re.match(r'^(\*|-)\s', stripped):
            text = re.sub(r'^[\*\-]\s+', '', stripped)
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"•  {text}", ParagraphStyle(
                "bullet",
                fontName="Helvetica", fontSize=9, textColor=TEXT_MID,
                leading=13, leftIndent=12, spaceAfter=3,
            )))
        else:
            text = stripped
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            if len(text) > 10:
                story.append(Paragraph(text, styles["body"]))

    if in_table:
        story.extend(flush_table(table_rows))

    return story


def build_audit_section(audited_results: list, styles: dict) -> list:
    story = []
    story.append(PageBreak())
    story.append(Paragraph("AUDIT & RECOMMENDATIONS", ParagraphStyle(
        "section_tag5",
        fontName="Helvetica-Bold",
        fontSize=7, textColor=GREEN_MID,
        letterSpacing=3, spaceAfter=5,
    )))
    story.append(Paragraph("Audit Remarks & Recommendations", styles["title"]))
    story.append(AccentBar(100*mm, GREEN_LIGHT, 3))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "The following audit notes were generated by the AI Compliance Auditor (Agent B) "
        "for each assessed KPI. Remarks follow GRI-aligned disclosure quality criteria: "
        "completeness, clarity, and citation adequacy.",
        styles["body"]
    ))
    story.append(Spacer(1, 10))

    for r in audited_results:
        audit = r.get('audit', {})
        remark = audit.get('audit_remarks', '')
        recommendation = audit.get('recommendation', '')
        score = audit.get('score', 0) or 0
        is_compliant = audit.get('is_compliant', False)
        q_short = r['question'][:70] + "…" if len(r['question']) > 70 else r['question']

        if not remark and not recommendation:
            continue

        icon = "✓" if is_compliant else "✕"
        icon_color = HexColor("#065f46") if is_compliant else RED_DARK
        bg_color = HexColor("#f0fdf4") if is_compliant else HexColor("#fef9f9")
        border_color = GREEN_LIGHT if is_compliant else HexColor("#fca5a5")

        note_content = []
        header_row = [
            Paragraph(f'<font color="{"#065f46" if is_compliant else "#991b1b"}">{icon}</font> <b>{q_short}</b>',
                      styles["body_bold"]),
            Paragraph(f"<b>{score}/10</b>", ParagraphStyle("score_right", fontName="Helvetica-Bold",
                                                             fontSize=8, textColor=TEXT_MID, alignment=TA_RIGHT)),
        ]
        # Inner width is parent width (PAGE_W - 36*mm) minus paddings (12 + 12 = 24 points)
        # 25*mm is ~70 points. So first col gets the rest.
        header_t = Table([header_row], colWidths=[PAGE_W - 36*mm - 24 - 26*mm, 25*mm])
        header_t.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        note_content.append(header_t)

        if remark:
            note_content.append(Paragraph(
                f"<b>Remark:</b> {remark}",
                ParagraphStyle("remark", fontName="Helvetica", fontSize=8,
                               textColor=TEXT_MID, leading=12, spaceBefore=4)
            ))
        if recommendation:
            note_content.append(Paragraph(
                f"<b>Recommendation:</b> {recommendation}",
                ParagraphStyle("rec", fontName="Helvetica", fontSize=8,
                               textColor=TEXT_MID, leading=12, spaceBefore=3)
            ))

        audit_data = [[cell] for cell in note_content]
        audit_t = Table(audit_data, colWidths=[PAGE_W - 36*mm])
        audit_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBEFORE', (0, 0), (-1, -1), 3, border_color),
            ('BOX', (0, 0), (-1, -1), 0.3, BORDER_CLR),
        ]))
        story.append(audit_t)
        story.append(Spacer(1, 5))

    # Priority improvements
    story.append(Spacer(1, 14))
    story.append(Paragraph("Priority Improvements for Next Reporting Cycle", styles["h2"]))
    improvements = [
        "Expand Scope 3 GHG emissions disclosure to cover the full institutional value chain, including supply chain and downstream activities.",
        "Introduce quantitative Social KPIs: training hours per FTE, Total Recordable Injury Rate (TRIR), employee turnover rate, and gender pay gap.",
        "Establish a formal Governance disclosure policy aligned with ESRS G1 (Business Conduct and Ethics), including anti-corruption training coverage.",
        "Improve source documentation to achieve GRI full-disclosure compliance for all reported metrics; assign a document reference code to each KPI.",
        "Set science-based emission reduction targets aligned with the Paris Agreement 1.5°C trajectory and publish a climate transition plan.",
    ]
    for imp in improvements:
        story.append(Paragraph(f"•  {imp}", ParagraphStyle(
            "improvement",
            fontName="Helvetica", fontSize=9, textColor=TEXT_MID,
            leading=13, leftIndent=10, spaceAfter=5,
        )))

    return story


def build_attestation_section(org: str, styles: dict) -> list:
    story = []
    story.append(Spacer(1, 20))

    att_data = [
        [Paragraph("Data Integrity Attestation", styles["body_bold"])],
        [Paragraph(
            f"This ESG report has been generated by an AI-powered multi-agent system using data extracted "
            f"directly from institutional documents submitted by <b>{org}</b>. All KPI data points are "
            f"referenced to their source documents and have been assessed for disclosure quality against "
            f"GRI, SASB, and ESRS compliance criteria. This report does not constitute external assurance "
            f"or third-party verification and is intended for internal strategic review and stakeholder "
            f"communication purposes.",
            styles["attestation"]
        )],
    ]
    att_t = Table(att_data, colWidths=[PAGE_W - 36*mm])
    att_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('LINEABOVE', (0, 0), (-1, 0), 3, GREEN_MID),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(att_t)
    story.append(Spacer(1, 10))

    date_str = datetime.now().strftime("%B %d, %Y")
    stamp_data = [[Paragraph(
        f"📄 Generated by ESG Multi-Agent Reporting Suite  |  {date_str}  |  {org}  |  Confidential",
        ParagraphStyle("stamp", fontName="Helvetica", fontSize=7.5,
                       textColor=GREEN_MID, alignment=TA_CENTER)
    )]]
    stamp_t = Table(stamp_data, colWidths=[PAGE_W - 36*mm])
    stamp_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GREEN_PALE),
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor("#a7f3d0")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stamp_t)

    return story


# ============================================================================
# MASTER PDF BUILDER
# ============================================================================

def generate_pdf_report(
    report_markdown: str,
    extraction_details: dict,
    audited_results: list,
    topic: str,
    stats: dict,
    output_filename: str,
) -> str:
    """
    Generate a publication-quality PDF ESG report using ReportLab.
    Returns the path to the saved PDF.
    """
    org = ORGANIZATION
    year = REPORT_YEAR
    styles = build_styles()

    pdf_path = os.path.join(REPORTS_DIR, output_filename)

    # ── Closures so callbacks can access our data ──
    _cover_data = {"org": org, "year": year, "topic": topic, "stats": stats}

    def draw_cover(c, doc):
        """Draw the full-bleed cover page on the canvas."""
        c.saveState()

        # Green top section (60%)
        top_h = PAGE_H * 0.60
        c.setFillColor(GREEN_DARK)
        c.rect(0, PAGE_H - top_h, PAGE_W, top_h, fill=1, stroke=0)

        # Decorative circles
        c.setFillColor(HexColor("#1f5c38"))
        c.circle(PAGE_W - 25*mm, PAGE_H - 10*mm, 55*mm, fill=1, stroke=0)
        c.setFillColor(HexColor("#26704a"))
        c.circle(PAGE_W - 35*mm, PAGE_H - 60*mm, 35*mm, fill=1, stroke=0)

        # Accent bar
        c.setFillColor(ACCENT)
        c.rect(0, PAGE_H - top_h - 4, PAGE_W, 4, fill=1, stroke=0)

        # Tag
        c.setFillColor(HexColor("#ffffff25"))
        c.roundRect(18*mm, PAGE_H - 38*mm, 60*mm, 8*mm, 2, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(21*mm, PAGE_H - 33.5*mm, "ESG SUSTAINABILITY REPORT")

        # Main title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 30)
        title = _cover_data["topic"]
        words = title.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= 25:
                current = (current + " " + word).strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = PAGE_H - 58*mm
        for line in lines[:3]:
            c.drawString(18*mm, y, line)
            y -= 12*mm

        # Org name
        c.setFont("Helvetica", 13)
        c.setFillColor(HexColor("#ffffffcc"))
        c.drawString(18*mm, y - 4*mm, _cover_data["org"])

        # Year
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#ffffff88"))
        c.drawString(18*mm, y - 15*mm, f"Fiscal Period: {_cover_data['year']}")

        # Divider
        c.setStrokeColor(ACCENT)
        c.setLineWidth(3)
        c.line(18*mm, y - 22*mm, 40*mm, y - 22*mm)

        # Stats row
        kpis_extracted = _cover_data["stats"].get("kpis_extracted", 0)
        kpis_total = _cover_data["stats"].get("kpis_requested", 14)
        frameworks = _cover_data["stats"].get("frameworks_count", 3)
        stat_items = [
            (str(kpis_extracted), "KPIs Extracted"),
            (str(kpis_total), "KPIs Assessed"),
            (str(frameworks), "Frameworks"),
            (str(_cover_data["year"]), "Period"),
        ]
        stats_y = PAGE_H * 0.37
        box_w = (PAGE_W - 36*mm) / 4
        x = 18*mm
        for val, label in stat_items:
            c.setFillColor(GREEN_LIGHT)
            c.rect(x, stats_y + 2, 3, 28, fill=1, stroke=0)
            c.setFillColor(GREEN_DARK)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(x + 7*mm, stats_y + 14, val)
            c.setFillColor(TEXT_LIGHT)
            c.setFont("Helvetica", 7)
            c.drawString(x + 7*mm, stats_y + 4, label.upper())
            x += box_w + 2*mm

        # Footer
        footer_y = 18*mm
        c.setStrokeColor(BORDER_CLR)
        c.setLineWidth(0.5)
        c.line(18*mm, footer_y, PAGE_W - 18*mm, footer_y)
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(18*mm, footer_y - 7*mm, _cover_data["org"])
        date_str = datetime.now().strftime("%B %d, %Y")
        c.setFillColor(TEXT_LIGHT)
        c.setFont("Helvetica", 8)
        c.drawRightString(PAGE_W - 18*mm, footer_y - 7*mm, f"Generated: {date_str}  |  Confidential")

        c.restoreState()

    def draw_content_page(c, doc):
        """Draw header and footer on content pages."""
        pass  # NumberedCanvas handles this

    # ── Page templates ──
    margin = 18 * mm
    full_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=1, bottomPadding=1,
                       rightPadding=1, topPadding=1, id='full')
    content_frame = Frame(margin, 15*mm, PAGE_W - 2*margin,
                          PAGE_H - 18*mm - 15*mm, id='main')


    cover_template = PageTemplate(id='cover', frames=[full_frame], onPage=draw_cover)
    content_template = PageTemplate(id='content', frames=[content_frame], onPage=draw_content_page)

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A4,
        pageTemplates=[cover_template, content_template],
        title=f"{topic} — {org}",
        author=org,
        subject="ESG Sustainability Report",
    )

    from reportlab.platypus import NextPageTemplate

    # ── Build story ──
    story = []

    # 1. Cover — use NextPageTemplate to switch to cover template, then a tiny spacer + break
    story.append(NextPageTemplate('cover'))
    story.append(Spacer(1, 1))  # minimal content to trigger the cover page
    story.append(NextPageTemplate('content'))
    story.append(PageBreak())

    # 2. Table of Contents
    toc_sections = [
        {"title": "Executive Summary"},
        {"title": "Performance Analysis & Narrative"},
        {"title": "ESG KPI Data Table"},
        {"title": "Framework Compliance Mapping"},
    ]
    story.extend(build_toc(toc_sections, styles))
    story.append(PageBreak())

    # 3. Executive Summary
    story.extend(build_exec_summary(report_markdown, org, styles))
    story.extend(build_kpi_cards_row(audited_results, styles))

    # 4. Performance Narrative
    story.extend(build_narrative_section(report_markdown, styles))

    # 5. KPI Table
    story.extend(build_kpi_table(extraction_details, audited_results, styles))

    # 6. Compliance
    story.extend(build_compliance_section(audited_results, styles))

    # 7. Attestation
    story.extend(build_attestation_section(org, styles))

    # ── Build PDF ──
    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info(f"✅ PDF report generated: {pdf_path}")

    return pdf_path

