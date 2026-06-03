"""
Analysis Planner

Automatically chooses analysis modules based on available fields.
Produces tables and findings for the report.
"""
import pandas as pd
import numpy as np
from .result_schema import finding, thinking_model, recommendation, table_sheet, risk_check


def plan_analysis(df: pd.DataFrame, field_semantics: list = None) -> dict:
    """
    Main entry point. Inspects the DataFrame and returns:
    - tables: list of table_sheet dicts for rendering
    - findings: list of finding dicts
    - thinking_models: list of thinking_model dicts
    - recommendations: list of recommendation dicts
    - risk_checks: list of risk_check dicts
    - metrics: list of metric_entry dicts
    """
    tables = []
    findings_list = []
    models_list = []
    recs_list = []
    risk_list = []

    # Build a lookup: column_name → human-readable business meaning
    _col_meaning = {}
    if field_semantics:
        for fs in field_semantics:
            meaning = fs.get("inferred_meaning", "")
            if meaning and meaning not in ("Unknown — review needed", "Unique identifier"):
                _col_meaning[fs["field"]] = meaning

    fields = set(df.columns)

    # Identify columns to exclude from analysis (identifiers, indices, years, URLs, etc.)
    _id_keywords = ["_id", "_key", "_uuid", "cik", "index", "ad_id", "campaign_id",
                    "fb_campaign", "invoice", "stock_code", "sku", "asin", "url",
                    "image", "source", "key"]
    _id_exact = {"id", "dateadded", "dateupdated", "keys", "imageurls", "sourceurls",
                 "manufacturernumber"}
    _exclude_cols = set()
    for col in df.columns:
        col_lower = col.lower().replace(".", "").replace("_", "").replace(" ", "")
        if col_lower in _id_exact:
            _exclude_cols.add(col)
        elif any(kw in col.lower() for kw in _id_keywords):
            _exclude_cols.add(col)

    numeric_cols = [c for c in df.select_dtypes(include=["number"]).columns
                    if c not in _exclude_cols]
    # Also exclude columns with <3 unique values that are clearly not metrics
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 3 or c.lower() not in ("year",)]

    # Category columns: object type, 2-50 unique values, not excluded, not date-like
    cat_cols = [c for c in df.columns
                if c not in _exclude_cols
                and ((df[c].dtype == "object" and 2 <= df[c].nunique() <= 50)
                     or df[c].dtype.name == "category")]
    # Filter out date-like strings (e.g. "2018-01-01T00:00:00Z")
    _date_patterns = ["date", "time", "added", "updated", "seen"]
    cat_cols = [c for c in cat_cols
                if not any(p in c.lower() for p in _date_patterns)]
    date_cols = list(df.select_dtypes(include=["datetime64"]).columns)

    # ── Risk Checks ──
    for col in numeric_cols:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0 and neg_count / len(df) > 0.01:
            risk_list.append(risk_check(
                check=f"Negative values in {col}",
                status="warn",
                detail=f"{neg_count} rows ({neg_count/len(df)*100:.1f}%) have negative values in {col}",
                affected_analysis="Summary statistics and ranking may be misleading",
            ))
        zero_count = (df[col] == 0).sum()
        if zero_count / len(df) > 0.3 and ("spent" in col.lower() or "cost" in col.lower()):
            risk_list.append(risk_check(
                check=f"High zero-rate in {col}",
                status="warn",
                detail=f"{zero_count} rows ({zero_count/len(df)*100:.1f}%) have zero {col}",
                affected_analysis="Averages and efficiency metrics may be overstated",
            ))

    # Missing values check
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing > 0 and missing / len(df) > 0.05:
            risk_list.append(risk_check(
                check=f"Missing values in {col}",
                status="warn",
                detail=f"{missing} rows ({missing/len(df)*100:.1f}%) missing",
                affected_analysis="Analysis involving this field will have reduced sample size",
            ))

    # ── Ranking Analysis (category + metric pairs) ──
    for cat_col in cat_cols[:3]:  # limit to first 3 categorical dimensions
        for num_col in numeric_cols[:2]:  # limit to first 2 numeric
            try:
                ranking = df.groupby(cat_col)[num_col].agg(["sum", "mean", "count"]) \
                    .sort_values("sum", ascending=False).reset_index()
                ranking.columns = [cat_col, f"{num_col}_合计", f"{num_col}_均值", "记录数"]
                tables.append(table_sheet(
                    name=f"按{cat_col}看{num_col}",
                    headers=list(ranking.columns),
                    data=[[round(v, 2) if isinstance(v, float) else v for v in row]
                          for row in ranking.values],
                ))
                # Generate finding if top/bottom are notable
                if len(ranking) >= 3:
                    top = ranking.iloc[0]
                    bot = ranking.iloc[-1]
                    top_name = top.iloc[0]
                    top_val = top.iloc[1]
                    bot_name = bot.iloc[0]
                    bot_val = bot.iloc[1]
                    ratio_str = f"Range ratio: {top_val/bot_val:.1f}x" if bot_val != 0 else "leads by a large margin"
                    findings_list.append(finding(
                        title=f"{num_col} Top/Bottom by {cat_col}",
                        data_evidence=f"Top: {top_name} ({top_val:,.2f}), Bottom: {bot_name} ({bot_val:,.2f}). {ratio_str}",
                        business_interpretation=f"{cat_col} is a strong differentiator for {num_col}. The gap between top and bottom segments suggests significant optimization opportunity.",
                        suggested_action=f"Investigate what drives success in top {cat_col} segments and apply best practices to lower performers.",
                        metric_to_track=f"{num_col} by {cat_col} over time",
                        what_it_cannot_prove=(
                            f"这个结果只能说明 {cat_col} 分组之间的 {num_col} 表现存在差异，"
                            f"不能证明 {cat_col} 本身导致了这种差异。差异也可能来自样本量、门店规模、渠道、产品结构或其他未观察字段。"
                        ),
                        how_to_reuse=(
                            f"下次看到数据中同时有类别字段（如地区、品类、渠道）和数值字段（如销售额、成本、数量）时，"
                            f"可以按类别字段分组，对数值字段做 sum / mean / count 聚合，再比较 Top 和 Bottom 的差距。"
                        ),
                    ))
            except Exception as e:
                risk_list.append(risk_check(
                    check=f"Ranking analysis failed for {cat_col} × {num_col}",
                    status="warn",
                    detail=f"Groupby/sort failed: {e}",
                    affected_analysis=f"Ranking table for {cat_col} × {num_col}",
                ))

    # ── Trend Analysis (date + numeric) ──
    for date_col in date_cols[:1]:
        for num_col in numeric_cols[:1]:
            try:
                df_time = df.copy()
                df_time["_period"] = df_time[date_col].dt.to_period("M").astype(str)
                trend = df_time.groupby("_period")[num_col].sum().reset_index()
                trend.columns = ["期间", num_col]
                tables.append(table_sheet(
                    name=f"{num_col}趋势",
                    headers=list(trend.columns),
                    data=[[round(v, 2) if isinstance(v, float) else v for v in row]
                          for row in trend.values],
                ))
                if len(trend) >= 2:
                    first_val = trend[num_col].iloc[0]
                    last_val = trend[num_col].iloc[len(trend) - 1]
                    if first_val != 0:
                        change = (last_val - first_val) / first_val * 100
                        direction = "增长" if change > 0 else "下降"
                        findings_list.append(finding(
                            title=f"{num_col} {direction}趋势",
                            data_evidence=f"从 {trend['期间'].iloc[0]} 到 {trend['期间'].iloc[-1]}: {first_val:,.2f} → {last_val:,.2f} ({change:+.1f}%)",
                            business_interpretation=f"{num_col} 在观察期内{direction}。需结合业务背景判断这是季节性波动还是结构性变化。",
                            suggested_action=f"持续监控{direction}趋势，关注异常月份并定位驱动因素。",
                            metric_to_track=f"月度 {num_col} 同比增长率",
                            what_it_cannot_prove=(
                                f"趋势分析描述的是过去一段时间内 {num_col} 的变化方向，"
                                f"不等于预测未来，也不能单独证明变化由某个具体原因导致。"
                            ),
                            how_to_reuse=(
                                f"下次看到数据中有日期字段和数值指标字段时，可以先把日期转换为月度/周度周期，"
                                f"再按周期汇总数值指标，观察业务是上升、下降还是波动。"
                            ),
                        ))
            except Exception as e:
                risk_list.append(risk_check(
                    check=f"Trend analysis failed for {date_col} × {num_col}",
                    status="warn",
                    detail=f"Date grouping/sorting failed: {e}",
                    affected_analysis=f"Trend table for {num_col} by {date_col}",
                ))

    # ── Distribution analysis for key numeric fields ──
    for num_col in numeric_cols[:2]:
        try:
            desc = df[num_col].describe().reset_index()
            desc.columns = ["统计量", num_col]
            dist_data = []
            for _, drow in desc.iterrows():
                vals = list(drow)
                if isinstance(vals[1], float):
                    vals[1] = round(vals[1], 2)
                dist_data.append(vals)
            tables.append(table_sheet(
                name=f"{num_col}分布",
                headers=list(desc.columns),
                data=dist_data,
            ))
        except Exception as e:
            risk_list.append(risk_check(
                check=f"Distribution analysis failed for {num_col}",
                status="warn",
                detail=f"describe() failed: {e}",
                affected_analysis=f"Distribution statistics for {num_col}",
            ))

    # ── Thinking Models ──
    # Build human-readable dimension/method labels for evidence text
    _dim_names = [_col_meaning.get(c, c) for c in cat_cols[:3]]
    _metric_names = [_col_meaning.get(c, c) for c in numeric_cols[:3]]
    _dim_label = ", ".join(_dim_names) if _dim_names else "可用分类维度"
    _metric_label = ", ".join(_metric_names) if _metric_names else "可用数值指标"

    models_list.append(thinking_model(
        model_name="1. 分解思维 (Decomposition)",
        evidence=f"将数据按照 {_dim_label} 等维度拆解分析。各分组间的 {_metric_label} 存在显著差异，整体指标无法反映细分表现。",
        takeaway="永远先拆解再下结论。汇总指标会隐藏关键的分组差异。",
    ))
    models_list.append(thinking_model(
        model_name="2. 分层差异 (Segment Divergence)",
        evidence=f"数据集包含 {len(cat_cols)} 个分类维度（{_dim_label}）。各维度下的分组均值差异倍数可达数倍甚至数十倍。",
        takeaway="不要相信平均值。检查分组间的差异倍数，差异越大，平均值越具有误导性。",
    ))
    models_list.append(thinking_model(
        model_name="3. 间接推断 (Proxy Inference)",
        evidence=f"{len(numeric_cols)} 个数值字段（含 {_metric_label}）中，部分字段可作为业务健康度的代理指标。没有直接的数据时，用可观察的指标间接推断。",
        takeaway="选择合适的代理变量，比等待完美数据更重要。",
    ))
    models_list.append(thinking_model(
        model_name="4. 杠杆点识别 (Leverage Point)",
        evidence=f"通过按 {_dim_label} 分组排名分析，识别出高贡献/高差异的分组。这些分组同时具备\"影响面广\"和\"改善空间大\"两个特点。",
        takeaway="聚焦高份额 + 高差异的分组，资源投入产出比最高。",
    ))
    models_list.append(thinking_model(
        model_name="5. 约束 vs 偏好 (Constraint vs Preference)",
        evidence="分组间的差异可能是结构性约束（用户无法选择）或偏好（用户主动选择）导致。需要结合业务背景判断。",
        takeaway="约束型问题需要改变产品/流程；偏好型问题需要改变营销/定位。诊断清楚再行动。",
    ))

    # ── Recommendations ──
    if findings_list:
        recs_list.append(recommendation(
            title="优先关注 Top-Bottom 差距大的维度",
            action="对排名靠前和靠后的分组分别分析，找出最佳实践和问题根因。将成功经验横向复制。",
            metric_to_track="分组间的差距倍数变化",
            data_needed="细分到分组的详细数据",
        ))
    recs_list.append(recommendation(
        title="建立定期监控机制",
        action="对核心数值字段建立定期（周/月）监控，及时发现异常波动。",
        metric_to_track="核心指标的环比和同比增长率",
        data_needed="连续时间序列数据",
    ))
    if risk_list:
        recs_list.append(recommendation(
            title="数据质量改进",
            action=f"处理发现的 {len(risk_list)} 个数据质量问题，包括异常值和缺失值。建立数据校验规则。",
            metric_to_track="数据质量评分（完全率 + 准确率）",
            data_needed="数据质量审计报告",
        ))

    return {
        "tables": tables,
        "findings": findings_list,
        "thinking_models": models_list,
        "recommendations": recs_list,
        "risk_checks": risk_list,
    }
