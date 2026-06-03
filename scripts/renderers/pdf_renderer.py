"""
Generic PDF Renderer

Consumes a report dict (result_schema) and produces a .pdf file via reportlab.
No dataset-specific logic here — everything is driven by the report structure.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Register Chinese font ──
_CJK_FONT = 'Helvetica'
_CJK_FONT_BOLD = 'Helvetica-Bold'
_CJK_PATHS = [
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
]
for fp in _CJK_PATHS:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('STHeiti', fp, subfontIndex=0))
            _CJK_FONT = 'STHeiti'
            _CJK_FONT_BOLD = 'STHeiti'
            break
        except Exception:
            continue

_HAS_CJK = _CJK_FONT != 'Helvetica'

# ── Style constants ──
BLUE = HexColor('#1B365D')
GRAY = HexColor('#666666')
DARK = HexColor('#282828')
LIGHT_GRAY = HexColor('#F5F5F5')
ACCENT = HexColor('#C9A96E')

styles = getSampleStyleSheet()

# English / fallback styles
s_cover_title = ParagraphStyle('CT', fontName='Helvetica-Bold', fontSize=22,
                                textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)
s_cover_sub = ParagraphStyle('CS', fontName='Helvetica', fontSize=12,
                              textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)
s_cover_info = ParagraphStyle('CI', fontName='Helvetica', fontSize=10,
                               textColor=HexColor('#888888'), alignment=TA_CENTER)
s_section = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=14,
                            textColor=BLUE, spaceBefore=6*mm, spaceAfter=4*mm)
s_sub = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11,
                        textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=10,
                         textColor=DARK, leading=15, alignment=TA_JUSTIFY, spaceAfter=3*mm)
s_small = ParagraphStyle('Small', fontName='Helvetica', fontSize=9,
                          textColor=GRAY, leading=13, spaceAfter=2*mm)

# Chinese styles (use CJK font when available)
s_section_cn = ParagraphStyle('SecCN', fontName=_CJK_FONT_BOLD, fontSize=14,
                               textColor=BLUE, spaceBefore=6*mm, spaceAfter=4*mm)
s_sub_cn = ParagraphStyle('SubCN', fontName=_CJK_FONT_BOLD, fontSize=11,
                           textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body_cn = ParagraphStyle('BodyCN', fontName=_CJK_FONT, fontSize=10,
                            textColor=DARK, leading=16, alignment=TA_JUSTIFY, spaceAfter=3*mm)
s_lead_cn = ParagraphStyle('LeadCN', fontName=_CJK_FONT_BOLD, fontSize=11,
                            textColor=BLUE, leading=18, spaceBefore=2*mm, spaceAfter=3*mm)
s_cover_title_cn = ParagraphStyle('CTCN', fontName=_CJK_FONT_BOLD, fontSize=22,
                                   textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)
s_cover_sub_cn = ParagraphStyle('CSCN', fontName=_CJK_FONT, fontSize=12,
                                 textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)


def _section(text):
    """Section heading, auto-selects font based on content."""
    has_cjk = any('一' <= c <= '鿿' or '　' <= c <= '〿' for c in text)
    style = s_section_cn if has_cjk and _HAS_CJK else s_section
    return [Paragraph(text, style), HRFlowable(width="100%", color=BLUE, thickness=0.5)]


def _sub(text):
    has_cjk = any('一' <= c <= '鿿' for c in text)
    style = s_sub_cn if has_cjk and _HAS_CJK else s_sub
    return Paragraph(text, style)


def _body(text):
    text = text.replace('\n', '<br/>')
    has_cjk = any('一' <= c <= '鿿' for c in text)
    style = s_body_cn if has_cjk and _HAS_CJK else s_body
    return Paragraph(text, style)


def _bullet(text):
    has_cjk = any('一' <= c <= '鿿' for c in text)
    style = s_body_cn if has_cjk and _HAS_CJK else s_body
    return Paragraph(f'&bull; {text}', style)


def _lead(text):
    return Paragraph(text, s_lead_cn)


def _metric_table(metrics):
    """Render metric glossary as a table."""
    if not metrics:
        return []
    has_cjk = any('一' <= c <= '鿿' for c in str(metrics))
    font = _CJK_FONT if has_cjk and _HAS_CJK else 'Helvetica'
    data = [['Metric', 'Value', 'Formula']]
    for m in metrics[:8]:
        data.append([
            m.get('name', ''),
            str(m.get('current_value', '')),
            m.get('formula', '')[:60],
        ])
    t = Table(data, colWidths=[80*mm, 50*mm, 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.3, HexColor('#CCCCCC')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return [Spacer(1, 3*mm), t, Spacer(1, 3*mm)]


def _on_page(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0] / 2, 15 * mm, f'Page {doc.page}')
    canvas_obj.restoreState()


def render(report: dict, output_path: str) -> str:
    """
    Main entry point. Takes a report dict and writes a .pdf file.
    Returns the output path.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=22*mm,
        leftMargin=20*mm,
        rightMargin=20*mm,
    )
    story = []
    overview = report.get("dataset_overview", {})
    findings = report.get("key_findings", [])
    models = report.get("thinking_models", [])
    recs = report.get("recommendations", [])
    metrics = report.get("metric_glossary", [])
    quality = report.get("data_quality", {})
    semantics = report.get("field_semantics", [])
    beginner = report.get("beginner_notes", {})

    # ── Cover ──
    story.append(Spacer(1, 40*mm))
    title = report.get("title", "Analysis Report")
    if _HAS_CJK:
        story.append(Paragraph(title, s_cover_title_cn))
    else:
        story.append(Paragraph(title, s_cover_title))
    story.append(Paragraph(f'Mode: {report.get("analysis_mode", "audit_report")}', s_cover_sub))
    story.append(Spacer(1, 8*mm))
    line_tbl = Table([['']], colWidths=[80*mm])
    line_tbl.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, BLUE)]))
    story.append(line_tbl)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(f'File: {overview.get("file_name", "N/A")}', s_cover_info))
    story.append(Paragraph(f'Rows: {overview.get("rows", 0):,} | Fields: {overview.get("columns", 0)}', s_cover_info))
    if overview.get("time_range"):
        story.append(Paragraph(f'Period: {overview["time_range"]}', s_cover_info))
    story.append(Spacer(1, 15*mm))

    # Key KPIs on cover
    if metrics:
        story.append(Paragraph('Key Metrics',
                     ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12,
                                    textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
        cover_metrics = metrics[:6]
        md = [['Metric', 'Value']] + [[m.get('name', ''), str(m.get('current_value', ''))]
                                       for m in cover_metrics]
        mt = Table(md, colWidths=[90*mm, 50*mm])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(mt)

    # ── Dataset Overview ──
    story.append(PageBreak())
    story.extend(_section('Dataset Overview'))
    overview_lines = [
        f'File: {overview.get("file_name", "N/A")}',
        f'Records: {overview.get("rows", 0):,}  |  Fields: {overview.get("columns", 0)}',
    ]
    if overview.get("time_range"):
        overview_lines.append(f'Period: {overview["time_range"]}')
    overview_lines.append(f'Missing values: {"Yes" if overview.get("has_missing") else "None"}')
    overview_lines.append(f'Duplicate rows: {overview.get("duplicate_rows", 0)}')
    for line in overview_lines:
        story.append(_bullet(line))

    # Fields
    fields = overview.get("fields", [])
    if fields:
        story.append(_sub('Fields'))
        ftypes = overview.get("field_types", {})
        field_list = ', '.join(f'{f} ({ftypes.get(f, "?")})' for f in fields[:20])
        story.append(_body(field_list))
        if len(fields) > 20:
            story.append(_body(f'... and {len(fields) - 20} more fields'))

    # ── Field Semantics ──
    if semantics:
        story.extend(_section('Field Semantics'))
        sem_data = [['Field', 'Inferred Meaning', 'Confidence']]
        for s in semantics:
            sem_data.append([s['field'], s['inferred_meaning'], s['confidence']])
        if len(sem_data) > 1:
            t = Table(sem_data, colWidths=[50*mm, 90*mm, 30*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), _CJK_FONT if _HAS_CJK else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.3, HexColor('#CCCCCC')),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t)

    # ── Data Quality ──
    risk_checks = quality.get("risk_checks", [])
    if risk_checks:
        story.append(PageBreak())
        story.extend(_section('Data Quality'))
        for rc in risk_checks:
            status_icon = {'pass': 'PASS', 'warn': 'WARN', 'fail': 'FAIL'}
            story.append(_sub(f'[{status_icon.get(rc["status"], "?")}] {rc["check"]}'))
            story.append(_body(rc.get("detail", "")))
            if rc.get("affected_analysis"):
                story.append(_body(f'<i>Affects: {rc["affected_analysis"]}</i>'))

    # ── Key Findings ──
    if findings:
        story.append(PageBreak())
        story.extend(_section('Key Findings'))
        for i, f in enumerate(findings):
            title = f.get('title', f'Finding {i+1}')
            story.append(_sub(title))
            evidence = f.get('data_evidence', '')
            if evidence:
                story.append(_body(f'<b>Evidence:</b> {evidence}'))
            interpretation = f.get('business_interpretation', '')
            if interpretation:
                story.append(_body(f'<b>Interpretation:</b> {interpretation}'))
            action = f.get('suggested_action', '')
            if action:
                story.append(_body(f'<b>Action:</b> {action}'))
            cannot_prove = f.get('what_it_cannot_prove', '')
            if cannot_prove:
                story.append(_body(f'<i>Boundary: {cannot_prove}</i>'))
            reuse = f.get('how_to_reuse', '')
            if reuse:
                story.append(_body(f'<i>Reuse: {reuse}</i>'))

    # ── Thinking Models ──
    if models:
        story.append(PageBreak())
        story.extend(_section('Thinking Models'))
        for m in models:
            story.append(_sub(m.get('model_name', 'Unknown Model')))
            evidence = m.get('evidence', '')
            if evidence:
                story.append(_body(f'<b>Evidence:</b> {evidence}'))
            takeaway = m.get('takeaway', '')
            if takeaway:
                story.append(_body(f'<b>Takeaway:</b> {takeaway}'))

    # ── Learning Guide (Beginner Notes) ──
    story.append(PageBreak())
    story.extend(_section('Learning Guide'))

    concepts = beginner.get('concepts_learned', [])
    if concepts:
        story.append(_sub('Concepts Learned'))
        for c in concepts:
            story.append(_bullet(c))

    methods = beginner.get('methods_learned', [])
    if methods:
        story.append(_sub('Methods Learned'))
        for m in methods:
            story.append(_bullet(m))

    metric_names = beginner.get('metrics_learned', [])
    if metric_names:
        story.append(_sub('Metrics Learned'))
        for mn in metric_names:
            story.append(_bullet(mn))

    patterns = beginner.get('thinking_patterns', [])
    if patterns:
        story.append(_sub('Reusable Thinking Patterns'))
        for p in patterns:
            story.append(_bullet(p))

    # Next-time reuse steps
    next_steps = beginner.get('next_time_steps', [])
    if next_steps:
        story.append(_sub('Next Time You See Similar Data'))
        for step in next_steps:
            story.append(_bullet(step))

    # Conclusions not to over-interpret
    caveats = beginner.get('conclusions_not_to_overinterpret', [])
    if caveats:
        story.append(_sub('Caveats: Do Not Over-Interpret'))
        for c in caveats:
            story.append(_bullet(c))

    # Self-check questions for learning
    story.append(_sub('Self-Check Questions'))
    questions = [
        'Q1: What total metric can be decomposed, and by which dimensions?',
        'Q2: After decomposition, how large are the subgroup differences?',
        'Q3: What missing key information can be inferred by a proxy variable?',
        'Q4: Is the observed difference a preference or a constraint?',
        'Q5: Which segment is both high-share and high-difference (a leverage point)?',
    ]
    for q in questions:
        story.append(_body(q))

    # ── Metrics Glossary ──
    if metrics:
        story.append(PageBreak())
        story.extend(_section('Metrics Glossary'))
        story.extend(_metric_table(metrics))
        for m in metrics:
            meaning = m.get('meaning', '')
            if meaning:
                story.append(_sub(m.get('name', 'Metric')))
                story.append(_body(f'<b>Meaning:</b> {meaning}'))
                biz_use = m.get('business_use', '')
                if biz_use:
                    story.append(_body(f'<b>Business Use:</b> {biz_use}'))
                limit = m.get('limitation', '')
                if limit:
                    story.append(_body(f'<b>Limitation:</b> {limit}'))

    # ── Data Tables ──
    tables = report.get("tables", [])
    if tables:
        story.append(PageBreak())
        story.extend(_section('Data Tables'))
        for tbl in tables:
            name = tbl.get("name", "Table")
            story.append(_sub(name))
            headers = tbl.get("headers", [])
            data = tbl.get("data", [])
            if not headers or not data:
                story.append(_body("(no data)"))
                continue
            tbl_data = [headers] + data[:25]

            ncols = len(headers)
            avail = 170 * mm
            col_widths = [min(avail / ncols, 70 * mm)] * ncols

            t = Table(tbl_data, colWidths=col_widths, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), _CJK_FONT if _HAS_CJK else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.3, HexColor('#CCCCCC')),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(Spacer(1, 2*mm))
            story.append(t)
            story.append(Spacer(1, 3*mm))
            if len(data) > 25:
                story.append(_body(f'(showing 25 of {len(data)} rows)'))

    # ── Recommendations ──
    if recs:
        story.append(PageBreak())
        story.extend(_section('Recommendations'))
        for r in recs:
            story.append(_sub(r.get('title', 'Recommendation')))
            action = r.get('action', '')
            if action:
                story.append(_body(f'<b>Action:</b> {action}'))
            metric_track = r.get('metric_to_track', '')
            if metric_track:
                story.append(_body(f'<b>Metric to Track:</b> {metric_track}'))
            data_needed = r.get('data_needed', '')
            if data_needed:
                story.append(_body(f'<b>Data Needed:</b> {data_needed}'))

    doc.build(story, onLaterPages=_on_page)
    return output_path
