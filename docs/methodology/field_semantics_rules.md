# Field Semantics Rules

This document explains how the field semantics recognition works, what it can and cannot identify, and what the confidence levels mean.

## 1. Current Recognition Method

字段语义识别**不使用** LLM 或 AI 模型。当前实现使用**正则表达式规则匹配**。

具体机制：

```python
_SEMANTIC_PATTERNS = [
    (r"(?i)^(customer_id|cust_id|client_id)$", "Customer identifier", "high"),
    (r"(?i).*date.*", "Date field", "high"),
    # ... 共 130+ 条规则
]

def infer_semantics(df):
    for field in df.columns:
        for pattern, meaning, confidence in _SEMANTIC_PATTERNS:
            if re.match(pattern, field):
                # 匹配 → 记录语义和置信度
                break
        else:
            # 未匹配 → 标记 "Unknown — review needed"
```

即：对每个字段名，从上到下依次尝试正则匹配，命中了就记录语义并停止，都不命中就标记未知。

## 2. Recognition Basis

字段识别依据以下信息：

| 依据 | 说明 | 示例 |
|------|------|------|
| **字段名** | 主要依据。正则匹配字段名字符串 | `customer_id` → "Customer identifier" |
| **数据类型** | pandas dtype 间接使用（分析阶段会检查 dtype，但语义识别阶段只用字段名） | 未直接使用 |
| **字段名模式** | 通配/模糊匹配 | `.*date.*` 匹配所有含 "date" 的字段 |
| **预定义语义规则库** | 130+ 条正则规则，按业务域分组 | finance / marketing / SaaS / retail 等 |

当前版本**不**使用以下信息来推断语义：
- 字段中的样本数据值
- 字段的统计分布特征
- 字段之间的关联关系
- LLM/API 调用
- 外部知识库

## 3. Confidence Levels

| 置信度 | 含义 | 判定标准 |
|--------|------|----------|
| **high** | 字段名与明确的具体规则高度匹配 | 精确匹配具体关键词，如 `customer_id` 匹配 `^(customer_id|cust_id|client_id)$` |
| **medium** | 字段名与通用模式或弱规则匹配 | 匹配通用模式，如 `.*date.*` 匹配所有含 date 的字段；或匹配业务相关但不精确的规则 |
| **low** | 无法确定，需要人工检查 | 没有任何规则匹配该字段名；或匹配到的规则与预期业务含义不符 |

**high 的典型例子：**
- `customer_id` → Customer identifier (high)
- `revenue` → Revenue / total sales (high)
- `churn_flag` → Churn status indicator (high)

**medium 的典型例子：**
- `interest` → Interest category (medium) — 可能是广告兴趣分类，也可能是金融利息
- `type` → Type / classification (medium) — 太模糊

**low 的典型例子：**
- `xyz_campaign_id` → 匹配到 Campaign/ad identifier (high)，但如果字段名不在规则库中则 → Unknown (low)
- 任意中文字段名 → 全部 Unknown (low)

## 4. Supported Field Types

当前规则库覆盖以下类型的字段（按业务域分组）：

