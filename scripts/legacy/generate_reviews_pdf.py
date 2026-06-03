"""
Product Reviews Analysis — PDF Report (ReportLab)
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
import warnings; warnings.filterwarnings("ignore")

f = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/product_reviews_ratings/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
df = pd.read_csv(f)
df["reviews.date"] = pd.to_datetime(df["reviews.date"], errors="coerce")
df["review_len"] = df["reviews.text"].fillna("").str.len()

rd = df["reviews.rating"].value_counts().sort_index()
cats = df.groupby("categories").agg(
    评论数=("reviews.rating","count"),
    平均评分=("reviews.rating","mean"),
).sort_values("评论数",ascending=False)

one_star = df[df["reviews.rating"]==1].groupby("categories").size()
total_by_cat = df.groupby("categories").size()
one_star_rate = (one_star/total_by_cat*100).dropna().sort_values(ascending=False)

len_by_rating = df.groupby("reviews.rating")["review_len"].agg(["mean","median"])
helpful_by_rating = df.groupby("reviews.rating")["reviews.numHelpful"].mean()

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

out = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output/reviews_report.pdf"
doc = SimpleDocTemplate(out, pagesize=A4, topMargin=20*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
story = []

# Cover
story.append(Spacer(1, 40*mm))
story.append(Paragraph('Product Reviews & Ratings Analysis', s_cover_title))
story.append(Paragraph('Amazon Consumer Reviews Dataset', s_cover_sub))
story.append(Spacer(1, 8*mm))
line_tbl = Table([['']], colWidths=[80*mm])
line_tbl.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, BLUE)]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))
story.append(Paragraph(f'Reviews: {len(df):,} | Categories: {df["categories"].nunique()} | Brand: {df["brand"].unique()[0]}', s_cover_info))
story.append(Paragraph(f'Avg Rating: {df["reviews.rating"].mean():.2f} | Recommend Rate: {df["reviews.doRecommend"].mean()*100:.1f}%', s_cover_info))
story.append(Paragraph(f'Period: {df["reviews.date"].min().date()} ~ {df["reviews.date"].max().date()}', s_cover_info))
story.append(Spacer(1, 15*mm))

story.append(Paragraph('Key Metrics', ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
metrics_data = [
    ['Metric', 'Value'],
    ['Avg Rating', f'{df["reviews.rating"].mean():.2f}'],
    ['5-Star Share', f'{rd.get(5,0)/len(df)*100:.1f}%'],
    ['Recommend Rate', f'{df["reviews.doRecommend"].mean()*100:.1f}%'],
    ['Categories', f'{df["categories"].nunique()}'],
    ['Total Reviews', f'{len(df):,}'],
    ['Avg Helpful', f'{df["reviews.numHelpful"].mean():.2f}'],
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
story.append(sub('Rating Distribution'))
story.append(body(
    f'5-star: {rd.get(5,0)} ({rd.get(5,0)/len(df)*100:.1f}%)<br/>'
    f'4-star: {rd.get(4,0)} ({rd.get(4,0)/len(df)*100:.1f}%)<br/>'
    f'3-star: {rd.get(3,0)} ({rd.get(3,0)/len(df)*100:.1f}%)<br/>'
    f'2-star: {rd.get(2,0)} ({rd.get(2,0)/len(df)*100:.1f}%)<br/>'
    f'1-star: {rd.get(1,0)} ({rd.get(1,0)/len(df)*100:.1f}%)'
))

story.append(sub('Review Depth & Helpfulness'))
story.append(body(
    f'1-star reviews are the longest (mean {len_by_rating.loc[1,"mean"]:.0f} chars) and most helpful (mean {helpful_by_rating.loc[1]:.2f}).<br/>'
    f'5-star reviews are the shortest (mean {len_by_rating.loc[5,"mean"]:.0f} chars) and least helpful (mean {helpful_by_rating.loc[5]:.2f}).<br/>'
    f'1-star reviews have {len_by_rating.loc[1,"mean"]/len_by_rating.loc[5,"mean"]:.0f}x the length and {helpful_by_rating.loc[1]/helpful_by_rating.loc[5]:.0f}x the helpfulness of 5-star reviews.'
))

story.append(sub('Risk Categories'))
story.append(body(
    f'eBook Readers has the highest 1-star rate at {one_star_rate.iloc[0]:.1f}% (vs overall avg of {rd.get(1,0)/len(df)*100:.1f}%).<br/>'
    f'Top 5 categories by 1-star rate: {", ".join(f"{c[:30]} ({r:.1f}%)" for c, r in one_star_rate.head(5).items())}.'
))

story.append(sub('Recommendation Analysis'))
story.append(body(
    f'{df["reviews.doRecommend"].sum()} recommended ({df["reviews.doRecommend"].mean()*100:.1f}%) vs '
    f'{(~df["reviews.doRecommend"]).sum()} not recommended ({(~df["reviews.doRecommend"]).mean()*100:.1f}%).<br/>'
    f'The 235 non-recommended reviews are the most valuable signal for product improvement.'
))
story.append(PageBreak())

# Thinking Models
story.extend(section('Thinking Models'))
models = [
    ("1. Decomposition (Breakdown)",
     f"Avg rating {df['reviews.rating'].mean():.1f} decomposed by category, year, and recommendation status. The high average masks significant category-level differences.",
     "Always decompose high-level metrics. A 4.6 average tells you little about individual product issues."),
    ("2. Segment Divergence",
     f"Category avg ratings range from {cats['平均评分'].min():.2f} to {cats['平均评分'].max():.2f}. Review length varies 2x between 1-star and 5-star reviews.",
     "Averages flatten reality. Segment-level analysis reveals where the real problems are."),
    ("3. Proxy Inference",
     "Review length and helpfulness count are proxies for review quality. A short 5-star review is less informative than a detailed 1-star review.",
     "Use proxy metrics (length, helpfulness) to identify high-value reviews for detailed analysis."),
    ("4. Leverage Point Identification",
     f"Low-rated reviews (1-2 stars) are only {rd.get(1,0)+rd.get(2,0)} out of {len(df)} but contain the highest-value product improvement signals.",
     "Small segments with high leverage (low volume, high value) deserve disproportionate attention."),
    ("5. Constraint vs. Preference",
     'A low rating is a preference signal (product did not meet expectations). Non-recommendation is closer to a constraint signal (user believes others should not buy). Different analytical responses apply.',
     "Preference signals suggest product fixes; constraint signals suggest positioning or targeting fixes."),
]
for title, evidence, takeaway in models:
    story.append(sub(title))
    story.append(body(f'<b>Evidence:</b> {evidence}'))
    story.append(body(f'<b>Takeaway:</b> {takeaway}'))

doc.build(story, onLaterPages=on_page)
print(f"PDF saved: {out}")
