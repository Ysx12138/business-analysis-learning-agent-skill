"""
Generate Standard Report PDF - ReportLab (Chinese, 3 models)
Uses Anthropic official PDF skill approach: reportlab
"""
import os
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Register Chinese font ──
FONT_PATH = '/System/Library/Fonts/STHeiti Light.ttc'
pdfmetrics.registerFont(TTFont('CN', FONT_PATH))
pdfmetrics.registerFont(TTFont('CN-Bold', FONT_PATH))

# ── Data ──
DATA_PATH = "/Users/sx/数据分析/telco_customer_churn/原始数据/telco_churn.csv"
OUTPUT_DIR = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/github/business-analysis-learning-agent-skill/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df = df.dropna(subset=['TotalCharges'])
df = df[df['tenure'] > 0]

df['tenure_group'] = pd.cut(df['tenure'],
    bins=[-1, 6, 12, 24, 48, 72],
    labels=['0-6月', '7-12月', '13-24月', '25-48月', '49-72月'])
for f in ['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies']:
    df[f+'_bin'] = df[f].apply(lambda x: 0 if x=='No' else (1 if x=='Yes' else 0))
df['service_count'] = sum(df[f+'_bin'] for f in ['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies'])
df['has_family'] = (df['Partner']=='Yes') | (df['Dependents']=='Yes')

BASE = df['Churn'].value_counts(normalize=True)['Yes']
contract_churn = df.groupby('Contract')['Churn'].value_counts(normalize=True).unstack()['Yes']
tenure_churn = df.groupby('tenure_group', observed=True)['Churn'].value_counts(normalize=True).unstack()['Yes']

# ── Styles ──
BLUE = HexColor('#2F5496')
LIGHT_BLUE = HexColor('#F2F7FB')
GRAY = HexColor('#666666')
DARK = HexColor('#282828')

styles = getSampleStyleSheet()

s_cover_title = ParagraphStyle('CoverTitle', fontName='CN-Bold', fontSize=22, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4*mm)
s_cover_sub = ParagraphStyle('CoverSub', fontName='CN', fontSize=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)
s_cover_line = ParagraphStyle('CoverLine', fontName='CN', fontSize=10, textColor=HexColor('#888888'), alignment=TA_CENTER, spaceAfter=2*mm)
s_section = ParagraphStyle('Section', fontName='CN-Bold', fontSize=14, textColor=BLUE, spaceBefore=6*mm, spaceAfter=4*mm)
s_sub = ParagraphStyle('Sub', fontName='CN-Bold', fontSize=11, textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body = ParagraphStyle('Body', fontName='CN', fontSize=10, textColor=DARK, leading=16, alignment=TA_JUSTIFY, spaceAfter=3*mm)
s_kv_key = ParagraphStyle('KVKey', fontName='CN-Bold', fontSize=10, textColor=DARK)
s_kv_val = ParagraphStyle('KVVal', fontName='CN', fontSize=10, textColor=DARK)
s_label = ParagraphStyle('Label', fontName='CN-Bold', fontSize=9, textColor=white, alignment=TA_CENTER)
s_box_text = ParagraphStyle('BoxText', fontName='CN', fontSize=9, textColor=DARK, leading=14, spaceAfter=1*mm)

# ── Helper Functions ──
def section(text):
    return [Paragraph(text, s_section), HRFlowable(width="100%", color=BLUE, thickness=0.5)]

def sub(text):
    return Paragraph(text, s_sub)

def body(text):
    return Paragraph(text.replace('\n', '<br/>'), s_body)

def kv(k, v):
    return Paragraph(f'<b>{k}:</b>  {v}', s_body)

def box(title, content):
    """Blue header box with light blue background"""
    hdr_data = [[Paragraph(title, s_label)]]
    hdr_tbl = Table(hdr_data, colWidths=[170*mm])
    hdr_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLUE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    body_data = [[Paragraph(content, s_box_text)]]
    body_tbl = Table(body_data, colWidths=[170*mm])
    body_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    tbl = Table([[hdr_tbl], [body_tbl]], colWidths=[170*mm])
    tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return tbl

def bullet(text):
    return Paragraph(f'• {text}', s_body)

# ── Page template callbacks ──
def on_first_page(canvas_obj, doc):
    pass

def on_later_pages(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('CN', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0]/2, 15, f'第 {doc.page} 页')
    # Header line
    canvas_obj.setStrokeColor(HexColor('#CCCCCC'))
    canvas_obj.setLineWidth(0.3)
    canvas_obj.line(20*mm, A4[1] - 15*mm, A4[0] - 20*mm, A4[1] - 15*mm)
    canvas_obj.setFont('CN', 7)
    canvas_obj.drawString(20*mm, A4[1] - 14*mm, 'Business Analysis Learning Agent - 思维模型提炼 (ReportLab)')
    canvas_obj.restoreState()

# ── Build document ──
output_path = os.path.join(OUTPUT_DIR, "telco_churn_reportlab.pdf")
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    topMargin=22*mm,
    bottomMargin=22*mm,
    leftMargin=20*mm,
    rightMargin=20*mm,
)

