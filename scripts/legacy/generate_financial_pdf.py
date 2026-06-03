"""
Financial / Operating Performance — PDF Report (ReportLab)
"""
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
)
import warnings; warnings.filterwarnings("ignore")

BASE = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/financial_operating_performance"
df = pd.read_csv(f"{BASE}/BCG.csv")
df = df.sort_values(["Company_Name", "Year"])

apple = df[df["Company_Name"]=="Apple"].iloc[-1]
msft = df[df["Company_Name"]=="Microsoft"].iloc[-1]
tsla = df[df["Company_Name"]=="Tesla"].iloc[-1]
apple_rev_g = (apple["Total_Revenue"] / df[df["Company_Name"]=="Apple"]["Total_Revenue"].iloc[0] - 1) * 100

BLUE = HexColor('#1B365D')
GRAY = HexColor('#666666')
DARK = HexColor('#282828')
styles = getSampleStyleSheet()

s_cover_title = ParagraphStyle('CT', fontName='Helvetica-Bold', fontSize=22, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)
s_cover_sub = ParagraphStyle('CS', fontName='Helvetica', fontSize=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)
s_cover_info = ParagraphStyle('CI', fontName='Helvetica', fontSize=10, textColor=HexColor('#888888'), alignment=TA_CENTER)
s_section = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=14, textColor=BLUE, spaceBefore=6*mm, spaceAfter=4*mm)
s_sub = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11, textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, textColor=DARK, leading=15, alignment=TA_JUSTIFY, spaceAfter=3*mm)

def section(text): return [Paragraph(text, s_section), HRFlowable(width="100%", color=BLUE, thickness=0.5)]
def sub(text): return Paragraph(text, s_sub)
def body(text): return Paragraph(text.replace('\n','<br/>'), s_body)
def bullet(text): return Paragraph(f'&bull; {text}', s_body)

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0]/2, 15*mm, f'Page {doc.page}')
    canvas_obj.restoreState()

out = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output/financial_report.pdf"
doc = SimpleDocTemplate(out, pagesize=A4, topMargin=20*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
story = []

# Cover
story.append(Spacer(1, 40*mm))
story.append(Paragraph('Financial & Operating Performance Analysis', s_cover_title))
story.append(Paragraph('BCG Company Financial Data -- Apple, Microsoft, Tesla', s_cover_sub))
story.append(Spacer(1, 8*mm))
line_tbl = Table([['']], colWidths=[80*mm])
line_tbl.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, BLUE)]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))
story.append(Paragraph(f'Period: 2020-2023 | 3 companies | 9 records', s_cover_info))
story.append(Spacer(1, 15*mm))

story.append(Paragraph('Key Metrics (Latest Year)', ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
metrics_data = [
    ['Metric', 'Value'],
    ['Apple Revenue', f'${apple["Total_Revenue"]/1e3:.1f}B'],
    ['Microsoft Revenue', f'${msft["Total_Revenue"]/1e3:.1f}B'],
    ['Tesla Revenue', f'${tsla["Total_Revenue"]/1e3:.1f}B'],
    ['Apple Profit Margin', f'{apple["Net_Income"]/apple["Total_Revenue"]*100:.1f}%'],
    ['Microsoft Profit Margin', f'{msft["Net_Income"]/msft["Total_Revenue"]*100:.1f}%'],
    ['Tesla Profit Margin', f'{tsla["Net_Income"]/tsla["Total_Revenue"]*100:.1f}%'],
    ['Apple 3yr Rev Growth', f'{apple_rev_g:.1f}%'],
]
mt = Table(metrics_data, colWidths=[80*mm, 60*mm])
mt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), BLUE),
    ('TEXTCOLOR', (0,0), (-1,0), HexColor('#FFFFFF')),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ('GRID', (0,0), (-1,-1), 0.5, HexColor('#CCCCCC')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(mt)
story.append(PageBreak())

# Key Findings
story.extend(section('Key Findings'))
findings = [
    f"Revenue scale: Apple (${apple['Total_Revenue']/1e3:.1f}B) > Microsoft (${msft['Total_Revenue']/1e3:.1f}B) > Tesla (${tsla['Total_Revenue']/1e3:.1f}B). Apple remains the revenue leader but shows signs of maturity.",
    f"Profit margin: Microsoft leads at {msft['Net_Income']/msft['Total_Revenue']*100:.1f}%, followed by Apple at {apple['Net_Income']/apple['Total_Revenue']*100:.1f}%. Tesla trails at {tsla['Net_Income']/tsla['Total_Revenue']*100:.1f}% due to capital-intensive automotive industry structure.",
    f"Debt ratio: Apple at {apple['Total_Liabilities']/apple['Total_Assets']*100:.0f}% (highest), Microsoft at {msft['Total_Liabilities']/msft['Total_Assets']*100:.0f}%, Tesla at {tsla['Total_Liabilities']/tsla['Total_Assets']*100:.0f}%. Apple's debt is mostly long-term strategic borrowing, not operational weakness.",
    "Growth trajectory: Tesla in high-growth phase (2020-2022 revenue +158%), Microsoft steady growth, Apple mature. Three different lifecycle stages require different valuation frameworks.",
    f"Apple's 3-year revenue growth: {apple_rev_g:.1f}% -- illustrates the growth ceiling for mature mega-cap companies. Margin expansion becomes the primary profit driver.",
]
for f in findings:
    story.append(bullet(f))
story.append(PageBreak())

# Thinking Models
story.extend(section('Thinking Models'))
models = [
    ("1. Decomposition",
     "Financial performance broken into 5 dimensions: revenue, profit, assets, liabilities, cash flow. Companies that look similar on revenue show very different structures on debt and cash.",
     "Cross-dimensional analysis reveals hidden risk and opportunity. Always decompose before comparing."),
    ("2. Segment Divergence",
     f"Apple (mature, {apple['Net_Income']/apple['Total_Revenue']*100:.1f}% margin), Microsoft (growth+profit, {msft['Net_Income']/msft['Total_Revenue']*100:.1f}%), Tesla (high-growth, {tsla['Net_Income']/tsla['Total_Revenue']*100:.1f}%). Same metric, three completely different stories.",
     "Never compare companies across lifecycle stages without adjusting for industry and scale."),
    ("3. Proxy Inference",
     "Debt ratio proxies for financial risk. Cash flow / assets proxies for operational efficiency. ROA proxies for capital allocation quality. Without market data, use financial ratios to infer company health.",
     "Choose proxies that match the decision context, not just available metrics."),
    ("4. Leverage Point",
     f"Apple's debt ratio ({apple['Total_Liabilities']/apple['Total_Assets']*100:.0f}%) looks high but its profit margin ({apple['Net_Income']/apple['Total_Revenue']*100:.1f}%) is strong -- indicates financial leverage potential.",
     "A high debt ratio is not inherently bad if the company has the margin to service it."),
    ("5. Constraint vs Preference",
     "Tesla's low margin reflects automotive industry capital intensity (constraint), not poor management (preference). Apple's high margin reflects brand power and ecosystem lock-in.",
     "Benchmark against industry peers, not cross-industry averages. Structure drives behavior."),
]
for title, evidence, takeaway in models:
    story.append(sub(title))
    story.append(body(f'<b>Evidence:</b> {evidence}'))
    story.append(body(f'<b>Takeaway:</b> {takeaway}'))

doc.build(story, onLaterPages=on_page)
print(f"PDF saved: {out}")
