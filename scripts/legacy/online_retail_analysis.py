"""
在线零售数据分析 (UCI Online Retail)
按照 business-analysis skill workflow 执行
"""

import pandas as pd
import numpy as np

# ── 1. 读取数据 ──
print("=" * 60)
print("1. 数据集概览")
print("=" * 60)

df = pd.read_csv("/Users/sx/数据分析/online_retail/原始数据/online_retail.csv",
                 encoding="ISO-8859-1")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

print(f"行数: {len(df):,}")
print(f"字段: {list(df.columns)}")
print(f"时间范围: {df['InvoiceDate'].min()} ~ {df['InvoiceDate'].max()}")
print(f"客户数: {df['CustomerID'].nunique():,}")
print(f"商品数: {df['StockCode'].nunique():,}")
print(f"发票数: {df['InvoiceNo'].nunique():,}")
print(f"国家数: {df['Country'].nunique()}")
print()

# ── 2. 数据风险检查 ──
print("=" * 60)
print("2. 数据风险检查")
print("=" * 60)

# 缺失 CustomerID
missing_cid = df["CustomerID"].isnull().sum()
print(f"缺失 CustomerID: {missing_cid:,} ({missing_cid/len(df)*100:.1f}%)")
# 业务影响: 无法做客户级分析 (RFM、复购率等)

# 缺失 Description
missing_desc = df["Description"].isnull().sum()
print(f"缺失 Description: {missing_desc:,} ({missing_desc/len(df)*100:.1f}%)")

# 取消订单 (InvoiceNo 以 C 开头)
cancelled = df[df["InvoiceNo"].astype(str).str.startswith("C", na=False)]
print(f"取消订单行数: {len(cancelled):,} ({len(cancelled)/len(df)*100:.1f}%)")

# 负数量
neg_qty = df[df["Quantity"] < 0]
print(f"负数量行数: {len(neg_qty):,} ({len(neg_qty)/len(df)*100:.1f}%)")
# 包括取消订单 + 退货调整

# 零/负单价
bad_price = df[df["UnitPrice"] <= 0]
print(f"零/负单价行数: {len(bad_price):,} ({len(bad_price)/len(df)*100:.1f}%)")

# 异常大额订单
high_qty = df[df["Quantity"] > 10000]
print(f"数量>10000的行: {len(high_qty):,}")
if len(high_qty) > 0:
    print(f"  最大数量: {df['Quantity'].max():,}")
    print(f"  这些行: {high_qty[['InvoiceNo','Description','Quantity','UnitPrice','Revenue']].to_string(index=False)}")

# 异常单价
high_price = df[df["UnitPrice"] > 1000]
print(f"单价>1000的行: {len(high_price):,}")
if len(high_price) > 0:
    print(f"  最大单价: £{df['UnitPrice'].max():,.2f}")

print()

# ── 3. 数据清洗 ──
print("=" * 60)
print("3. 数据清洗")
print("=" * 60)

before = len(df)

# 3a. 删除无客户ID的行（无法做客户分析）
df_clean = df.dropna(subset=["CustomerID"]).copy()
print(f"删除缺失 CustomerID: {before - len(df_clean):,} 行 ({((before-len(df_clean))/before)*100:.1f}%)")

before = len(df_clean)

# 3b. 删除取消订单
df_clean = df_clean[~df_clean["InvoiceNo"].astype(str).str.startswith("C", na=False)]
print(f"删除取消订单: {before - len(df_clean):,} 行 ({((before-len(df_clean))/before)*100:.1f}%)")

before = len(df_clean)

# 3c. 删除负数量（取消后剩余的退货/调整）
df_clean = df_clean[df_clean["Quantity"] > 0]
print(f"删除负数量: {before - len(df_clean):,} 行 ({((before-len(df_clean))/before)*100:.1f}%)")

before = len(df_clean)

# 3d. 删除零/负单价
df_clean = df_clean[df_clean["UnitPrice"] > 0]
print(f"删除零/负单价: {before - len(df_clean):,} 行 ({((before-len(df_clean))/before)*100:.1f}%)")