story = []

# ── Cover page ──
story.append(Spacer(1, 40*mm))
story.append(Paragraph('商业分析思维模型提炼', s_cover_title))
story.append(Spacer(1, 4*mm))
story.append(Paragraph('电信客户流失分析', s_cover_sub))
story.append(Paragraph('模式: standard_report (报告基于 ReportLab)', s_cover_sub))
story.append(Spacer(1, 8*mm))

# Blue line
line_data = [['']]
line_tbl = Table(line_data, colWidths=[80*mm])
line_tbl.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 1, BLUE),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(line_tbl)
story.append(Spacer(1, 8*mm))

story.append(Paragraph('Business Analysis Learning Agent Skill', s_cover_line))
story.append(Paragraph(f'数据集: {len(df)} 条 | 流失率: {BASE*100:.2f}%', s_cover_line))
story.append(Paragraph('PDF生成引擎: ReportLab (Anthropic PDF Skill)', s_cover_line))

story.append(PageBreak())

# ── Executive Summary ──
story.extend(section('摘要'))
story.append(body(f'本报告提取了在电信客户流失分析中应用的 3 个核心思维模型。整体流失率 {BASE*100:.2f}%，月付客户流失率 42.7%，前6个月新客流失率 53.3%。'))
story.append(kv('总客户数', f'{len(df):,}'))
story.append(kv('平均月费', f'${df["MonthlyCharges"].mean():.2f}'))
story.append(kv('平均在网月数', f'{df["tenure"].mean():.1f} 个月'))
story.append(kv('核心发现', '合同类型是流失最强预测因素（月付42.7% vs 两年约2.8%）'))

# ── Model A: 分解思维 ──
story.append(PageBreak())
story.extend(section('模型 A：分解思维'))
story.append(sub('拆解了什么？'))
monthly_share = (df['Contract']=='Month-to-month').mean()
monthly_churn_rate = float(contract_churn.get('Month-to-month', 0))
story.append(body(
    f'将总流失率 {BASE*100:.1f}% 按合同类型拆解。月付客户占总客户 {monthly_share*100:.1f}%，'
    f'流失率 {monthly_churn_rate*100:.1f}%，贡献了总流失的 {monthly_share*monthly_churn_rate*100:.1f}%。'
    f'一年和两年合同合计仅贡献 3.1 个百分点。'
))
story.append(sub('商业洞察'))
story.append(body('分解发现问题高度集中：改善月付客户的合同体验就能覆盖近 90% 的流失问题。资源不需要分散到所有群体。'))
story.append(sub('初学者收获'))
story.append(body(
    '永远要拆解汇总指标。26% 的流失率看起来中等，但拆开后发现月付群体 42.7%，两年群体只有 2.8%。平均值会隐藏真相。<br/><br/>'
    '下次你看到任何汇总数字——收入、转化率、满意度——先问一句：拆开按不同维度看会是什么样？'
))

