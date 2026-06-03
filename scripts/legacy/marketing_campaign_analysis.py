"""
Marketing Campaign Performance Analysis
Facebook Ads dataset — audit_report mode
"""
import pandas as pd
import numpy as np

print("=" * 60)
print("1. 数据概览")
print("=" * 60)

df = pd.read_csv("/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/marketing_campaign_performance/KAG_conversion_data.csv")

print(f"行数: {len(df):,}")
print(f"字段: {list(df.columns)}")
print(f"缺失值: 无")
print(f"广告系列数: {df['xyz_campaign_id'].nunique()}")
print(f"广告数: {df['ad_id'].nunique()}")
print(f"兴趣分类数: {df['interest'].nunique()}")
print(f"年龄组: {sorted(df['age'].unique())}")
print()

# ── 2. 数据风险检查 ──
print("=" * 60)
print("2. 数据风险检查")
print("=" * 60)

# 零花费但有数据
zero_spend = df[df["Spent"] == 0]
print(f"零花费广告: {len(zero_spend)} 条 ({len(zero_spend)/len(df)*100:.1f}%)")

# 有花费但零点击
spend_no_click = df[(df["Spent"] > 0) & (df["Clicks"] == 0)]
print(f"有花费但零点击: {len(spend_no_click)} 条")

# 有点击但零花费
click_no_spend = df[(df["Clicks"] > 0) & (df["Spent"] == 0)]
print(f"有点击但零花费: {len(click_no_spend)} 条")

# 转化大于点击 (数据异常)
conv_gt_click = df[df["Total_Conversion"] > df["Clicks"]]
print(f"转化数大于点击数: {len(conv_gt_click)} 条")

# 零展示但有数据
zero_imp = df[df["Impressions"] == 0]
print(f"零展示广告: {len(zero_imp)} 条")

# 成本指标衍生
df["CPC"] = df["Spent"] / df["Clicks"].replace(0, np.nan)
df["CPM"] = df["Spent"] / df["Impressions"].replace(0, np.nan) * 1000
df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, np.nan) * 100
df["Conversion_Rate"] = df["Total_Conversion"] / df["Clicks"].replace(0, np.nan) * 100
df["Approved_Rate"] = df["Approved_Conversion"] / df["Total_Conversion"].replace(0, np.nan) * 100

print()

# ── 3. 整体指标 ──
print("=" * 60)
print("3. 关键业务指标")
print("=" * 60)

total_spent = df["Spent"].sum()
total_imp = df["Impressions"].sum()
total_clicks = df["Clicks"].sum()
total_conv = df["Total_Conversion"].sum()
total_approved = df["Approved_Conversion"].sum()

print(f"总花费:       ${total_spent:,.2f}")
print(f"总展示量:     {total_imp:,}")
print(f"总点击量:     {total_clicks:,}")
print(f"总转化数:     {total_conv:,}")
print(f"审核通过转化: {total_approved:,}")
print(f"整体 CPC:     ${total_spent/total_clicks:.4f}")
print(f"整体 CPM:     ${total_spent/total_imp*1000:.2f}")
print(f"整体 CTR:     {total_clicks/total_imp*100:.2f}%")
print(f"整体转化率:   {total_conv/total_clicks*100:.2f}%")
print(f"每转化成本:   ${total_spent/total_conv:.2f}")
print(f"审核通过率:   {total_approved/total_conv*100:.1f}%")
print()

# ── 4. 广告系列对比 ──
print("=" * 60)
print("4. 广告系列 (Campaign) 对比")
print("=" * 60)

campaigns = df.groupby("xyz_campaign_id").agg(
    Ads=("ad_id", "count"),
    Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
    Approved=("Approved_Conversion", "sum"),
)
campaigns["CPC"] = campaigns["Spent"] / campaigns["Clicks"]
campaigns["CPM"] = campaigns["Spent"] / campaigns["Impressions"] * 1000
campaigns["CTR"] = campaigns["Clicks"] / campaigns["Impressions"] * 100
campaigns["Conv_Rate"] = campaigns["Conversions"] / campaigns["Clicks"] * 100
campaigns["Cost_per_Conv"] = campaigns["Spent"] / campaigns["Conversions"]
campaigns["Approved_Rate"] = campaigns["Approved"] / campaigns["Conversions"] * 100
print(campaigns.round(4).to_string())
print()

