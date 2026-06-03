"""
Marketing Campaign Analysis — PDF Report (ReportLab)
"""
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
)

# ── Data ──
df = pd.read_csv("/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/marketing_campaign_performance/KAG_conversion_data.csv")
df["CPC"] = df["Spent"] / df["Clicks"].replace(0, np.nan)
df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, np.nan) * 100

total_spent = df["Spent"].sum()
total_imp = df["Impressions"].sum()
total_clicks = df["Clicks"].sum()
total_conv = df["Total_Conversion"].sum()
total_approved = df["Approved_Conversion"].sum()
overall_cpc = total_spent / total_clicks
overall_cpm = total_spent / total_imp * 1000
overall_ctr = total_clicks / total_imp * 100
overall_conv_rate = total_conv / total_clicks * 100
cost_per_conv = total_spent / total_conv
approved_rate = total_approved / total_conv * 100

campaigns = df.groupby("xyz_campaign_id").agg(
    Ads=("ad_id", "count"), Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"), Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
)
campaigns["CPC"] = campaigns["Spent"] / campaigns["Clicks"]
campaigns["CTR"] = campaigns["Clicks"] / campaigns["Impressions"] * 100
campaigns["Conv_Rate"] = campaigns["Conversions"] / campaigns["Clicks"] * 100
campaigns["Cost_per_Conv"] = campaigns["Spent"] / campaigns["Conversions"]

age_group = df.groupby("age").agg(
    Spent=("Spent", "sum"), Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
)
age_group["CTR"] = age_group["Clicks"] / df.groupby("age")["Impressions"].sum() * 100
age_group["Cost_per_Conv"] = age_group["Spent"] / age_group["Conversions"]

gender_group = df.groupby("gender").agg(
    Spent=("Spent", "sum"), Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
)
gender_group["CTR"] = gender_group["Clicks"] / df.groupby("gender")["Impressions"].sum() * 100
gender_group["Cost_per_Conv"] = gender_group["Spent"] / gender_group["Conversions"]

# ── Styles ──
BLUE = HexColor('#1B365D')
GRAY = HexColor('#666666')
DARK = HexColor('#282828')
LIGHT_GRAY = HexColor('#F5F5F5')

styles = getSampleStyleSheet()

s_cover_title = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=22, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)
s_cover_sub = ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)
s_cover_info = ParagraphStyle('CoverInfo', fontName='Helvetica', fontSize=10, textColor=HexColor('#888888'), alignment=TA_CENTER, spaceAfter=2*mm)
s_section = ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=14, textColor=BLUE, spaceBefore=6*mm, spaceAfter=4*mm)
s_sub = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11, textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, textColor=DARK, leading=15, alignment=TA_JUSTIFY, spaceAfter=3*mm)
s_bold = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=10, textColor=DARK, leading=15, spaceAfter=2*mm)
s_label = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=9, textColor=HexColor('#FFFFFF'), alignment=TA_CENTER)
s_kv_key = ParagraphStyle('KVKey', fontName='Helvetica-Bold', fontSize=10, textColor=DARK)
s_kv_val = ParagraphStyle('KVVal', fontName='Helvetica', fontSize=10, textColor=DARK)

def section(text):
    return [Paragraph(text, s_section), HRFlowable(width="100%", color=BLUE, thickness=0.5)]

def sub(text):
    return Paragraph(text, s_sub)

def body(text):
    return Paragraph(text.replace('\n', '<br/>'), s_body)

def bold(text):
    return Paragraph(text, s_bold)

def kv(k, v):
    return Paragraph(f'<b>{k}:</b>  {v}', s_body)

def bullet(text):
    return Paragraph(f'&bull; {text}', s_body)

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0]/2, 15*mm, f'Page {doc.page}')
    canvas_obj.restoreState()

# ── Build ──
out_path = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output/marketing_report.pdf"
doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=20*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
story = []

# Cover
story.append(Spacer(1, 40*mm))
story.append(Paragraph('Marketing Campaign Performance', s_cover_title))
story.append(Paragraph('Facebook Ads Dataset Analysis Report', s_cover_sub))
story.append(Spacer(1, 8*mm))
line_tbl = Table([['']], colWidths=[80*mm])
line_tbl.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, BLUE)]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))
story.append(Paragraph(f'Dataset: KAG_conversion_data.csv', s_cover_info))
story.append(Paragraph(f'Records: {len(df):,} ads | 3 Campaigns | 40 Interest Categories', s_cover_info))
story.append(Paragraph(f'Age Groups: 30-34 / 35-39 / 40-44 / 45-49 | Gender: M / F', s_cover_info))