# ── Model B: 分层差异思维 ──
story.append(PageBreak())
story.extend(section('模型 B：分层差异思维'))
story.append(sub('层级：在网时长分组'))
t0 = float(tenure_churn.iloc[0])
t4 = float(tenure_churn.iloc[-1])
story.append(body(
    f'0-6个月:   {t0*100:.1f}%<br/>'
    f'7-12个月:  {float(tenure_churn.iloc[1])*100:.1f}%<br/>'
    f'13-24个月: {float(tenure_churn.iloc[2])*100:.1f}%<br/>'
    f'25-48个月: {float(tenure_churn.iloc[3])*100:.1f}%<br/>'
    f'49-72个月: {t4*100:.1f}%<br/>'
    f'<br/>差异幅度: {t0/t4:.1f}倍'
))
story.append(box('核心发现',
    f'0-6个月流失率是49-72个月的 {t0/t4:.1f}倍。平均值26.6%不能代表任何一组——新客户是53%，老客户只有9.5%。'))
story.append(sub('商业含义'))
story.append(body(
    '头 6 个月是关键期。资源应集中在这里：入网引导、使用提示、首次体验优化。'
    '如果客户撑过第一年，流失概率下降一半以上。'
))
story.append(sub('初学者收获'))
story.append(body(
    '分层差异大时绝不要只看平均值。好比你问一桌子人"你们觉得菜怎么样"——一个人说咸一个人说淡，平均"刚刚好"其实什么都没说。'
    '分析客户也一样，要把不同群体分开看。'
))

# ── Model C: 杠杆点识别 ──
story.append(PageBreak())
story.extend(section('模型 C：杠杆点识别'))
story.append(sub('哪些群体值得优先改善？'))
story.append(body('杠杆值 = 客户占比 × 流失率差距（vs 基线）<br/><br/>候选群体评估：'))

monthly_leverage = monthly_share * (monthly_churn_rate - BASE)
new_share = float((df['tenure_group']=='0-6月').mean())
new_churn = t0
new_leverage = new_share * (new_churn - BASE)
fiber_share = float((df['InternetService']=='Fiber optic').mean())
fiber_churn = float(df[df['InternetService']=='Fiber optic']['Churn'].value_counts(normalize=True).get('Yes', 0))
fiber_leverage = fiber_share * (fiber_churn - BASE)

story.append(body(
    f'月付客户: 占比{monthly_share*100:.1f}%, 杠杆值{monthly_leverage:.3f}<br/>'
    f'前6月新客: 占比{new_share*100:.1f}%, 杠杆值{new_leverage:.3f}<br/>'
    f'光纤客户: 占比{fiber_share*100:.1f}%, 杠杆值{fiber_leverage:.3f}'
))
story.append(box('主要杠杆点',
    f'月付客户（杠杆值{monthly_leverage:.3f}）是最高影响力改善目标。同时影响55%的客户群体，投入产出比最高。'))
story.append(sub('为什么这很重要？'))
story.append(body(
    '资源有限。杠杆点思维确保你投资在回报最高的地方。<br/><br/>'
    '改善月付客户体验同时影响 55% 的客户，而仅修复光纤问题只触及 44% 的基础。<br/><br/>'
    '推荐：针对月付且在头 6 个月的客户，提供免费附加服务试用 + 年契转化优惠。'
))
story.append(sub('初学者收获'))
story.append(body(
    '面对多个问题，不要平均用力。先问两个问题：<br/>'
    '1. 这个问题影响多少人？<br/>'
    '2. 改善这个问题能让情况好多少？<br/>'
    '两者相乘，就是杠杆值。杠杆值最高的，就是你应该优先做的事。'
))

# ── Build ──
doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
print(f"PDF saved: {output_path}")