| 类型 | 规则示例 | 覆盖数量 |
|------|----------|----------|
| 客户 ID | `customer_id`, `cust_id`, `client_id` | ~5 |
| 产品 ID | `product_id`, `sku`, `stock_code` | ~3 |
| 订单/交易 ID | `order_id`, `invoice_no`, `transaction_id` | ~3 |
| 门店 ID | `store_id`, `store`, `branch_id` | ~3 |
| 广告/活动 ID | `campaign_id`, `ad_id`, `xyz_campaign_id`, `fb_campaign_id` | ~4 |
| 时间字段 | `.*date.*`, `.*time.*`, `year`, `month`, `quarter` | ~5 |
| 金额字段 | `revenue`, `sales`, `spent`, `cost`, `price`, `profit` | ~15 |
| 数量字段 | `quantity`, `qty` | ~2 |
| 广告指标 | `clicks`, `impressions`, `ctr`, `spent` | ~8 |
| 财务字段 | `total_assets`, `total_liabilities`, `cash_flow`, `cik_number` | ~5 |
| 零售字段 | `store_size`, `sq_ft`, `isholiday`, `fuel_price`, `temperature` | ~5 |
| 类别/分组 | `category`, `department`, `country`, `region`, `age_group`, `gender` | ~12 |
| 客户状态 | `churn_flag`, `tenure`, `satisfaction_score`, `rating` | ~8 |
| SaaS 订阅 | `mrr`, `arr`, `plan_tier`, `seats`, `billing_frequency`, `subscription_id` | ~15 |
| 使用分析 | `usage_count`, `usage_duration_secs`, `error_count`, `feature_name` | ~6 |
| 支持工单 | `ticket_id`, `priority`, `resolution_time_hours`, `first_response_time_minutes` | ~10 |
| 流失事件 | `churn_date`, `reason_code`, `refund_amount_usd`, `is_reactivation` | ~6 |
| 其他 | `name`, `description`, `title`, `status`, `flag`, `index` | ~6 |

合计约 130+ 条规则模式，覆盖 16 个业务域。

## 5. Cases Where Recognition May Fail

| 情况 | 问题 | 影响 |
|------|------|------|
| **中文字段名** | 规则库只包含英文/拼音模式 | 全部标记为 Unknown (low) |
| **非标准缩写** | 如 `cust_id` 可以识别，但 `cst_id`, `cus_id` 不在规则中 | 无法识别 |
| **拼写错误** | 如 `categorie` 而非 `categories` | 无法识别 |
| **内部代号** | 如 `dim_01`, `fact_02`, `col_A` | 全部标记为 Unknown (low) |
| **多义词** | 如 `interest` 可以是广告兴趣或金融利息 | 只匹配到一种含义，没有消歧能力 |
| **字段名过短** | 如 `id`, `no`, `dt`, `amt`, `qty` | `id` 匹配 Unique identifier (high)，但无法区分是客户 ID 还是产品 ID |
| **复合含义字段** | 如 `total_revenue_usd_2023` 包含了多个信息片段 | 正则 `.*revenue.*` 可以匹配，但无法提取时间、币种等附加信息 |
| **分拆信息字段** | 如 `year`, `month`, `day` 分列存储 | 每个字段可以单独识别，但无法将三者关联为"完整日期" |
| **枚举代码字段** | 如 `status_code` 值为 0/1/2，但无显式说明 | 只能识别为 "Status / boolean flag" (medium)，无法说明枚举值的业务含义 |

## 6. 当字段语义不准确时的安全措施

当前机制在面对不确定字段时，通过以下方式降低误导风险：

1. **置信度分级**：`low` 置信度的字段明确标记 "Unknown — review needed"，要求人工确认
2. **仅用于教育目的**：字段语义主要用于 `field_semantics` 表和学习笔记，不直接参与指标计算决策
3. **指标匹配独立于语义**：指标匹配 (`metric_registry.py`) 使用精确字段名匹配，不依赖语义推断结果。即使语义识别失败，只要字段名在指标优先级列表中，指标计算仍能正常执行

## 7. Future Improvements

以下改进方向已识别但尚未实现：

| 方向 | 预期效果 | 实现难度 |
|------|----------|----------|
| 增加中文字段名规则 | 覆盖使用中文命名的数据集 | 低（增加正则规则即可） |
| 增加常见缩写映射表 | 提高非标准缩写的识别率 | 中（需要收集常见缩写变体） |
| 增加唯一值比例判断 | 区分 ID 字段和类别字段 | 低（`nunique/len` 逻辑已有） |
| 增加样本值模式判断 | 通过样本数据推断字段含义 | 中（需要抽样 + 模式分析逻辑） |
| 增加人工确认机制 | 对 low 置信度字段要求用户确认 | 低（在 agent 交互中实现） |
| 增加语义识别日志 | 记录每个字段的匹配过程和结果 | 低（参见 audit_log_design.md） |
