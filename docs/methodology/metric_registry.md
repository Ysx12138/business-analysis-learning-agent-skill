# Metric Registry

This document lists every metric in the current metric registry (`metric_registry.py`).

每个指标条目说明：
- 匹配逻辑：`field_priority` 列表顺序取第一个匹配的字段名
- 计算逻辑：`formula_func` 中定义的 pandas 操作
- 衍生指标：需要多个字段同时存在才能计算

---

## 注册表指标

### Total Revenue

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Revenue |
| **业务含义** | 总销售收入 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Total_Revenue, total_revenue, Weekly_Sales, sales, Sales, revenue, TotalRevenue（按优先级顺序匹配） |
| **适用场景** | 零售、电商、订阅业务的整体收入规模评估 |
| **不适用场景** | 数据集不含收入字段，或收入数据已被预聚合 |
| **风险提示** | 只是简单求和，不区分正负；如果数据包含退款/取消单，求和结果会偏低 |

### Total Spent

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Marketing Spend |
| **业务含义** | 总营销/广告支出 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Spent, spent, spend, Cost, cost（按优先级顺序匹配） |
| **适用场景** | 广告投放分析、营销活动效果评估 |
| **不适用场景** | 非营销类数据 |
| **风险提示** | 零花费记录会影响 CPC、ROI 等衍生指标的解读 |

### Total Impressions

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Impressions |
| **业务含义** | 广告总曝光量 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Impressions, impressions |
| **适用场景** | 广告投放分析 |
| **不适用场景** | 缺少曝光字段的数据集 |
| **风险提示** | 曝光数据可能来自不同平台的统计口径，横向对比需要注意口径一致性 |

### Total Clicks

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Clicks |
| **业务含义** | 广告总点击数 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Clicks, clicks |
| **适用场景** | 广告投放分析、转化漏斗 |
| **不适用场景** | 非广告数据 |
| **风险提示** | 点击数不等于独立用户数，同一个用户可能多次点击 |

### Total Net Income

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Net Income |
| **业务含义** | 总净利润 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Net_Income, net_income, profit, Profit |
| **适用场景** | 财务分析、公司盈利评估 |
| **不适用场景** | 数据集不含利润字段 |
| **风险提示** | 净利润口径（税前/税后/运营利润）因数据源不同，跨数据集对比时需要确认口径一致性 |

### Total Assets

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Assets |
| **业务含义** | 总资产 |
| **计算公式** | 取最后一个值（`iloc[-1]`） |
| **所需字段** | Total_Assets, total_assets |
| **适用场景** | 财务分析、资产负债评估 |
| **不适用场景** | 只包含利润表数据时 |
| **风险提示** | 取最后一个值而非求和，因为资产是存量指标而非流量指标 |

### Avg Rating

| 项目 | 内容 |
|------|------|
| **英文名称** | Average Rating |
| **业务含义** | 平均客户评分 |
| **计算公式** | `AVG(field)` |
| **所需字段** | reviews.rating, rating, Rating, score |
| **适用场景** | 产品评论分析、满意度评估 |
| **不适用场景** | 评分分布极偏时（如几乎所有评分都是 5 星），平均值信息量有限 |
| **风险提示** | 评分均值会掩盖分布差异。建议同时查看评分占比分布 |

### Churn Rate

| 项目 | 内容 |
|------|------|
| **英文名称** | Customer Churn Rate |
| **业务含义** | 客户流失率 |
| **计算公式** | `SUM(field) / COUNT(*)` |
| **所需字段** | churn_flag, Churn, churn, is_churn |
| **适用场景** | SaaS 订阅分析、客户留存评估 |
| **不适用场景** | 数据集不含流失标签字段 |
| **风险提示** | 流失标签的定义因业务而异（主动取消 / 欠费停用 / 长期不活跃），跨数据对比时需确认定义是否一致 |

### MRR

| 项目 | 内容 |
|------|------|
| **英文名称** | Monthly Recurring Revenue |
| **业务含义** | 月度经常性收入 |
| **计算公式** | `SUM(field)` |
| **所需字段** | mrr, mrr_amount, MonthlyCharges, monthly_charges |
| **适用场景** | SaaS 订阅业务分析 |
| **不适用场景** | 非订阅制业务 |
| **风险提示** | MRR 通常排除一次性费用，但数据集中可能未区分。Sum 结果可能包含非经常性收入 |

### ARR

| 项目 | 内容 |
|------|------|
| **英文名称** | Annualized Run Rate |
| **业务含义** | 年化经常性收入 |
| **计算公式** | 取最后一个值（`iloc[-1]`） |
| **所需字段** | arr, arr_amount |
| **适用场景** | SaaS 订阅业务的年度收入评估 |
| **不适用场景** | 数据集不含 ARR 字段，或业务非订阅制 |
| **风险提示** | ARR 通常是月度 MRR × 12 计算得出，如果数据源已经计算好了 ARR，需要注意其计算口径 |

### Total Charges

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Customer Charges |
| **业务含义** | 客户费用总额 |
| **计算公式** | `SUM(field)` |
| **所需字段** | TotalCharges, total_charges |
| **适用场景** | SaaS 客户账单分析 |
| **不适用场景** | 缺少费用字段 |
| **风险提示** | 需要与收入字段配合使用才能评估盈利性 |

