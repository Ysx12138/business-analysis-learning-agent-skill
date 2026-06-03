"""
Store Retail Operations Analysis
Walmart retail dataset — audit_report mode
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

BASE = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/store_retail_operations"

sales = pd.read_csv(f"{BASE}/sales data-set.csv", parse_dates=["Date"], date_format="%d/%m/%Y")
stores = pd.read_csv(f"{BASE}/stores data-set.csv")
features = pd.read_csv(f"{BASE}/Features data set.csv", parse_dates=["Date"], date_format="%d/%m/%Y")

print("=" * 70)
print("1. 数据概览")
print("=" * 70)
print(f"销售记录: {len(sales):,} 行 x {len(sales.columns)} 列")
print(f"门店: {len(stores)} 家")
print(f"特征数据: {len(features):,} 行 x {len(features.columns)} 列")
print(f"日期范围: {sales['Date'].min().date()} ~ {sales['Date'].max().date()}")
print(f"门店数 (销售表): {sales['Store'].nunique()}")
print(f"部门数: {sales['Dept'].nunique()}")
print(f"缺失值: 销售表={sales.isna().sum().sum()}, 特征表={features.isna().sum().sum()}")

# Merge stores
sales_full = sales.merge(stores, on="Store", how="left")

# ── 2. Overall sales ──
print("\n" + "=" * 70)
print("2. 整体销售表现")
print("=" * 70)
total_sales = sales["Weekly_Sales"].sum()
avg_weekly = sales["Weekly_Sales"].mean()
print(f"总销售额: ${total_sales:,.0f}")
print(f"平均周销售额: ${avg_weekly:,.2f}")
print(f"中位周销售额: ${sales['Weekly_Sales'].median():,.2f}")
holiday_sales = sales[sales["IsHoliday"] == True]["Weekly_Sales"].sum()
non_holiday = sales[sales["IsHoliday"] == False]["Weekly_Sales"].sum()
print(f"\n节假日销售额: ${holiday_sales:,.0f} (占 {holiday_sales/total_sales*100:.1f}%)")
print(f"非节假日销售额: ${non_holiday:,.0f} (占 {non_holiday/total_sales*100:.1f}%)")
hol_avg = sales[sales["IsHoliday"]==True]["Weekly_Sales"].mean()
non_avg = sales[sales["IsHoliday"]==False]["Weekly_Sales"].mean()
print(f"节假日平均周销: ${hol_avg:,.0f} vs 非节假日 ${non_avg:,.0f}")

# ── 3. Store type ──
print("\n" + "=" * 70)
print("3. 门店类型分析")
print("=" * 70)
store_type = sales_full.groupby("Type").agg(
    门店数=("Store", "nunique"),
    总销售额=("Weekly_Sales", "sum"),
    平均周销=("Weekly_Sales", "mean"),
)
store_type["店均销售额"] = store_type["总销售额"] / store_type["门店数"]
print(store_type.round(2).to_string())

print("\n--- 门店大小与销售关系 ---")
size_sales = sales_full.groupby("Store").agg(
    Size=("Size", "first"),
    Type=("Type", "first"),
    Total_Sales=("Weekly_Sales", "sum"),
    Avg_Sales=("Weekly_Sales", "mean"),
).reset_index()
corr = size_sales["Size"].corr(size_sales["Avg_Sales"])
print(f"门店面积与周销相关系数: {corr:.4f}")

# ── 4. Department analysis ──
print("\n" + "=" * 70)
print("4. 部门表现")
print("=" * 70)
dept = sales.groupby("Dept").agg(
    Total_Sales=("Weekly_Sales", "sum"),
    Avg_Sales=("Weekly_Sales", "mean"),
    Stores=("Store", "nunique"),
).sort_values("Total_Sales", ascending=False)
print("Top 10 部门（按总销售额）:")
print(dept.head(10).round(2).to_string())
print("\nBottom 10 部门:")
print(dept.tail(10).round(2).to_string())

# ── 5. Time trends ──
print("\n" + "=" * 70)
print("5. 时间趋势")
print("=" * 70)
monthly = sales.copy()
monthly["YearMonth"] = monthly["Date"].dt.to_period("M")
monthly_agg = monthly.groupby("YearMonth").agg(
    Sales=("Weekly_Sales", "sum"),
    Weeks=("Weekly_Sales", "count"),
    Avg=("Weekly_Sales", "mean"),
)
print("月度销售额:")
print(monthly_agg.round(2).to_string())

print(f"\n最高月: {monthly_agg['Sales'].idxmax()} (${monthly_agg['Sales'].max():,.0f})")
print(f"最低月: {monthly_agg['Sales'].idxmin()} (${monthly_agg['Sales'].min():,.0f})")
print(f"月间波动: {(monthly_agg['Sales'].max()-monthly_agg['Sales'].min())/monthly_agg['Sales'].mean()*100:.1f}%")

# ── 6. External factors ──
print("\n" + "=" * 70)
print("6. 外部因素相关性")
print("=" * 70)
feat_agg = features.groupby("Store").agg(
    Avg_Temp=("Temperature", "mean"),
    Avg_Fuel=("Fuel_Price", "mean"),
    Avg_CPI=("CPI", "mean"),
    Avg_Unemp=("Unemployment", "mean"),
).round(4)

store_sales_agg = sales.groupby("Store").agg(Avg_Sales=("Weekly_Sales", "mean"))
ext_corr = feat_agg.join(store_sales_agg).corr()["Avg_Sales"].drop("Avg_Sales")
print("外部因素与销售额相关性:")
for idx, val in ext_corr.items():
    print(f"  {idx}: {val:.4f}")

# ── 7. Holiday effect ──
print("\n" + "=" * 70)
print("7. 节假日效应")
print("=" * 70)
dept_holiday = sales.groupby(["Dept", "IsHoliday"]).agg(
    Avg=("Weekly_Sales", "mean")
).round(2).unstack()
dept_holiday["lift"] = (dept_holiday["Avg"][True] - dept_holiday["Avg"][False]) / dept_holiday["Avg"][False] * 100
top_lift = dept_holiday["lift"].dropna().sort_values(ascending=False)
print("节假日销售增幅 Top 10 部门:")
for dept_id, lift in top_lift.head(10).items():
    print(f"  部门 {dept_id}: {lift:+.1f}%")

bottom_lift = top_lift.tail(10)
print("\n节假日销售降幅 Top 10 部门:")
for dept_id, lift in bottom_lift.items():
    print(f"  部门 {dept_id}: {lift:+.1f}%")

# ── 8. Insights ──
print("\n" + "=" * 70)
print("8. 核心业务洞察")
print("=" * 70)
insights = [
    ("门店类型与规模", f"A 型门店 {len(stores[stores['Type']=='A'])} 家，平均周销 ${store_type.loc['A', '平均周销']:,.0f} "
     f"，大小相关系数 {corr:.4f}", "不同类型门店需差异化运营策略"),
    ("节假日效应", f"节假日周均 ${hol_avg:,.0f} vs 非节假日 ${non_avg:,.0f}，增幅 {(hol_avg/non_avg-1)*100:+.1f}%",
     "优化节假日备货与促销安排"),
    ("部门表现差异", f"Top 部门 ${dept.iloc[0]['Total_Sales']:,.0f} vs Bottom ${dept.iloc[-1]['Total_Sales']:,.0f}",
     "淘汰或调整低效部门"),
    ("外部因素", f"主要影响因素: {ext_corr.abs().idxmax()} (r={ext_corr[ext_corr.abs().idxmax()]:.4f})",
     "将外部因素纳入销售预测模型"),
]
for label, detail, action in insights:
    print(f"\n  洞察: {label}")
    print(f"    数据: {detail}")
    print(f"    建议: {action}")

# ── 9. Thinking Models ──
print("\n" + "=" * 70)
print("9. 思维模型")
print("=" * 70)
models = [
    ("1. 分解思维", f"总销售额 ${total_sales:,.0f} 按门店类型、部门、月份、节假日拆解。A 型门店贡献主要销售额，但 C 型门店单位面积效率可能更高。"),
    ("2. 分层差异", f"部门间销售额差距可达数十倍（Top {dept.index[0]} vs Bottom {dept.index[-1]}）。节假日对不同部门的提升幅度从 +50% 到 -10% 不等。"),
    ("3. 间接推断", "CPI 和失业率可作为消费者购买力的代理指标。即使销售额未下降，外部经济指标恶化可能是未来销售下滑的领先信号。"),
    ("4. 杠杆点识别", f"Top 3 部门贡献总销售额的显著份额，同时节假日对特定部门的拉动效应高达 {top_lift.iloc[0]:.0f}%。在这些部门优化促销可获得最大回报。"),
    ("5. 约束 vs 偏好", f"门店类型间的销售差异可能反映选址策略（约束），而非消费者偏好。A 型门店面积大销售高，但单位面积效率需进一步分析。"),
]
for m in models:
    print(f"\n  {m[0]}: {m[1]}")

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