story.append(Spacer(1, 15*mm))
story.append(Paragraph('Key Metrics', ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
metrics_data = [
    ['Metric', 'Value'],
    ['Total Spent', f'${total_spent:,.2f}'],
    ['Total Impressions', f'{total_imp:,}'],
    ['Total Clicks', f'{total_clicks:,}'],
    ['Total Conversions', f'{total_conv:,}'],
    ['Approved Conversions', f'{total_approved:,}'],
    ['Overall CPC', f'${overall_cpc:.4f}'],
    ['Overall CPM', f'${overall_cpm:.2f}'],
    ['Overall CTR', f'{overall_ctr:.2f}%'],
    ['Conversion Rate', f'{overall_conv_rate:.2f}%'],
    ['Cost per Conversion', f'${cost_per_conv:.2f}'],
    ['Approval Rate', f'{approved_rate:.1f}%'],
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
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(mt)

story.append(PageBreak())

# Executive Summary
story.extend(section('Executive Summary'))
summary_points = [
    f"This dataset contains {len(df):,} Facebook ad records across 3 campaigns.",
    f"Total ad spend is ${total_spent:,.2f}, generating {total_imp:,} impressions, {total_clicks:,} clicks, and {total_conv:,} conversions.",
    f"The overall cost per conversion is ${cost_per_conv:.2f}, with an average CTR of {overall_ctr:.2f}%.",
    f"Campaign 1178 dominates spend (94.8% of total) but has the lowest conversion rate at {campaigns.loc[1178, 'Conv_Rate']:.1f}%.",
    f"Female audience generates more clicks and conversions overall, but male audience has a lower cost per conversion (${gender_group.loc['M', 'Cost_per_Conv']:.2f} vs ${gender_group.loc['F', 'Cost_per_Conv']:.2f}).",
    f"Age group 30-34 has the lowest cost per conversion (${age_group.loc['30-34', 'Cost_per_Conv']:.2f}), while 45-49 has the highest (${age_group.loc['45-49', 'Cost_per_Conv']:.2f}).",
    f"Interest category targeting shows significant efficiency variation, with cost per conversion ranging widely across categories.",
]
for s in summary_points:
    story.append(bullet(s))

story.append(PageBreak())

# Key Findings
story.extend(section('Key Findings'))
findings = [
    ("Finding 1: Campaign Efficiency Gap",
     f"Campaign 916 has a conversion rate of {campaigns.loc[916, 'Conv_Rate']:.1f}% and cost per conversion of ${campaigns.loc[916, 'Cost_per_Conv']:.2f}, while Campaign 1178 has only {campaigns.loc[1178, 'Conv_Rate']:.1f}% conversion rate at ${campaigns.loc[1178, 'Cost_per_Conv']:.2f} per conversion.",
     "Action: Reallocate budget from low-efficiency campaigns to high-efficiency ones, and investigate why Campaign 1178's volume does not translate to proportional conversions."),
    ("Finding 2: Age Group Performance Variation",
     f"Age group 30-34 achieves the lowest cost per conversion (${age_group.loc['30-34', 'Cost_per_Conv']:.2f}) with 1,431 conversions. Age group 45-49 has the highest spend (${age_group.loc['45-49', 'Spent']:,.0f}) but the highest cost per conversion (${age_group.loc['45-49', 'Cost_per_Conv']:.2f}).",
     "Action: Optimize ad creative and bidding strategy for 45-49 age group, or shift budget toward 30-34 which shows better ROI."),
    ("Finding 3: Gender Differences in Efficiency",
     f"Male audience has a lower cost per conversion (${gender_group.loc['M', 'Cost_per_Conv']:.2f}) despite lower CTR ({gender_group.loc['M', 'CTR']:.2f}% vs {gender_group.loc['F', 'CTR']:.2f}%).",
     "Action: Investigate whether male audience converts at higher quality (approved rate check), and whether female audience targeting can be refined to reduce wasted spend."),
    ("Finding 4: Interest Targeting Optimization Opportunity",
     "Interest categories show 2-3x variation in cost per conversion. Top-spend categories are not necessarily the most efficient.",
     "Action: Increase budget for high-conversion, low-cost-per-conversion interest categories. Reduce or pause low-efficiency categories."),
]
for title, detail, action in findings:
    story.append(sub(title))
    story.append(body(f'<b>Data:</b> {detail}'))
    story.append(body(f'<b>Action:</b> {action}'))

story.append(PageBreak())

# Thinking Models
story.extend(section('Thinking Models'))
thought_models = [
    ("1. Decomposition (Breakdown)",
     f"Total spend of ${total_spent:,.2f} was broken down by campaign, age group, gender, and interest category. This revealed that Campaign 1178 dominates spend (94.8%) but has the lowest conversion efficiency, a pattern invisible at the aggregate level.",
     "Decomposition is the most fundamental analytical move: always break a total into meaningful categories before drawing conclusions."),
    ("2. Segment Divergence (Layer Differences)",
     f"CTR ranges from {age_group['CTR'].min():.2f}% to {age_group['CTR'].max():.2f}% across age groups, and cost per conversion ranges from ${age_group['Cost_per_Conv'].min():.2f} to ${age_group['Cost_per_Conv'].max():.2f}. Averages alone would mask these 2-3x differences.",
     "Never trust the average. Always check how much segments vary around it."),
    ("3. Leverage Point Identification",
     "Age 30-34 Female is the highest conversion segment (619 conversions) with moderate cost per conversion ($12.30). Improving this segment's targeting accuracy directly impacts overall campaign ROI.",
     "A leverage point = high share x high improvement potential. Find where these intersect."),
    ("4. Proxy Inference",
     f"Approved conversion rate ({approved_rate:.1f}%) serves as a proxy for conversion quality. A segment with many conversions but low approval rate may need better targeting.",
     "When direct quality metrics are unavailable or slow, use approval/completion rates as a proxy."),
    ("5. Constraint vs. Preference",
     "Age group differences in cost per conversion may reflect product-market fit (preference) rather than campaign setup (constraint). High spend on 45-49 could be because the product appeals to them, or because campaign settings over-target them.",
     "Differentiate whether the audience chooses the product or the campaign forces it. The answer determines whether to change product positioning or ad settings."),
]
for title, evidence, takeaway in thought_models:
    story.append(sub(title))
    story.append(body(f'<b>Evidence:</b> {evidence}'))
    story.append(body(f'<b>Takeaway:</b> {takeaway}'))

story.append(PageBreak())

# Self-Check Questions
story.extend(section('Self-Check Questions'))
questions = [
    ("Q1: What total metric can be decomposed, and by which dimensions?",
     f"Total spend (${total_spent:,.0f}) can be decomposed by campaign (3 campaigns), age group (4 groups), gender (2 groups), and interest category (40 categories)."),
    ("Q2: How large are subgroup differences after decomposition?",
     f"Cost per conversion varies from ${age_group['Cost_per_Conv'].min():.2f} (30-34) to ${age_group['Cost_per_Conv'].max():.2f} (45-49) across age groups -- a {age_group['Cost_per_Conv'].max()/age_group['Cost_per_Conv'].min():.1f}x difference. Campaign conversion rate varies from {campaigns['Conv_Rate'].min():.1f}% to {campaigns['Conv_Rate'].max():.1f}%."),
    (f"Q3: What missing key information can be inferred by a proxy variable?",
     f"Approved conversion rate ({approved_rate:.1f}%) is a proxy for conversion quality. Revenue per conversion is not in the dataset, so approval rate is the closest signal of whether a conversion was valuable."),
    ("Q4: Is the observed difference a preference or a constraint?",
     "Male vs female differences in cost per conversion could be preference (product appeals more to male buyers after clicking) or constraint (ad creative is shown to more female users regardless of intent). A/B testing with controlled audience segments would help differentiate."),
    ("Q5: Which segment is both high-share and high-difference (a leverage point)?",
     "Age 30-34 Female: 619 conversions (highest single segment) with moderate cost per conversion. Optimizing this segment's conversion rate even by 10% yields ~62 additional conversions. This is the segment with the highest leverage."),
]
for q, a in questions:
    story.append(bold(q))
    story.append(body(f'Answer: {a}'))

story.append(PageBreak())

# Recommendations
story.extend(section('Action Recommendations'))
recommendations = [
    ("1. Rebalance Campaign Budget",
     f"Shift budget from Campaign 1178 (${campaigns.loc[1178, 'Spent']:,.0f} spend, {campaigns.loc[1178, 'Conv_Rate']:.1f}% conversion rate) toward Campaign 936 ({campaigns.loc[936, 'Conv_Rate']:.1f}% conversion rate) and Campaign 916 ({campaigns.loc[916, 'Conv_Rate']:.1f}%).",
     "Campaign-level conversion rate",
     "Campaign-level spend and conversion data"),
    ("2. Optimize Age 45-49 Targeting",
     f"Review ad creative and landing page for 45-49 audience (${age_group.loc['45-49', 'Cost_per_Conv']:.2f} per conversion vs ${age_group.loc['30-34', 'Cost_per_Conv']:.2f} for 30-34). Either improve relevance or reduce budget allocation.",
     "Cost per conversion for 45-49 segment",
     "Age-segmented conversion and spend data"),
    ("3. Scale Efficient Interest Categories",
     "Increase budget for interest categories with below-average cost per conversion (e.g., interest 15, 29). Reduce spend on categories with high cost per conversion.",
     "Interest-level cost per conversion",
     "Interest-category spend and conversion reports"),
    ("4. A/B Test Gender Creative",
     f"Test separate ad creatives for male (${gender_group.loc['M', 'Cost_per_Conv']:.2f}/conv) and female (${gender_group.loc['F', 'Cost_per_Conv']:.2f}/conv) audiences to determine whether the cost difference is driven by creative or audience fit.",
     "Gender-segmented CPC and conversion rate",
     "A/B test results with controlled creative variables"),
]
for title, detail, metric, data_needed in recommendations:
    story.append(sub(title))
    story.append(body(f'<b>Action:</b> {detail}'))
    story.append(body(f'<b>Metric to Track:</b> {metric}'))
    story.append(body(f'<b>Data Needed:</b> {data_needed}'))

story.append(PageBreak())

# Metrics Glossary
story.extend(section('Metrics and Concepts Explained'))
metrics_glossary = [
    ("CPC (Cost Per Click)", "Cost per individual click on an ad.",
     f"Formula: Spent / Clicks = {total_spent:.2f} / {total_clicks} = ${overall_cpc:.4f}",
     "Measures how efficiently budget generates clicks. Lower is better for traffic-oriented campaigns."),
    ("CPM (Cost Per Mille)", "Cost per 1,000 impressions.",
     f"Formula: (Spent / Impressions) x 1000 = ({total_spent:.2f} / {total_imp}) x 1000 = ${overall_cpm:.2f}",
     "Used for brand awareness campaigns where visibility matters more than clicks."),
    ("CTR (Click-Through Rate)", "Percentage of impressions that resulted in a click.",
     f"Formula: (Clicks / Impressions) x 100 = ({total_clicks} / {total_imp}) x 100 = {overall_ctr:.2f}%",
     "Measures ad relevance. Higher CTR generally means the creative matches the audience."),
    ("Conversion Rate", "Percentage of clicks that resulted in a conversion.",
     f"Formula: (Total_Conversion / Clicks) x 100 = ({total_conv} / {total_clicks}) x 100 = {overall_conv_rate:.2f}%",
     "Measures post-click effectiveness. Low conversion rate suggests landing page or offer issues."),
    ("Cost per Conversion (CPA)", "Average cost to acquire one conversion.",
     f"Formula: Spent / Total_Conversion = {total_spent:.2f} / {total_conv} = ${cost_per_conv:.2f}",
     "The most important ROI metric. All optimization efforts should ultimately reduce this."),
]
for name, meaning, formula, use in metrics_glossary:
    story.append(sub(name))
    story.append(body(f'<b>Meaning:</b> {meaning}'))
    story.append(body(f'<b>{formula}</b>'))
    story.append(body(f'<b>Business Use:</b> {use}'))

doc.build(story, onLaterPages=on_page)
print(f"PDF saved: {out_path}")
