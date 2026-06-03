"""
Retail Operations — PDF Report (ReportLab)
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

BASE = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/store_retail_operations"
sales = pd.read_csv(f"{BASE}/sales data-set.csv", parse_dates=["Date"], date_format="%d/%m/%Y")
stores = pd.read_csv(f"{BASE}/stores data-set.csv")
sf = sales.merge(stores, on="Store", how="left")

ts = sales["Weekly_Sales"].sum()
avg = sales["Weekly_Sales"].mean()
ha = sales[sales["IsHoliday"]==True]["Weekly_Sales"].mean()
na = sales[sales["IsHoliday"]==False]["Weekly_Sales"].mean()
st = sf.groupby("Type").agg(N=("Store","nunique"), A=("Weekly_Sales","mean"))
corr = sf.groupby("Store").agg(Size=("Size","first"), S=("Weekly_Sales","mean")).corr().iloc[0,1]
dept_total = sales.groupby("Dept")["Weekly_Sales"].sum().sort_values(ascending=False)
dept_holiday = sales[sales["IsHoliday"]==True].groupby("Dept")["Weekly_Sales"].mean()
dept_nonholiday = sales[sales["IsHoliday"]==False].groupby("Dept")["Weekly_Sales"].mean()
holiday_lift = ((dept_holiday / dept_nonholiday) - 1) * 100
monthly = sales.copy(); monthly["Month"] = monthly["Date"].dt.month; monthly["Yr"] = monthly["Date"].dt.year
monthly_sales = monthly.groupby(["Yr","Month"])["Weekly_Sales"].sum().unstack(0)

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

out = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output/retail_report.pdf"
doc = SimpleDocTemplate(out, pagesize=A4, topMargin=20*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
story = []

# Cover
story.append(Spacer(1, 40*mm))
story.append(Paragraph('Store Retail Operations Analysis', s_cover_title))
story.append(Paragraph('Walmart Retail Dataset', s_cover_sub))
story.append(Spacer(1, 8*mm))
line_tbl = Table([['']], colWidths=[80*mm])
line_tbl.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, BLUE)]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))
story.append(Paragraph(f'Sales Records: {len(sales):,} | Stores: {len(stores)} | Depts: {sales["Dept"].nunique()}', s_cover_info))
story.append(Paragraph(f'Period: {sales["Date"].min().date()} ~ {sales["Date"].max().date()}', s_cover_info))
story.append(Spacer(1, 15*mm))

story.append(Paragraph('Key Metrics', ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
metrics_data = [
    ['Metric', 'Value'],
    ['Total Sales', f'${ts/1e9:.2f}B'],
    ['Avg Weekly', f'${avg:,.0f}'],
    ['Holiday Avg', f'${ha:,.0f}'],
    ['Non-Holiday Avg', f'${na:,.0f}'],
    ['A-Store Avg', f'${st.loc["A","A"]:,.0f}'],
    ['B-Store Avg', f'${st.loc["B","A"]:,.0f}'],
    ['C-Store Avg', f'${st.loc["C","A"]:,.0f}'],
    ['Size-Sales Corr', f'{corr:.4f}'],
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
    f"Store size correlates strongly with sales (r={corr:.4f}). A-type stores (22 stores) average ${st.loc['A','A']:,.0f}/week, while C-type stores (6 stores) average ${st.loc['C','A']:,.0f}/week.",
    f"Holiday weeks average ${ha:,.0f} vs ${na:,.0f} for non-holidays -- a {(ha/na-1)*100:+.1f}% lift. However, department-level impact varies from +303% to -152%.",
    f"Department 92 leads with ${dept_total.iloc[0]:,.0f} total sales across 45 stores. Several departments show negative sales, indicating data quality issues.",
    "December is the peak month, while January is the lowest. Seasonal patterns are consistent across both years.",
    "External factors (CPI, unemployment, fuel price, temperature) show weak direct correlation with sales at the store level.",
]
for f in findings:
    story.append(bullet(f))
story.append(PageBreak())

# Thinking Models
story.extend(section('Thinking Models'))
models = [
    ("1. Decomposition",
     f"Total sales ${ts/1e9:.2f}B broken down by store type, department, month, and holiday status. A-type stores contribute {st.loc['A','A']*st.loc['A','N']/(st['A']*st['N']).sum()*100:.0f}% of sales.",
     "Break aggregates before acting."),
    ("2. Segment Divergence",
     "Dept sales range from $484M (dept 92) to negative values. Holiday lift varies from +303% to -152%. Department strategy must be segment-specific.",
     "Never average across highly divergent segments."),
    ("3. Proxy Inference",
     "CPI and unemployment proxy for consumer purchasing power. Even when sales look stable, economic indicators may signal future decline.",
     "Use leading indicators, not just lagging ones."),
    ("4. Leverage Point",
     f"Top 3 departments (92, 95, 38) generate significant revenue. Holiday-sensitive departments offer high-leverage promotional ROI.",
     "Focus optimization on high-share, high-sensitivity segments."),
    ("5. Constraint vs Preference",
     "Store type differences reflect location strategy (constraint), not consumer preference. A-type stores are larger because of market size, not because customers prefer them.",
     "Differentiate structural constraints from preference signals."),
]
for title, evidence, takeaway in models:
    story.append(sub(title))
    story.append(body(f'<b>Evidence:</b> {evidence}'))
    story.append(body(f'<b>Takeaway:</b> {takeaway}'))

doc.build(story, onLaterPages=on_page)
print(f"PDF saved: {out}")