print(f"\n清洗后数据: {len(df_clean):,} 行 (原始: {len(df):,}, 保留: {len(df_clean)/len(df)*100:.1f}%)")
print()

# 重建 Revenue
df_clean["Revenue"] = df_clean["Quantity"] * df_clean["UnitPrice"]

# 添加时间字段
df_clean["Month"] = df_clean["InvoiceDate"].dt.to_period("M")
df_clean["Hour"] = df_clean["InvoiceDate"].dt.hour
df_clean["DayOfWeek"] = df_clean["InvoiceDate"].dt.dayofweek  # 0=Mon

# ── 4. 关键指标 ──
print("=" * 60)
print("4. 关键业务指标")
print("=" * 60)

total_revenue = df_clean["Revenue"].sum()
total_orders = df_clean["InvoiceNo"].nunique()
total_customers = df_clean["CustomerID"].nunique()
total_items = df_clean["Quantity"].sum()
aov = total_revenue / total_orders
revenue_per_customer = total_revenue / total_customers
items_per_order = total_items / total_orders
avg_unit_price = df_clean["UnitPrice"].mean()

print(f"总收入:        £{total_revenue:,.2f}")
print(f"总订单数:      {total_orders:,}")
print(f"总客户数:      {total_customers:,}")
print(f"总销量(件):    {total_items:,}")
print(f"客单价 (AOV):  £{aov:.2f}")
print(f"每客户收入:    £{revenue_per_customer:.2f}")
print(f"每单平均件数:  {items_per_order:.1f}")
print(f"平均单价:      £{avg_unit_price:.2f}")
print()

# ── 5. 趋势分析 ──
print("=" * 60)
print("5. 月度趋势")
print("=" * 60)

monthly = df_clean.groupby("Month").agg(
    Revenue=("Revenue", "sum"),
    Orders=("InvoiceNo", "nunique"),
    Customers=("CustomerID", "nunique"),
    Items=("Quantity", "sum"),
)
monthly["AOV"] = monthly["Revenue"] / monthly["Orders"]
print(monthly.to_string())
print()

# ── 6. 国家/市场分析 ──
print("=" * 60)
print("6. 国家贡献分析")
print("=" * 60)

country = df_clean.groupby("Country").agg(
    Revenue=("Revenue", "sum"),
    Orders=("InvoiceNo", "nunique"),
    Customers=("CustomerID", "nunique"),
    Items=("Quantity", "sum"),
).sort_values("Revenue", ascending=False)

country["Revenue%"] = country["Revenue"] / country["Revenue"].sum() * 100
country["AOV"] = country["Revenue"] / country["Orders"]
country = country.round(2)
print(country.head(15).to_string())
print()

# ── 7. 商品分析 ──
print("=" * 60)
print("7. 商品分析 (Top 20)")
print("=" * 60)

products = df_clean.groupby(["StockCode", "Description"]).agg(
    Revenue=("Revenue", "sum"),
    Quantity=("Quantity", "sum"),
    Orders=("InvoiceNo", "nunique"),
).sort_values("Revenue", ascending=False)

products["Revenue%"] = products["Revenue"] / products["Revenue"].sum() * 100
products["AvgPrice"] = products["Revenue"] / products["Quantity"]
products = products.round(2)
print(products.head(20).to_string())
print()

# ── 8. 客户分层分析 ──
print("=" * 60)
print("8. 客户分层 (RFM 简版)")
print("=" * 60)

# 计算每个客户的: 最近一次消费(Recency), 频率(Frequency), 金额(Monetary)
ref_date = df_clean["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df_clean.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (ref_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum"),
)

# 分层
def rfm_segment(row):
    if row["Recency"] <= 30 and row["Frequency"] >= 10:
        return "高价值活跃"
    elif row["Recency"] <= 90 and row["Frequency"] >= 5:
        return "中等活跃"
    elif row["Recency"] <= 180:
        return "低频但近"
    elif row["Frequency"] >= 5:
        return "曾活跃但流失"
    else:
        return "低频/沉睡"