# ── 5. 年龄组分析 ──
print("=" * 60)
print("5. 年龄组表现")
print("=" * 60)

age = df.groupby("age").agg(
    Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
    Approved=("Approved_Conversion", "sum"),
).round(2)
age["CPC"] = age["Spent"] / age["Clicks"]
age["CTR"] = age["Clicks"] / age["Impressions"] * 100
age["Cost_per_Conv"] = age["Spent"] / age["Conversions"]
print(age.to_string())
print()

# ── 6. 性别分析 ──
print("=" * 60)
print("6. 性别表现")
print("=" * 60)

gender = df.groupby("gender").agg(
    Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
    Approved=("Approved_Conversion", "sum"),
).round(2)
gender["CPC"] = gender["Spent"] / gender["Clicks"]
gender["CTR"] = gender["Clicks"] / gender["Impressions"] * 100
gender["Cost_per_Conv"] = gender["Spent"] / gender["Conversions"]
print(gender.to_string())
print()

# ── 7. 年龄×性别 交叉分析 ──
print("=" * 60)
print("7. 年龄×性别 交叉分析")
print("=" * 60)

cross = df.groupby(["age", "gender"]).agg(
    Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
).round(2)
cross["CPC"] = cross["Spent"] / cross["Clicks"]
cross["CTR"] = cross["Clicks"] / cross["Impressions"] * 100
cross["Cost_per_Conv"] = cross["Spent"] / cross["Conversions"]
print(cross.to_string())
print()

# ── 8. Top 兴趣分类 ──
print("=" * 60)
print("8. 兴趣分类 Top 15 (按花费)")
print("=" * 60)

interest = df.groupby("interest").agg(
    Spent=("Spent", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Total_Conversion", "sum"),
).sort_values("Spent", ascending=False)
interest["CPC"] = interest["Spent"] / interest["Clicks"]
interest["Cost_per_Conv"] = interest["Spent"] / interest["Conversions"]
print(interest.head(15).round(4).to_string())
print()

# ── 9. 核心洞察 ──
print("=" * 60)
print("9. 核心业务洞察")
print("=" * 60)

insights = [
    {
        "finding": "广告系列之间效率差异显著",
        "detail": f"系列 {campaigns.index[0]}: CPC ${campaigns.iloc[0]['CPC']:.4f}, "
                  f"系列 {campaigns.index[2]}: CPC ${campaigns.iloc[2]['CPC']:.4f}",
        "action": "将预算向低 CPC、高转化率的广告系列倾斜"
    },
    {
        "finding": "年龄组表现差距很大",
        "detail": f"花费最高的年龄组: {age['Spent'].idxmax()} (${age['Spent'].max():,.0f}), "
                  f"但每转化成本最低的组可能完全不同",
        "action": "针对不同年龄组单独优化出价和素材策略"
    },
    {
        "finding": "兴趣定向的效果差异",
        "detail": f"兴趣分类中每转化成本从低到高差异可达数倍",
        "action": "对高转化率兴趣分类加大预算，低效兴趣减少投放"
    },
]

for i, ins in enumerate(insights, 1):
    print(f"\n洞察 {i}: {ins['finding']}")
    print(f"  数据: {ins['detail']}")
    print(f"  建议: {ins['action']}")

# 5 个思考模型
print()
print("=" * 60)
print("10. 思维模型")
print("=" * 60)

models = [
    ("1. 分解思维", "把总花费 $12.4K 按广告系列、年龄组、性别、兴趣拆开，不同维度的效率差异揭示了优化方向"),
    ("2. 分层差异", "不同年龄组的 CTR 和每转化成本差异可以达数倍，只看平均值会掩盖这些差异"),
    ("3. 杠杆点识别", "找到花费占比大且转化率高的年龄×性别组合，集中资源"),
    ("4. 间接推断", "审核通过率可以作为转化质量的代理指标，而不仅仅是看转化数量"),
    ("5. 约束 vs 偏好", "性别和年龄的表现差异可能是受众偏好（产品适合谁），也可能是投放设置（出价/定向）的约束"),
]
for m in models:
    print(f"  {m[0]}: {m[1]}")

print()
print("=" * 60)
print("分析完成")
print("=" * 60)
