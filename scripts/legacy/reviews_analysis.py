"""
Product Reviews Analysis
Amazon Products dataset — audit_report mode
"""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings("ignore")

f = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/product_reviews_ratings/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
df = pd.read_csv(f)
df["reviews.date"] = pd.to_datetime(df["reviews.date"], errors="coerce")
df["review_len"] = df["reviews.text"].fillna("").str.len()

print("=" * 70)
print("1. 数据概览"); print("=" * 70)
print(f"评论数: {len(df):,}")
print(f"品牌: {df['brand'].nunique()} ({df['brand'].unique()[0]})")
print(f"品类: {df['categories'].nunique()}")
print(f"平均评分: {df['reviews.rating'].mean():.2f}")
print(f"推荐率: {df['reviews.doRecommend'].mean()*100:.1f}%")
print(f"日期范围: {df['reviews.date'].min().date()} ~ {df['reviews.date'].max().date()}")

print("\n" + "=" * 70)
print("2. 评分分布"); print("=" * 70)
rd = df["reviews.rating"].value_counts().sort_index()
for r, c in rd.items(): print(f"  {r} 星: {c} ({c/len(df)*100:.1f}%)")

print("\n" + "=" * 70)
print("3. 品类分析"); print("=" * 70)
cats = df.groupby("categories").agg(
    评论数=("reviews.rating", "count"),
    平均评分=("reviews.rating", "mean"),
    推荐数=("reviews.doRecommend", "sum"),
    平均有帮助数=("reviews.numHelpful", "mean"),
).sort_values("评论数", ascending=False)
print("Top 10 品类:")
print(cats.head(10).round(2).to_string())

# Rating by category
print("\n品类 1 星率 Top 5:")
one_star = df[df["reviews.rating"] == 1].groupby("categories").size()
total_by_cat = df.groupby("categories").size()
one_star_rate = (one_star / total_by_cat * 100).dropna().sort_values(ascending=False)
for c, r in one_star_rate.head(5).items():
    print(f"  {c[:50]}: {r:.1f}%")

print("\n" + "=" * 70)
print("4. 评论长度分析"); print("=" * 70)
len_by_rating = df.groupby("reviews.rating")["review_len"].agg(["mean", "median", "count"])
print("各评分平均评论长度:")
print(len_by_rating.round(1).to_string())

print("\n" + "=" * 70)
print("5. 有帮助性分析"); print("=" * 70)
hp = df[df["reviews.numHelpful"].notna()]
print(f"有帮助标记数: {len(hp)} ({len(hp)/len(df)*100:.1f}%)")
print(f"平均有帮助数: {hp['reviews.numHelpful'].mean():.2f}")
print(f"中位数: {hp['reviews.numHelpful'].median():.0f}")

# Helpful by rating
print("\n各评分平均有帮助数:")
print(df.groupby("reviews.rating")["reviews.numHelpful"].mean().round(2).to_string())

print("\n" + "=" * 70)
print("6. 时间趋势"); print("=" * 70)
yearly = df.groupby(df["reviews.date"].dt.year).agg(
    评论数=("reviews.rating", "count"),
    平均评分=("reviews.rating", "mean"),
)
print("年度趋势:")
print(yearly.round(3).to_string())

print("\n" + "=" * 70)
print("7. 核心洞察"); print("=" * 70)
print(f"\n  洞察 1: 评分高度集中 — 5 星占 {rd[5]/len(df)*100:.1f}%，平均 {df['reviews.rating'].mean():.2f} 星")
print(f"    数据: 1 星仅 {rd.get(1,0)} 条 ({rd.get(1,0)/len(df)*100:.1f}%)")
print(f"    建议: 聚焦分析低评分评论，提取产品改进方向")
print(f"\n  洞察 2: 品类间质量差异 — 部分品类 1 星率显著偏高")
print(f"    数据: 最高 1 星率品类 {one_star_rate.index[0][:40]} ({one_star_rate.iloc[0]:.1f}%)")
print(f"    建议: 对高差评率品类进行专项质量改进")
print(f"\n  洞察 3: 推荐率 {df['reviews.doRecommend'].mean()*100:.1f}% — 极少数用户不推荐")
print(f"    数据: {df['reviews.doRecommend'].sum()} 推荐 / {(~df['reviews.doRecommend']).sum()} 不推荐")
print(f"    建议: 分析不推荐评论的文本内容，提取共性问题")

print("\n" + "=" * 70)
print("8. 思维模型"); print("=" * 70)
models = [
    ("1. 分解思维", f"平均 {df['reviews.rating'].mean():.1f} 星评分按品类、年份、推荐状态拆解，发现部分品类 1 星率明显高于平均，整体高均值掩盖了细分差异。"),
    ("2. 分层差异", f"品类间平均评分范围从 {cats['平均评分'].min():.2f} 到 {cats['平均评分'].max():.2f}。评论长度与评分的关系也呈现非线性模式。"),
    ("3. 间接推断", "评论长度和帮助数可作为评论质量的代理指标。长评论+高帮助数 = 高影响评论，值得优先分析。"),
    ("4. 杠杆点识别", f"低评分评论（1-2 星）虽然仅 {rd.get(1,0)+rd.get(2,0)} 条，但其中提取的产品问题影响所有潜在购买者的决策。"),
    ("5. 约束 vs 偏好", '用户给出低评分是偏好(产品不满足期望)。但不推荐则更接近约束(用户认为其他人也不应购买)。两者分析重点不同。'),
]
for m in models: print(f"\n  {m[0]}: {m[1]}")
print("\n" + "=" * 70)
print("分析完成"); print("=" * 70)
