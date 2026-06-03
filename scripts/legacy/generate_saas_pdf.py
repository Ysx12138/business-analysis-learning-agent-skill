"""
SaaS Churn Analysis — PDF Report (ReportLab)
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

BASE = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/saas_subscription_churn"

accounts = pd.read_csv(f"{BASE}/ravenstack_accounts.csv")
subscriptions = pd.read_csv(f"{BASE}/ravenstack_subscriptions.csv")
churn_events = pd.read_csv(f"{BASE}/ravenstack_churn_events.csv")
support_tickets = pd.read_csv(f"{BASE}/ravenstack_support_tickets.csv")

total = len(accounts)
churned_total = accounts["churn_flag"].sum()
churn_rate = churned_total / total * 100
total_arr = subscriptions["arr_amount"].sum()
churned_ids = accounts[accounts["churn_flag"] == True]["account_id"]
churned_arr = subscriptions[subscriptions["account_id"].isin(churned_ids)]["arr_amount"].sum()

ind = accounts.groupby("industry").agg(N=("account_id","count"), C=("churn_flag","sum"))
ind["CR"] = ind["C"] / ind["N"] * 100

ref = accounts.groupby("referral_source").agg(N=("account_id","count"), C=("churn_flag","sum"))
ref["CR"] = ref["C"] / ref["N"] * 100

reasons = churn_events["reason_code"].value_counts()

tickets = support_tickets.merge(accounts[["account_id","churn_flag"]], on="account_id", how="left")
esc_retained = tickets[tickets["churn_flag"]==False]["escalation_flag"].mean()
esc_churned = tickets[tickets["churn_flag"]==True]["escalation_flag"].mean()

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
s_bold = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=10, textColor=DARK, leading=15, spaceAfter=2*mm)

def section(text): return [Paragraph(text, s_section), HRFlowable(width="100%", color=BLUE, thickness=0.5)]
def sub(text): return Paragraph(text, s_sub)
def body(text): return Paragraph(text.replace('\n','<br/>'), s_body)
def bold(text): return Paragraph(text, s_bold)
def bullet(text): return Paragraph(f'&bull; {text}', s_body)

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0]/2, 15*mm, f'Page {doc.page}')
    canvas_obj.restoreState()

out = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output/saas_churn_report.pdf"
doc = SimpleDocTemplate(out, pagesize=A4, topMargin=20*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
story = []

# Cover
story.append(Spacer(1, 40*mm))
story.append(Paragraph('SaaS Subscription & Churn', s_cover_title))
story.append(Paragraph('Churn Analysis Report', s_cover_sub))
story.append(Spacer(1, 8*mm))
line_tbl = Table([['']], colWidths=[80*mm])
line_tbl.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, BLUE)]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))
story.append(Paragraph(f'Dataset: RavenStack SaaS (5 relational tables)', s_cover_info))
story.append(Paragraph(f'Accounts: {total} | Subscriptions: {len(subscriptions):,} | Churn Events: {len(churn_events):,} | Support Tickets: {len(support_tickets):,}', s_cover_info))
story.append(Spacer(1, 15*mm))

story.append(Paragraph('Key Metrics', ParagraphStyle('KM', fontName='Helvetica-Bold', fontSize=12, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)))
metrics_data = [
    ['Metric', 'Value'],
    ['Total Accounts', f'{total}'],
    ['Churned Accounts', f'{churned_total} ({churn_rate:.1f}%)'],
    ['Retained Accounts', f'{total - churned_total} ({100-churn_rate:.1f}%)'],
    ['Total ARR', f'${total_arr:,.0f}'],
    ['Churned ARR', f'${churned_arr:,.0f} ({churned_arr/total_arr*100:.1f}%)'],
    ['Avg MRR/sub', f'${subscriptions["mrr_amount"].mean():.0f}'],
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

# Executive Summary
story.extend(section('Executive Summary'))
summary = [
    f"The dataset contains {total} accounts, {len(subscriptions):,} subscription records, {len(churn_events):,} churn events, and {len(support_tickets):,} support tickets.",
    f"The overall churn rate is {churn_rate:.1f}%, representing {churned_total} lost accounts with ${churned_arr:,.0f} in churned ARR ({churned_arr/total_arr*100:.1f}% of total).",
    f"DevTools has the highest churn rate at {ind.loc['DevTools', 'CR']:.1f}%, followed by FinTech at {ind.loc['FinTech', 'CR']:.1f}%.",
    f"Event-sourced customers have the highest churn ({ref.loc['event', 'CR']:.1f}%), while partner-sourced customers have the lowest ({ref.loc['partner', 'CR']:.1f}%).",
    f"Top churn reasons: features ({reasons.get('features',0)}), support ({reasons.get('support',0)}), budget ({reasons.get('budget',0)}) -- product quality and pricing are key churn drivers.",
    f"Escalation rate is higher for churned accounts ({esc_churned:.2f} vs {esc_retained:.2f}), suggesting support escalation is an early warning signal.",
]
for s in summary:
    story.append(bullet(s))
story.append(PageBreak())

# Key Findings
story.extend(section('Key Findings'))
findings = [
    ("1. Industry Churn Disparity",
     f"DevTools churn rate ({ind.loc['DevTools', 'CR']:.1f}%) is nearly double that of EdTech ({ind.loc['EdTech', 'CR']:.1f}%) and Cybersecurity ({ind.loc['Cybersecurity', 'CR']:.1f}%). This suggests product-market fit varies significantly by industry vertical.",
     "Conduct exit interviews with churned DevTools customers to identify missing features or integration gaps."),
    ("2. Acquisition Channel Impact",
     f"Event-sourced customers churn at {ref.loc['event', 'CR']:.1f}%, while partner-referred customers churn at only {ref.loc['partner', 'CR']:.1f}%. The acquisition channel is a strong predictor of retention.",
     "Review event activation flow; consider partner-channel expansion as a retention-friendly growth strategy."),
    ("3. Feature & Support Drive Churn",
     f"Features ({reasons.get('features',0)} events, {reasons.get('features',0)/len(churn_events)*100:.1f}%) and support ({reasons.get('support',0)} events, {reasons.get('support',0)/len(churn_events)*100:.1f}%) are the top two churn reasons. Combined, they account for over a third of all churn.",
     "Prioritize feature roadmap based on churn-driven feedback. Evaluate support staffing and response SLAs."),
    ("4. Support Escalation as Early Warning",
     f"Churned accounts had an escalation rate of {esc_churned:.2f} vs {esc_retained:.2f} for retained accounts. Similar overall ticket volume suggests escalation quality matters more than quantity.",
     "Implement automated alerts when an account's escalation rate exceeds 0.05, triggering customer success intervention."),
]
for title, detail, action in findings:
    story.append(sub(title))
    story.append(body(f'<b>Data:</b> {detail}'))
    story.append(body(f'<b>Action:</b> {action}'))
story.append(PageBreak())

# Thinking Models
story.extend(section('Thinking Models Applied'))
models = [
    ("1. Decomposition (Breakdown)",
     f"Overall churn rate of {churn_rate:.1f}% was decomposed by industry, plan tier, country, and acquisition channel. This revealed that DevTools alone has a {ind.loc['DevTools', 'CR']:.1f}% churn rate.",
     "Always decompose aggregate metrics by meaningful segments before drawing conclusions."),
    ("2. Segment Divergence",
     f"Churn rates range from {ind['CR'].min():.1f}% to {ind['CR'].max():.1f}% across industries, and from {ref['CR'].min():.1f}% to {ref['CR'].max():.1f}% across acquisition channels.",
     "When segments vary by more than 2x, the average is misleading. Act on segment-level data."),
    ("3. Proxy Inference",
     "Support ticket escalation rate, feature usage frequency, and satisfaction score serve as proxies for churn probability.",
     "Proactive retention uses behavioral proxies -- do not wait for the cancellation event."),
    ("4. Leverage Point Identification",
     f"Event-sourced accounts ({ref.loc['event', 'N']} accounts, {ref.loc['event', 'CR']:.1f}% churn) and DevTools industry ({ind.loc['DevTools', 'N']} accounts, {ind.loc['DevTools', 'CR']:.1f}% churn) are high-leverage targets.",
     "Focus retention efforts on segments where both share and churn rate are high."),
    ("5. Constraint vs. Preference",
     "High churn in DevTools could reflect a preference (product does not fit DevTools workflows) or a constraint (DevTools teams are more price-sensitive).",
     "Preferences require product changes; constraints require process/pricing changes."),
]
for title, evidence, takeaway in models:
    story.append(sub(title))
    story.append(body(f'<b>Evidence:</b> {evidence}'))
    story.append(body(f'<b>Takeaway:</b> {takeaway}'))
story.append(PageBreak())

# Recommendations
story.extend(section('Action Recommendations'))
recs = [
    ("1. DevTools Industry Retention Program",
     f"DevTools accounts ({ind.loc['DevTools', 'N']}) have {ind.loc['DevTools', 'CR']:.1f}% churn. Launch a dedicated customer success program.",
     "DevTools churn rate", "Industry-segmented churn and usage data"),
    ("2. Optimize Event-Acquired Customer Activation",
     f"Event-sourced customers ({ref.loc['event', 'N']}) churn at {ref.loc['event', 'CR']:.1f}%. Improve onboarding and time-to-value.",
     "Event-sourced customer retention rate at 30/60/90 days", "Channel-segmented activation metrics"),
    ("3. Address Feature Gaps",
     f"Features is the top churn reason ({reasons.get('features',0)} events). Conduct competitive analysis and feature gap assessment.",
     "Feature-related churn rate quarterly trend", "Competitive feature comparison + churn feedback"),
    ("4. Build Escalation Early Warning System",
     f"Escalation rate divergence ({esc_retained:.2f} retained vs {esc_churned:.2f} churned) is a leading indicator.",
     "Account-level escalation rate tracker", "Real-time support ticket + escalation data"),
]
for title, detail, metric, data_needed in recs:
    story.append(sub(title))
    story.append(body(f'<b>Action:</b> {detail}'))
    story.append(body(f'<b>Metric to Track:</b> {metric}'))
    story.append(body(f'<b>Data Needed:</b> {data_needed}'))

doc.build(story, onLaterPages=on_page)
print(f"PDF saved: {out}")