### Support Tickets

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Support Tickets |
| **业务含义** | 支持工单总数 |
| **计算公式** | `COUNT_DISTINCT(field)` |
| **所需字段** | ticket_id, ticket, case_id, support_ticket_id |
| **适用场景** | 客户支持分析 |
| **不适用场景** | 缺少工单标识字段 |
| **风险提示** | 使用 `nunique()` 计算唯一工单数，如果工单 ID 重复较多，计数会低于记录条数 |

### Avg Satisfaction

| 项目 | 内容 |
|------|------|
| **英文名称** | Average Customer Satisfaction Score |
| **业务含义** | 平均客户满意度评分 |
| **计算公式** | `AVG(field)` |
| **所需字段** | satisfaction_score, satisfaction, csat, NPS, nps |
| **适用场景** | 客服质量评估、客户体验分析 |
| **不适用场景** | 缺少满意度字段 |
| **风险提示** | 不同数据源对满意度评分的量纲可能不同（1-5 分 vs 1-10 分），需要注意 |

### Total Conversions

| 项目 | 内容 |
|------|------|
| **英文名称** | Total Conversions |
| **业务含义** | 总转化数 |
| **计算公式** | `SUM(field)` |
| **所需字段** | Total_Conversion, Conversions, conversions, approved_conversion |
| **适用场景** | 广告效果分析、转化漏斗 |
| **不适用场景** | 缺少转化字段 |
| **风险提示** | 转化定义因行业和平台不同（如购买、注册、下载等），跨数据对比需确认定义 |

---

## 衍生指标

### CTR 点击率

| 项目 | 内容 |
|------|------|
| **英文名称** | Click-Through Rate |
| **业务含义** | 广告曝光后产生点击的比例 |
| **计算公式** | `SUM(Clicks) / SUM(Impressions) × 100%` |
| **所需字段** | Clicks 或 clicks + Impressions 或 impressions |
| **适用场景** | 广告投放分析、素材效果评估 |
| **不适用场景** | 缺少曝光或点击字段 |
| **风险提示** | CTR 反映的是点击效率，不反映点击后的转化效果。高 CTR 低转化率可能说明落地页体验不佳 |

### CPC 单次点击成本

| 项目 | 内容 |
|------|------|
| **英文名称** | Cost Per Click |
| **业务含义** | 平均每次点击的广告花费 |
| **计算公式** | `SUM(Spent) / SUM(Clicks)` |
| **所需字段** | Spent/spent/spend + Clicks/clicks |
| **适用场景** | 广告投放成本效率分析 |
| **不适用场景** | 缺少花费或点击字段 |
| **风险提示** | CPC 低不一定意味着效果好——如果点击质量差（不转化），低 CPC 没有意义 |

### Profit Margin 利润率

| 项目 | 内容 |
|------|------|
| **英文名称** | Net Profit Margin |
| **业务含义** | 收入转化为利润的比例 |
| **计算公式** | `(Net_Income / Total_Revenue) × 100%` |
| **所需字段** | Net_Income/net_income/profit + Total_Revenue/total_revenue/revenue/Sales |
| **适用场景** | 财务分析、公司盈利效率评估 |
| **不适用场景** | 缺少收入或利润字段；数据周期不一致（如收入是全年数据，利润是半年数据） |
| **风险提示** | 取最后一个年份/期间的值，不一定是全年累计。利润率跨行业对比参考价值有限 |

### Debt Ratio 负债率

| 项目 | 内容 |
|------|------|
| **英文名称** | Debt-to-Assets Ratio |
| **业务含义** | 总资产中由负债融资的比例 |
| **计算公式** | `(Total_Liabilities / Total_Assets) × 100%` |
| **所需字段** | Total_Liabilities/total_liabilities + Total_Assets/total_assets |
| **适用场景** | 财务分析、公司偿债能力评估 |
| **不适用场景** | 缺少负债或资产字段 |
| **风险提示** | 负债率高不一定代表风险高（如 Apple 负债率高但 ROA 更高→资本运用效率高）。负债率需要结合行业平均水平和盈利能力一起看 |

### Conversion Rate 转化率

| 项目 | 内容 |
|------|------|
| **英文名称** | Conversion Rate |
| **业务含义** | 点击后完成转化的比例 |
| **计算公式** | `SUM(Total_Conversion) / SUM(Clicks) × 100%` |
| **所需字段** | Total_Conversion/Conversions + Clicks/clicks |
| **适用场景** | 广告投放、转化漏斗分析 |
| **不适用场景** | 缺少转化或点击字段 |
| **风险提示** | 转化定义因业务不同（购买/注册/下载/留资），跨数据对比需确认定义是否一致 |

---

## 指标匹配优先级规则

每个指标定义了一个 `field_priority` 列表。匹配时按列表顺序检查字段名是否在 DataFrame 的 columns 中，取第一个匹配的字段进行计算。

例如 Total Revenue 的优先级：

```
Total_Revenue → total_revenue → Weekly_Sales → sales → Sales → revenue → TotalRevenue
```

如果一个数据集同时包含 `Sales` 和 `revenue` 两个字段，最终会使用 `Sales`（因为它在列表中排名靠前）。

**影响：** 同一指标在不同数据集上可能使用了不同的字段名。跨数据集对比时需要注意字段口径是否一致。

---

## 缺失字段时的行为

如果 DataFrame 中没有匹配到任何 `field_priority` 中的字段：
- 注册表指标：被静默跳过，不出现在 `metric_glossary` 中
- 衍生指标：缺少所需字段组合时跳过，不会尝试替代字段

没有告警或日志提示指标被跳过。这是当前版本的已知限制（参见 `audit_log_design.md`）。
