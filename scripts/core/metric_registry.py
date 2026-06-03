"""
Metric Registry

Defines known metrics and their calculation rules.
Can auto-detect which metrics are computable from a given DataFrame.
"""
from .result_schema import metric_entry

# ── Registry: list of known metrics ──
# Each entry: (name, full_name, meaning, formula_func, business_use, required_fields)
# formula_func(df) -> (formula_string, current_value)

METRIC_REGISTRY = [
    {
        "name": "Total Revenue",
        "full_name": "Total Revenue",
        "meaning": "Total sales value",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,.2f}",
            round(df[field].sum(), 2),
        ),
        "business_use": "Core measure of business scale",
        "required_fields": {"Total_Revenue", "revenue", "sales", "Sales", "Weekly_Sales",
                            "total_revenue", "TotalRevenue"},
        "field_priority": ["Total_Revenue", "total_revenue", "Weekly_Sales", "sales", "Sales",
                           "revenue", "TotalRevenue"],
    },
    {
        "name": "Total Spent",
        "full_name": "Total Marketing Spend",
        "meaning": "Total advertising/marketing expenditure",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,.2f}",
            round(df[field].sum(), 2),
        ),
        "business_use": "Measures total marketing investment",
        "required_fields": {"Spent", "spent", "spend", "Cost", "cost"},
        "field_priority": ["Spent", "spent", "spend"],
    },
    {
        "name": "Total Impressions",
        "full_name": "Total Impressions",
        "meaning": "Total ad impressions / views",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,}",
            int(df[field].sum()),
        ),
        "business_use": "Measures campaign reach and visibility",
        "required_fields": {"Impressions", "impressions"},
        "field_priority": ["Impressions", "impressions"],
    },
    {
        "name": "Total Clicks",
        "full_name": "Total Clicks",
        "meaning": "Total ad clicks",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,}",
            int(df[field].sum()),
        ),
        "business_use": "Measures engagement with ads",
        "required_fields": {"Clicks", "clicks"},
        "field_priority": ["Clicks", "clicks"],
    },
    {
        "name": "Total Net Income",
        "full_name": "Total Net Income",
        "meaning": "Total profit after all expenses",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,.2f}",
            round(df[field].sum(), 2),
        ),
        "business_use": "Core measure of profitability",
        "required_fields": {"Net_Income", "net_income", "profit", "Profit"},
        "field_priority": ["Net_Income", "net_income", "profit", "Profit"],
    },
    {
        "name": "Total Assets",
        "full_name": "Total Assets",
        "meaning": "Total company assets",
        "formula_func": lambda df, field: (
            f"Latest {field} = {df[field].iloc[-1]:,.2f}",
            round(df[field].iloc[-1], 2),
        ),
        "business_use": "Measure of company size and resource base",
        "required_fields": {"Total_Assets", "total_assets"},
        "field_priority": ["Total_Assets", "total_assets"],
    },
    {
        "name": "Avg Rating",
        "full_name": "Average Rating",
        "meaning": "Average customer rating score",
        "formula_func": lambda df, field: (
            f"AVG({field}) = {df[field].mean():.2f}",
            round(df[field].mean(), 2),
        ),
        "business_use": "Overall customer satisfaction indicator",
        "required_fields": {"reviews.rating", "rating", "Rating", "score"},
        "field_priority": ["reviews.rating", "rating", "Rating"],
    },
    {
        "name": "Churn Rate",
        "full_name": "Customer Churn Rate",
        "meaning": "Percentage of customers who churned",
        "formula_func": lambda df, field: (
            f"SUM({field}) / COUNT(*) = {df[field].sum()} / {len(df)} = {df[field].mean()*100:.1f}%",
            f"{df[field].mean()*100:.1f}%",
        ),
        "business_use": "Measures customer retention health",
        "required_fields": {"churn_flag", "Churn", "churn", "is_churn"},
        "field_priority": ["churn_flag", "Churn", "churn", "is_churn"],
    },
    {
        "name": "MRR",
        "full_name": "Monthly Recurring Revenue",
        "meaning": "Total monthly recurring revenue from subscriptions",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,.2f}",
            round(df[field].sum(), 2),
        ),
        "business_use": "Core SaaS revenue metric — tracks predictable monthly income",
        "required_fields": {"mrr", "mrr_amount", "MonthlyCharges", "monthly_charges"},
        "field_priority": ["mrr_amount", "mrr", "MonthlyCharges", "monthly_charges"],
    },
    {
        "name": "ARR",
        "full_name": "Annualized Run Rate",
        "meaning": "Annualized recurring revenue (MRR × 12)",
        "formula_func": lambda df, field: (
            f"Latest {field} = {df[field].iloc[-1]:,.2f}",
            round(df[field].iloc[-1], 2),
        ),
        "business_use": "Annualized view of recurring revenue for growth benchmarking",
        "required_fields": {"arr", "arr_amount"},
        "field_priority": ["arr_amount", "arr"],
    },
    {
        "name": "Total Charges",
        "full_name": "Total Customer Charges",
        "meaning": "Total amount charged to customers",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,.2f}",
            round(df[field].sum(), 2),
        ),
        "business_use": "Measures total billing volume over the period",
        "required_fields": {"TotalCharges", "total_charges"},
        "field_priority": ["TotalCharges", "total_charges"],
    },
    {
        "name": "Support Tickets",
        "full_name": "Total Support Tickets",
        "meaning": "Total number of support tickets filed",
        "formula_func": lambda df, field: (
            f"COUNT({field}) = {df[field].nunique():,}",
            int(df[field].nunique()),
        ),
        "business_use": "Measures customer support volume and potential product friction",
        "required_fields": {"ticket_id", "ticket", "case_id", "support_ticket_id"},
        "field_priority": ["ticket_id", "support_ticket_id", "case_id", "ticket"],
    },
    {
        "name": "Avg Satisfaction",
        "full_name": "Average Customer Satisfaction Score",
        "meaning": "Average satisfaction rating from support interactions",
        "formula_func": lambda df, field: (
            f"AVG({field}) = {df[field].mean():.2f}",
            round(df[field].mean(), 2),
        ),
        "business_use": "Measures customer service quality and overall experience",
        "required_fields": {"satisfaction_score", "satisfaction", "csat", "NPS", "nps"},
        "field_priority": ["satisfaction_score", "satisfaction", "csat", "NPS", "nps"],
    },
    {
        "name": "Total Conversions",
        "full_name": "Total Conversions",
        "meaning": "Total number of conversions / successful actions",
        "formula_func": lambda df, field: (
            f"SUM({field}) = {df[field].sum():,}",
            int(df[field].sum()),
        ),
        "business_use": "Measures total successful conversion events",
        "required_fields": {"Total_Conversion", "Conversions", "conversions", "approved_conversion"},
        "field_priority": ["Total_Conversion", "Conversions", "conversions", "approved_conversion"],
    },
]


