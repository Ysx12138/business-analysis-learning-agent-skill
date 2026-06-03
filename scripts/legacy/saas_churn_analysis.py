"""
SaaS Subscription & Churn Analysis
Multi-table dataset — audit_report mode with relational joins
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

BASE = "/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/work/kaggle_datasets/downloads/saas_subscription_churn"

# ── 1. Load all tables ──
accounts = pd.read_csv(f"{BASE}/ravenstack_accounts.csv")
churn_events = pd.read_csv(f"{BASE}/ravenstack_churn_events.csv")
subscriptions = pd.read_csv(f"{BASE}/ravenstack_subscriptions.csv")
feature_usage = pd.read_csv(f"{BASE}/ravenstack_feature_usage.csv")
support_tickets = pd.read_csv(f"{BASE}/ravenstack_support_tickets.csv")

print("=" * 70)
print("1. 数据概览 (5 张表)")
print("=" * 70)
tables = [
    ("accounts", accounts, "客户档案"),
    ("subscriptions", subscriptions, "订阅记录"),
    ("churn_events", churn_events, "流失事件"),
    ("feature_usage", feature_usage, "功能使用日志"),
    ("support_tickets", support_tickets, "支持工单"),
]
for name, df, desc in tables:
    print(f"\n{name} ({desc}): {len(df):,} 行 x {len(df.columns)} 列")
    print(f"  字段: {list(df.columns)}")
    print(f"  缺失: {df.isna().sum().sum()}")

# ── 2. Account-level churn analysis ──
print("\n" + "=" * 70)
print("2. 整体流失率与客户画像")
print("=" * 70)

total_accounts = len(accounts)
churned = accounts["churn_flag"].sum()
churn_rate = churned / total_accounts * 100
print(f"总客户数: {total_accounts}")
print(f"流失客户: {churned:,} ({churn_rate:.1f}%)")
print(f"留存客户: {total_accounts - churned:,} ({(1-churn_rate/100)*100:.1f}%)")

# Plan tier distribution
print("\n--- 按套餐层级分布 ---")
plan_dist = accounts.groupby("plan_tier").agg(
    客户数=("account_id", "count"),
    流失数=("churn_flag", "sum"),
)
plan_dist["流失率"] = plan_dist["流失数"] / plan_dist["客户数"] * 100
print(plan_dist.to_string())

# Industry
print("\n--- 按行业分布 ---")
ind_dist = accounts.groupby("industry").agg(
    客户数=("account_id", "count"),
    流失数=("churn_flag", "sum"),
)
ind_dist["流失率"] = ind_dist["流失数"] / ind_dist["客户数"] * 100
ind_dist = ind_dist.sort_values("客户数", ascending=False)
print(ind_dist.to_string())

# Country
print("\n--- 按国家分布 (Top 10) ---")
ctry_dist = accounts.groupby("country").agg(
    客户数=("account_id", "count"),
    流失数=("churn_flag", "sum"),
)
ctry_dist["流失率"] = ctry_dist["流失数"] / ctry_dist["客户数"] * 100
ctry_dist = ctry_dist.sort_values("客户数", ascending=False)
print(ctry_dist.head(10).to_string())

# Referral source
print("\n--- 按来源渠道 ---")
ref_dist = accounts.groupby("referral_source").agg(
    客户数=("account_id", "count"),
    流失数=("churn_flag", "sum"),
)
ref_dist["流失率"] = ref_dist["流失数"] / ref_dist["客户数"] * 100
print(ref_dist.to_string())

# Trial vs non-trial
print("\n--- 试用 vs 非试用 ---")
trial_dist = accounts.groupby("is_trial").agg(
    客户数=("account_id", "count"),
    流失数=("churn_flag", "sum"),
)
trial_dist["流失率"] = trial_dist["流失数"] / trial_dist["客户数"] * 100
print(trial_dist.to_string())

# ── 3. Revenue analysis ──
print("\n" + "=" * 70)
print("3. 收入分析")
print("=" * 70)

total_arr = subscriptions["arr_amount"].sum()
total_mrr = subscriptions["mrr_amount"].sum()
print(f"总 ARR: ${total_arr:,.0f}")
print(f"总 MRR (订阅期内): ${total_mrr:,.0f}")
print(f"平均 MRR/订阅: ${subscriptions['mrr_amount'].mean():.2f}")
print(f"中位数 MRR: ${subscriptions['mrr_amount'].median():.2f}")

# Churned revenue
churned_accounts = accounts[accounts["churn_flag"] == True]["account_id"]
churned_subs = subscriptions[subscriptions["account_id"].isin(churned_accounts)]
churned_arr = churned_subs["arr_amount"].sum()
print(f"\n流失客户的总 ARR: ${churned_arr:,.0f}")
print(f"流失 ARR 占比: {churned_arr/total_arr*100:.1f}%")

# Revenue by plan
print("\n--- 按套餐收入 ---")
plan_rev = subscriptions.groupby("plan_tier").agg(
    订阅数=("subscription_id", "count"),
    MRR=("mrr_amount", "sum"),
    ARR=("arr_amount", "sum"),
).round(2)
print(plan_rev.to_string())

# ── 4. Churn reasons & patterns ──
print("\n" + "=" * 70)
print("4. 流失原因分析")
print("=" * 70)

if len(churn_events) > 0:
    print("\n--- 流失原因分布 ---")
    reason_dist = churn_events["reason_code"].value_counts()
    for code, cnt in reason_dist.items():
        pct = cnt / len(churn_events) * 100
        print(f"  {code}: {cnt} ({pct:.1f}%)")

    print(f"\n平均退款金额: ${churn_events['refund_amount_usd'].mean():.2f}")
    print(f"有退款的流失事件: {churn_events['refund_amount_usd'].gt(0).sum()} / {len(churn_events)}")

    print("\n--- 流失前行为 ---")
    pre_upgrade = churn_events["preceding_upgrade_flag"].mean() * 100
    pre_downgrade = churn_events["preceding_downgrade_flag"].mean() * 100
    print(f"流失前升级: {pre_upgrade:.1f}%")
    print(f"流失前降级: {pre_downgrade:.1f}%")
    print(f"重新激活: {churn_events['is_reactivation'].sum()} ({churn_events['is_reactivation'].mean()*100:.1f}%)")

# ── 5. Feature usage comparison ──
print("\n" + "=" * 70)
print("5. 功能使用对比 (流失 vs 留存)")
print("=" * 70)

# Merge accounts into subscriptions for churn flag
# Merge chain: feature_usage → subscriptions → accounts
usage_with_subs = feature_usage.merge(
    subscriptions[["subscription_id", "account_id"]], on="subscription_id", how="left"
)
usage_with_churn = usage_with_subs.merge(
    accounts[["account_id", "churn_flag"]], on="account_id", how="left"
)

# Aggregate per account
usage_agg = usage_with_churn.groupby(["account_id", "churn_flag"]).agg(
    total_usage=("usage_count", "sum"),
    avg_duration=("usage_duration_secs", "mean"),
    total_errors=("error_count", "sum"),
    unique_features=("feature_name", "nunique"),
    usage_days=("usage_date", "nunique"),
).reset_index()

print("\n--- 使用行为均值对比 ---")
comp = usage_agg.groupby("churn_flag")[["total_usage", "avg_duration", "total_errors", "unique_features", "usage_days"]].mean()
comp.index = ["留存", "流失"]
print(comp.round(2).to_string())

# Top features by churn rate
print("\n--- 各功能流失率 ---")
feat_churn = usage_with_churn.groupby("feature_name").agg(
    usage_count=("usage_count", "sum"),
    churned_count=("churn_flag", "sum"),
)
feat_churn["total_records"] = usage_with_churn.groupby("feature_name").size()
feat_churn["churn_rate"] = feat_churn["churned_count"] / feat_churn["total_records"] * 100
feat_churn = feat_churn.sort_values("churn_rate", ascending=False)
print("功能流失率 (Top 10 最高):")
print(feat_churn.head(10).round(2).to_string())

# Beta feature impact
print("\n--- Beta 功能使用与流失 ---")
beta_usage = usage_with_churn.groupby("is_beta_feature").agg(
    records=("usage_count", "count"),
    churn_rate=("churn_flag", "mean"),
)
beta_usage.index = ["正式功能", "Beta 功能"]
beta_usage["churn_rate"] = beta_usage["churn_rate"] * 100
print(beta_usage.round(2).to_string())

# ── 6. Support ticket patterns ──
print("\n" + "=" * 70)
print("6. 支持工单分析")
print("=" * 70)

tickets_with_churn = support_tickets.merge(
    accounts[["account_id", "churn_flag"]], on="account_id", how="left"
)

# Tickets per account
ticket_agg = tickets_with_churn.groupby("account_id").agg(
    ticket_count=("ticket_id", "count"),
    avg_resolution=("resolution_time_hours", "mean"),
    avg_response=("first_response_time_minutes", "mean"),
    avg_satisfaction=("satisfaction_score", "mean"),
    escalation_rate=("escalation_flag", "mean"),
).reset_index()

ticket_agg = ticket_agg.merge(accounts[["account_id", "churn_flag"]], on="account_id", how="inner")
ticket_agg["ticket_count"] = ticket_agg["ticket_count"].fillna(0)

print("\n--- 工单指标对比 ---")
ticket_comp = ticket_agg.groupby("churn_flag")[
    ["ticket_count", "avg_resolution", "avg_response", "avg_satisfaction", "escalation_rate"]
].mean()
ticket_comp.index = ["留存", "流失"]
print(ticket_comp.round(2).to_string())

# Priority distribution
print("\n--- 工单优先级分布 ---")
pri_dist = tickets_with_churn.groupby(["priority", "churn_flag"]).size().unstack(fill_value=0)
print(pri_dist.to_string())

# ── 7. Churn prediction signals summary ──
print("\n" + "=" * 70)
print("7. 流失信号汇总")
print("=" * 70)

signals = [
    ("整体流失率", f"{churn_rate:.1f}%", f"{total_accounts} 个客户中有 {churned} 个流失"),
    ("最高流失套餐", plan_dist["流失率"].idxmax(), f"流失率 {plan_dist['流失率'].max():.1f}%"),
    ("最高流失行业", ind_dist["流失率"].idxmax(), f"流失率 {ind_dist['流失率'].max():.1f}%"),
    ("最高流失渠道", ref_dist["流失率"].idxmax(), f"流失率 {ref_dist['流失率'].max():.1f}%"),
    ("试用客户流失率", f"{trial_dist.loc[True, '流失率']:.1f}%", f"vs 非试用 {trial_dist.loc[False, '流失率']:.1f}%"),
    ("流失 ARR 占比", f"{churned_arr/total_arr*100:.1f}%", f"流失客户 ARR ${churned_arr:,.0f}"),
    ("主要流失原因", reason_dist.index[0] if len(churn_events) > 0 else "N/A",
     f"{reason_dist.iloc[0]} 次 ({reason_dist.iloc[0]/len(churn_events)*100:.1f}%)" if len(churn_events) > 0 else "N/A"),
    ("流失前降级比例", f"{pre_downgrade:.1f}%", "流失客户中曾在流失前降级的比例"),
]
for label, val, note in signals:
    print(f"\n  {label}: {val}")
    print(f"    {note}")

# ── 8. Thinking Models ──
print("\n" + "=" * 70)
print("8. 思维模型")
print("=" * 70)

models = [
    ("1. 分解思维",
     f"总流失率 {churn_rate:.1f}% 按套餐、行业、国家、来源渠道拆解。\n"
     f"  关键发现：{plan_dist['流失率'].idxmax()} 套餐流失率 {plan_dist['流失率'].max():.1f}%，"
     f"远高于整体均值，单一细分拉高了整体数字。"),
    ("2. 分层差异",
     f"不同套餐的流失率差异显著（{plan_dist['流失率'].min():.1f}%~{plan_dist['流失率'].max():.1f}%），"
     f"行业间差距可达 {ind_dist['流失率'].max()-ind_dist['流失率'].min():.1f} 个百分点。\n"
     f"  只看整体流失率 会掩盖高危险细分。"),
    ("3. 间接推断",
     "支持工单满意度、功能使用频率、错误率可作为流失概率的代理信号。\n"
     "  即使客户尚未取消订阅，使用量骤降或工单升级率上升已预示风险。"),
    ("4. 杠杆点识别",
     f"试用客户流失率 {trial_dist.loc[True, '流失率']:.1f}% vs 非试用 {trial_dist.loc[False, '流失率']:.1f}%，"
     f"试用组是高杠杆优化目标。\n"
     f"  改善试用激活流程可将大量高潜力客户转化为付费留存用户。"),
    ("5. 约束 vs 偏好",
     "某些行业的高流失率可能反映产品-市场匹配度（偏好），而非销售策略问题。\n"
     "  如果特定行业的使用深度和满意度都低，产品可能需要针对性改进。"),
]
for m in models:
    print(f"\n  {m[0]}: {m[1]}")

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