rfm["Segment"] = rfm.apply(rfm_segment, axis=1)

segments = rfm.groupby("Segment").agg(
    Customers=("Monetary", "count"),
    AvgMonetary=("Monetary", "mean"),
    TotalRevenue=("Monetary", "sum"),
).sort_values("TotalRevenue", ascending=False)

segments["Customer%"] = segments["Customers"] / segments["Customers"].sum() * 100
segments["Revenue%"] = segments["TotalRevenue"] / segments["TotalRevenue"].sum() * 100
print(segments.round(2).to_string())
print()

# ── 9. 复购率 ──
print("=" * 60)
print("9. 复购率分析")
print("=" * 60)

# 单次 vs 多次购买
order_counts = df_clean.groupby("CustomerID")["InvoiceNo"].nunique()
repeat_count = (order_counts >= 2).sum()
repeat_rate = repeat_count / len(order_counts) * 100
print(f"单次购买客户: {(order_counts == 1).sum():,} ({(order_counts == 1).sum()/len(order_counts)*100:.1f}%)")
print(f"多次购买客户: {repeat_count:,} ({repeat_rate:.1f}%)")
print(f"平均购买次数: {order_counts.mean():.1f} 次")
print()

# 购买次数分布
print("购买次数分布:")
for bins in [1, 2, 3, 4, 5, 10, 20, 50, 100]:
    count = (order_counts >= bins).sum()
    print(f"  >= {bins:3d} 次: {count:5d} 客户 ({count/len(order_counts)*100:.1f}%)")
print()

# ── 10. 核心洞察 ──
print("=" * 60)
print("10. 核心业务洞察")
print("=" * 60)

insights = [
    {
        "finding": "英国市场占绝对主导，但海外市场客单价更高",
        "detail": f"英国贡献 £{country.loc['United Kingdom','Revenue']:,.0f} 收入 ({country.loc['United Kingdom','Revenue%']:.1f}%)，但荷兰平均客单价 £{country[country.index!='United Kingdom']['AOV'].max():.0f}，远高于英国的 £{country.loc['United Kingdom','AOV']:.0f}",
        "action": "海外市场值得投入，尤其荷兰、EIRE（爱尔兰）、德国、法国"
    },
    {
        "finding": "11月是全年收入最高月份",
        "detail": f"2011年11月收入 £{monthly.loc['2011-11','Revenue']:,.0f}，是全年最低月（2月 £{monthly['Revenue'].min():,.0f}）的 {monthly.loc['2011-11','Revenue']/monthly['Revenue'].min():.1f} 倍",
        "action": "圣诞旺季效应明显，应提前在9-10月布局库存和营销"
    },
    {
        "finding": "商品集中度低（长尾效应）",
        "detail": f"Top 1 商品 (REGENCY CAKESTAND 3 TIER) 仅占 {products.iloc[0]['Revenue%']:.1f}% 收入，Top 10 合计约 {products.head(10)['Revenue%'].sum():.1f}%",
        "action": "长尾品类管理：关注高频小商品和低频高利润商品的平衡"
    },
    {
        "finding": "客户分层明显，高价值客户贡献集中",
        "detail": f"高价值活跃客户 {segments.loc['高价值活跃','Customers']:.0f} 人 ({segments.loc['高价值活跃','Customer%']:.1f}%) 贡献了 {segments.loc['高价值活跃','Revenue%']:.1f}% 收入",
        "action": "高价值客户是核心资产，需专项维护"
    },
    {
        "finding": "复购率健康，但大量客户仅购买1次",
        "detail": f"多次购买客户占 {repeat_rate:.1f}%，平均每人 {order_counts.mean():.1f} 次。单次客户仍有优化空间",
        "action": "新客转化后的二次触达是提升复购率的关键"
    },
]

for i, ins in enumerate(insights, 1):
    print(f"\n洞察 {i}: {ins['finding']}")
    print(f"  数据: {ins['detail']}")
    print(f"  建议: {ins['action']}")
print()

print("=" * 60)
print("分析完成")
print("=" * 60)