def find_matching_metrics(df) -> list:
    """
    Scan the registry and return metric_glossary entries for all metrics
    that can be computed from the given DataFrame.
    """
    results = []
    for metric in METRIC_REGISTRY:
        for field_candidate in metric["field_priority"]:
            if field_candidate in df.columns:
                formula_str, value = metric["formula_func"](df, field_candidate)
                results.append(metric_entry(
                    name=metric["name"],
                    full_name=metric["full_name"],
                    meaning=metric["meaning"],
                    formula=formula_str,
                    current_value=value,
                    business_use=metric["business_use"],
                ))
                break
    return results


def detect_derived_metrics(df) -> list:
    """
    Detect derived/computed metrics (e.g., profit margin, CTR, CPC)
    that can be calculated from available fields.
    """
    results = []
    fields = set(df.columns)

    # CTR = Clicks / Impressions * 100
    click_field = next((c for c in ["Clicks", "clicks"] if c in fields), None)
    imp_field = next((c for c in ["Impressions", "impressions"] if c in fields), None)
    if click_field and imp_field and df[imp_field].sum() > 0:
        ctr = df[click_field].sum() / df[imp_field].sum() * 100
        results.append(metric_entry(
            name="CTR",
            full_name="Click-Through Rate",
            meaning="Percentage of impressions that resulted in a click",
            formula=f"SUM({click_field}) / SUM({imp_field}) * 100",
            current_value=f"{ctr:.2f}%",
            business_use="Measures ad relevance and audience targeting effectiveness",
        ))

    # CPC = Spent / Clicks
    spend_field = next((c for c in ["Spent", "spent", "spend"] if c in fields), None)
    if spend_field and click_field and df[click_field].sum() > 0:
        cpc = df[spend_field].sum() / df[click_field].sum()
        results.append(metric_entry(
            name="CPC",
            full_name="Cost Per Click",
            meaning="Average cost per ad click",
            formula=f"SUM({spend_field}) / SUM({click_field})",
            current_value=f"${cpc:.4f}",
            business_use="Measures cost efficiency of click generation",
        ))

    # Profit Margin = Net_Income / Total_Revenue * 100
    rev_field = next((c for c in ["Total_Revenue", "total_revenue", "revenue", "Sales"] if c in fields), None)
    ni_field = next((c for c in ["Net_Income", "net_income", "profit"] if c in fields), None)
    if rev_field and ni_field:
        pm = df[ni_field].iloc[-1] / df[rev_field].iloc[-1] * 100
        results.append(metric_entry(
            name="Profit Margin",
            full_name="Net Profit Margin",
            meaning="Percentage of revenue that becomes profit",
            formula=f"{ni_field} / {rev_field} * 100",
            current_value=f"{pm:.2f}%",
            business_use="Measures profitability efficiency",
        ))

    # Debt Ratio = Total_Liabilities / Total_Assets * 100
    liab_field = next((c for c in ["Total_Liabilities", "total_liabilities"] if c in fields), None)
    asset_field = next((c for c in ["Total_Assets", "total_assets"] if c in fields), None)
    if liab_field and asset_field:
        dr = df[liab_field].iloc[-1] / df[asset_field].iloc[-1] * 100
        results.append(metric_entry(
            name="Debt Ratio",
            full_name="Debt-to-Assets Ratio",
            meaning="Percentage of assets financed by debt",
            formula=f"{liab_field} / {asset_field} * 100",
            current_value=f"{dr:.2f}%",
            business_use="Measures financial leverage and risk",
        ))

    # Conversion Rate = Total_Conversion / Clicks * 100
    conv_field = next((c for c in ["Total_Conversion", "Conversions", "conversions"] if c in fields), None)
    if conv_field and click_field and df[click_field].sum() > 0:
        cvr = df[conv_field].sum() / df[click_field].sum() * 100
        results.append(metric_entry(
            name="Conversion Rate",
            full_name="Conversion Rate",
            meaning="Percentage of clicks that resulted in a conversion",
            formula=f"SUM({conv_field}) / SUM({click_field}) * 100",
            current_value=f"{cvr:.2f}%",
            business_use="Measures post-click effectiveness",
        ))

    return results
