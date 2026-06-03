"""
Field Semantics Module

Infer business meanings from field names using keyword matching.
"""
import re
from .result_schema import field_semantic


# ── Keyword -> Meaning mapping ──
_SEMANTIC_PATTERNS = [
    # ── Chinese field name patterns (checked first) ──
    # Date / Time
    (r"^.*(日期|时间|年月日).*$", "日期字段", "high"),
    (r"^(年|年份)$", "年份", "high"),
    (r"^(月|月份)$", "月份", "high"),
    (r"^(季度|季)$", "季度", "high"),

    # Monetary
    (r"^.*(营收|收入|销售额|销售金额|流水|GMV).*$", "收入/销售额", "high"),
    (r"^.*(成本|费用|支出|花费|广告费|投放费).*$", "成本/费用", "high"),
    (r"^.*(利润|净利|毛利|盈利|净收入).*$", "利润", "high"),
    (r"^.*(价格|单价|均价|客单价|金额|售价).*$", "单价/金额", "high"),
    (r"^.*(预算).*$", "预算金额", "medium"),
    (r"^.*(退款|退款金额|退货金额).*$", "退款金额", "high"),

    # Counts / Metrics
    (r"^.*(数量|销量|销售量|件数|购买量).*$", "交易数量", "high"),
    (r"^.*(点击|点击量|点击次数).*$", "点击量", "high"),
    (r"^.*(曝光|曝光量|曝光次数|展示量).*$", "曝光量", "high"),
    (r"^.*(转化|转化量|转化数|成交数).*$", "转化量", "high"),
    (r"^.*(浏览|浏览量|访问量|PV|UV).*$", "浏览/访问量", "high"),

    # Identifiers
    (r"^.*(客户ID|客户编号|用户ID|用户编号|会员ID).*$", "客户标识", "high"),
    (r"^.*(产品ID|产品编号|商品ID|商品编号|SKU|货号).*$", "产品标识", "high"),
    (r"^.*(订单ID|订单编号|交易ID|交易编号).*$", "交易标识", "high"),
    (r"^.*(门店ID|门店编号|店铺ID|店铺编号|网点ID).*$", "门店标识", "high"),
    (r"^.*(活动ID|广告ID|推广ID).*$", "活动/广告标识", "high"),

    # Categorical
    (r"^.*(类别|类型|分类|品类|种类|类目).*$", "类别/分类", "high"),
    (r"^.*(地区|区域|城市|省份|省$|市$|国家|市场).*$", "地理区域", "high"),
    (r"^性别$", "性别", "high"),
    (r"^.*(年龄|年龄段|年龄组).*$", "年龄/人群属性", "high"),
    (r"^.*(渠道|来源|获客渠道|推广渠道).*$", "获客/来源渠道", "high"),

    # Ratings / Feedback
    (r"^.*(评分|评价|打分|满意度|星级|好评).*$", "评分/满意度", "high"),
    (r"^.*(评价内容|评论|反馈内容).*$", "评价/反馈文本", "medium"),

    # Status / Flags
    (r"^.*(状态|是否|标志|标识).*$", "状态/布尔标记", "medium"),
    (r"^.*(是否会员|是否复购|是否流失|是否续费).*$", "状态标记", "high"),

    # Text / Name
    (r"^.*(名称|名字|描述|备注|说明).*$", "名称/描述文本", "medium"),

    # General
    (r"^(编号|序号|代码|编码)$", "编号/序号", "low"),

    # ── English field name patterns ──
    # Identifiers
    (r"(?i)^(id|.*_id|.*_uuid|.*_key)$", "Unique identifier", "high"),
    (r"(?i)^(customer_id|cust_id|client_id)$", "Customer identifier", "high"),
    (r"(?i)^(product_id|sku|stock_code)$", "Product identifier", "high"),
    (r"(?i)^(order_id|invoice_no|transaction_id)$", "Transaction identifier", "high"),
    (r"(?i)^(store_id|store|branch_id)$", "Store/location identifier", "high"),
    (r"(?i)^(campaign_id|ad_id|xyz_campaign_id|fb_campaign_id)$", "Campaign/ad identifier", "high"),

    # Date / Time
    (r"(?i).*date.*", "Date field", "high"),
    (r"(?i).*time.*", "Time field", "high"),
    (r"(?i)^year$", "Year", "high"),
    (r"(?i)^month$", "Month", "high"),
    (r"(?i)^quarter$", "Quarter", "high"),

    # Monetary
    (r"(?i)^(revenue|sales|total_revenue|gross_revenue|net_revenue)$", "Revenue / total sales", "high"),
    (r"(?i)^(spent|spend|ad_spend|cost|cpc|cpm|total_spent)$", "Marketing spend / cost", "high"),
    (r"(?i)^(profit|net_income|gross_profit|operating_profit)$", "Profit / net income", "high"),
    (r"(?i)^(price|unit_price|amount|value|aov)$", "Monetary value per unit", "high"),
    (r"(?i)^(arr|mrr|subscription_revenue)$", "Recurring revenue", "high"),
    (r"(?i)^(total_charges|monthly_charges)$", "Customer charges / fees", "high"),
    (r"(?i)^(budget)$", "Budget allocation", "medium"),

    # Counts / Metrics
    (r"(?i)^(quantity|qty)$", "Transaction quantity", "high"),
    (r"(?i)^(clicks|impressions|ctr)$", "Ad engagement metric", "high"),
    (r"(?i)^(total_conversion|approved_conversion|conversions)$", "Conversion count", "high"),
    (r"(?i)^(weekly_sales)$", "Weekly sales figure", "high"),
    (r"(?i)^(churn_flag|churned|is_churn)$", "Churn status indicator", "high"),
    (r"(?i)^(tenure|seniority|account_age)$", "Customer tenure / account age", "high"),
    (r"(?i)^(rating|score|review_rating)$", "Rating / satisfaction score", "high"),
    (r"(?i)^(review_len|review_length|text_len)$", "Review / text length", "medium"),
    (r"(?i)^(reviews\.numHelpful|num_helpful|helpful_votes)$", "Helpfulness votes", "medium"),

    # Categorical flags
    (r"(?i)^(gender|sex)$", "Gender", "high"),
    (r"(?i)^(age|age_group|age_range)$", "Age group / demographic", "high"),
    (r"(?i)^(country|region|market|area)$", "Geographic region", "high"),
    (r"(?i)^(category|categories|product_category|department|dept)$", "Category / department", "high"),
    (r"(?i)^(type|store_type|business_type)$", "Type / classification", "medium"),
    (r"(?i)^(industry|vertical)$", "Industry / vertical", "high"),
    (r"(?i)^(source|channel|referral_source|acquisition_channel)$", "Acquisition / source channel", "high"),
    (r"(?i)^(contract|plan|tier|subscription_type)$", "Contract / plan type", "high"),
    (r"(?i)^(status|state|flag|is_.*)$", "Status / boolean flag", "medium"),
    (r"(?i)^(interest)$", "Interest category", "medium"),
    (r"(?i)^(name|description|title|review_text|reviews\.text)$", "Text / description field", "medium"),

    # Financial statements
    (r"(?i)^(total_assets)$", "Total assets", "high"),
    (r"(?i)^(total_liabilities)$", "Total liabilities", "high"),
    (r"(?i)^(cash_flow)$", "Cash flow", "high"),
    (r"(?i)^(cik_number)$", "SEC CIK identifier (company filing)", "high"),
    (r"(?i)^(filling_type)$", "SEC filing type", "medium"),

    # Retail specific
    (r"(?i)^(size|store_size|sq_ft)$", "Store size / square footage", "high"),
    (r"(?i)^(isholiday|is_holiday|holiday)$", "Holiday flag", "high"),
    (r"(?i)^(cpi|unemployment|fuel_price|temperature)$", "External economic/environmental factor", "medium"),

    # General
    (r"(?i)^(index)$", "Row index / sequence number", "low"),

    # SaaS / Subscription
    (r"(?i)^(mrr|mrr_amount)$", "Monthly recurring revenue (MRR)", "high"),
    (r"(?i)^(arr|arr_amount)$", "Annualized recurring revenue (ARR)", "high"),
    (r"(?i)^(subscription_id)$", "Subscription identifier", "high"),
    (r"(?i)^(plan_tier)$", "Subscription plan tier level", "high"),
    (r"(?i)^(billing_frequency)$", "Billing cycle frequency (monthly/yearly)", "high"),
    (r"(?i)^(is_trial)$", "Free trial status flag", "medium"),
    (r"(?i)^(auto_renew_flag|auto_renew)$", "Auto-renewal setting flag", "medium"),
    (r"(?i)^(upgrade_flag|is_upgrade)$", "Upgrade event indicator", "medium"),
    (r"(?i)^(downgrade_flag|is_downgrade)$", "Downgrade event indicator", "medium"),
    (r"(?i)^(seats|num_seats)$", "Number of license seats", "high"),
    (r"(?i)^(tenure|account_age|seniority)$", "Customer tenure / account age", "high"),
    (r"(?i)^(churn_flag|churned|is_churn|churn)$", "Churn status indicator", "high"),
    (r"(?i)^(total_charges|monthly_charges)$", "Customer charges / billing amount", "high"),

    # Usage analytics
    (r"(?i)^(usage_id)$", "Usage event identifier", "high"),
    (r"(?i)^(usage_date)$", "Usage event date", "high"),
    (r"(?i)^(feature_name)$", "Software feature name", "high"),
    (r"(?i)^(usage_count)$", "Feature usage count", "high"),
    (r"(?i)^(usage_duration_secs)$", "Usage duration in seconds", "high"),
    (r"(?i)^(error_count)$", "Error occurrence count", "high"),
    (r"(?i)^(is_beta_feature)$", "Beta feature flag", "medium"),

    # Support tickets
    (r"(?i)^(ticket_id)$", "Support ticket identifier", "high"),
    (r"(?i)^(submitted_at)$", "Ticket submission timestamp", "high"),
    (r"(?i)^(closed_at)$", "Ticket closure timestamp", "high"),
    (r"(?i)^(resolution_time_hours)$", "Ticket resolution time (hours)", "high"),
    (r"(?i)^(priority|ticket_priority)$", "Ticket priority level", "high"),
    (r"(?i)^(first_response_time_minutes)$", "First response time (minutes)", "high"),
    (r"(?i)^(satisfaction_score|csat)$", "Customer satisfaction score", "high"),
    (r"(?i)^(escalation_flag|is_escalated)$", "Escalation indicator", "medium"),
    (r"(?i)^(feedback_text|ticket_description)$", "Customer feedback / ticket description", "medium"),

    # Churn events
    (r"(?i)^(churn_event_id)$", "Churn event identifier", "high"),
    (r"(?i)^(churn_date)$", "Churn event date", "high"),
    (r"(?i)^(reason_code)$", "Churn reason category code", "high"),
    (r"(?i)^(refund_amount_usd)$", "Refund amount in USD", "high"),
    (r"(?i)^(preceding_upgrade_flag)$", "Upgrade event preceding churn", "medium"),
    (r"(?i)^(preceding_downgrade_flag)$", "Downgrade event preceding churn", "medium"),
    (r"(?i)^(is_reactivation)$", "Reactivation flag (returning customer)", "medium"),

    # Referral / acquisition
    (r"(?i)^(referral_source)$", "Customer referral / acquisition source", "high"),
    (r"(?i)^(signup_date)$", "Customer signup / registration date", "high"),

    # Industry / company
    (r"(?i)^(industry)$", "Industry classification", "high"),
    (r"(?i)^(account_name|company_name)$", "Company / account name", "high"),
]


def infer_semantics(df, field_names=None) -> list:
    """
    Infer business meanings for all fields in a DataFrame.
    Returns a list of field_semantic dicts.
    """
    if field_names is None:
        field_names = list(df.columns)

    results = []
    for field in field_names:
        matched = False
        for pattern, meaning, confidence in _SEMANTIC_PATTERNS:
            if re.match(pattern, field):
                results.append(field_semantic(
                    field=field,
                    inferred_meaning=meaning,
                    confidence=confidence,
                    evidence=f"Matched pattern: {pattern}",
                ))
                matched = True
                break
        if not matched:
            results.append(field_semantic(
                field=field,
                inferred_meaning="Unknown — review needed",
                confidence="low",
                evidence="No matching semantic pattern",
            ))
    return results
