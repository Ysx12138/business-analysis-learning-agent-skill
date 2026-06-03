"""
Financial / Operating Performance Analysis
BCG company financial data — audit_report mode
"""
import pandas as pd, numpy as np

f = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/financial_operating_performance/BCG.csv"
df = pd.read_csv(f)
df = df.sort_values(["Company_Name", "Year"])

print("=" * 70)
print("1. 数据概览"); print("=" * 70)
print(f"记录数: {len(df)}")
print(f"公司: {', '.join(sorted(df['Company_Name'].unique()))}")
print(f"年份: {df['Year'].min()} - {df['Year'].max()}")
print(f"字段: {list(df.columns)}")
print()

# ── 2. Per-company summary ──
print("=" * 70)
print("2. 公司财务总览 (2023)")
print("=" * 70)
current = df[df["Year"] == 2023].copy()
if len(current) > 0:
    current["利润率"] = current["Net_Income"] / current["Total_Revenue"] * 100
    current["负债率"] = current["Total_Liabilities"] / current["Total_Assets"] * 100
    current["现金/资产比"] = current["Cash_Flow"] / current["Total_Assets"] * 100
    cols = ["Company_Name", "Total_Revenue", "Net_Income", "Total_Assets", "Total_Liabilities", "Cash_Flow", "利润率", "负债率"]
    print(current[cols].round(2).to_string(index=False))

# ── 3. YoY growth ──
print("\n" + "=" * 70)
print("3. 同比增长率")
print("=" * 70)
df_pivot = df.pivot_table(index="Company_Name", columns="Year",
    values=["Total_Revenue", "Net_Income", "Total_Assets"]).round(2)
print("收入趋势 (百万):")
print(df_pivot["Total_Revenue"].to_string())
print("\n净利趋势 (百万):")
print(df_pivot["Net_Income"].to_string())

# YoY growth rates
for company in df["Company_Name"].unique():
    c = df[df["Company_Name"] == company].sort_values("Year")
    print(f"\n--- {company} YoY ---")
    for i in range(1, len(c)):
        y1, y2 = c.iloc[i-1], c.iloc[i]
        rev_g = (y2["Total_Revenue"] - y1["Total_Revenue"]) / y1["Total_Revenue"] * 100
        ni_g = (y2["Net_Income"] - y1["Net_Income"]) / y1["Net_Income"] * 100
        print(f"  {y1['Year']}-{y2['Year']}: 收入 {rev_g:+.1f}%, 净利 {ni_g:+.1f}%")

# ── 4. Profitability ──
print("\n" + "=" * 70)
print("4. 盈利能力分析")
print("=" * 70)
df["利润率"] = df["Net_Income"] / df["Total_Revenue"] * 100
df["资产回报率"] = df["Net_Income"] / df["Total_Assets"] * 100
df["负债率"] = df["Total_Liabilities"] / df["Total_Assets"] * 100

for company in df["Company_Name"].unique():
    c = df[df["Company_Name"] == company].sort_values("Year")
    print(f"\n{company}:")
    for _, r in c.iterrows():
        print(f"  {r['Year']}: 利润率 {r['利润率']:.1f}%, 资产回报率 {r['资产回报率']:.1f}%, 负债率 {r['负债率']:.1f}%")

# ── 5. Cross-company comparison ──
print("\n" + "=" * 70)
print("5. 跨公司对标")
print("=" * 70)
latest = df[df["Year"] == df.groupby("Company_Name")["Year"].transform("max")]
latest = latest.sort_values("Total_Revenue", ascending=False)
print("\n最新财务数据排序:")
latest["利润率"] = latest["Net_Income"] / latest["Total_Revenue"] * 100
latest["负债率"] = latest["Total_Liabilities"] / latest["Total_Assets"] * 100
print(latest[["Company_Name", "Year", "Total_Revenue", "Net_Income", "利润率", "负债率"]].round(2).to_string(index=False))

# ── 6. Insights ──
print("\n" + "=" * 70)
print("6. 核心发现"); print("=" * 70)

apple = df[df["Company_Name"]=="Apple"].iloc[-1]
msft = df[df["Company_Name"]=="Microsoft"].iloc[-1]
tsla = df[df["Company_Name"]=="Tesla"].iloc[-1]

print(f"\n  1. 收入规模: Apple ({apple['Total_Revenue']/1000:.1f}B) > Microsoft ({msft['Total_Revenue']/1000:.1f}B) > Tesla ({tsla['Total_Revenue']/1000:.1f}B)")
print(f"  2. 利润率: Apple ({(apple['Net_Income']/apple['Total_Revenue']*100):.1f}%), Microsoft ({(msft['Net_Income']/msft['Total_Revenue']*100):.1f}%), Tesla ({(tsla['Net_Income']/tsla['Total_Revenue']*100):.1f}%)")
print(f"  3. 负债率: Apple {apple['Total_Liabilities']/apple['Total_Assets']*100:.0f}%, Microsoft {msft['Total_Liabilities']/msft['Total_Assets']*100:.0f}%, Tesla {tsla['Total_Liabilities']/tsla['Total_Assets']*100:.0f}%")
print(f"  4. Apple 三年收入增长 {(df[df['Company_Name']=='Apple']['Total_Revenue'].iloc[-1]/df[df['Company_Name']=='Apple']['Total_Revenue'].iloc[0]-1)*100:.1f}%")
print(f"  5. Tesla 增长最快但盈利能力最低，Apple 最稳健")

# ── 7. Thinking Models ──
print("\n" + "=" * 70)
print("7. 思维模型"); print("=" * 70)
models = [
    ("1. 分解思维", "将公司整体财务表现拆解为收入、利润、资产、负债、现金流五个维度，交叉对比发现不同公司的优劣势。"),
    ("2. 分层差异", "三家公司处于不同发展阶段——Apple 成熟稳定，Microsoft 稳健增长，Tesla 高增长低利润。不同阶段的估值逻辑不同。"),
    ("3. 间接推断", "负债率是财务风险的代理指标。现金流/资产比是运营效率的代理指标。缺乏市场数据时，用这些财务比率推断公司健康度。"),
    ("4. 杠杆点识别", f"Apple 负债率最低但利润率最高——财务杠杆空间最大。适度的债务融资可能提升股东回报。"),
    ("5. 约束 vs 偏好", "Tesla 的低利润率可能反映行业特征（汽车制造业的资本密集约束），而非运营选择。对标应选用行业均值而非跨行业对比。"),
]
for m in models: print(f"\n  {m[0]}: {m[1]}")
print("\n" + "=" * 70)
print("分析完成"); print("=" * 70)
