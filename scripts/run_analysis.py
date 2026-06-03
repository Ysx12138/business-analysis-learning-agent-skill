#!/usr/bin/env python3
"""
Universal Analysis Runner — v0.6.2 (Multi-Table)

Usage:
    # Single file
    python scripts/run_analysis.py --input path/to/data.csv --mode audit_report

    # Multi-table folder
    python scripts/run_analysis.py --input path/to/folder/ --mode audit_report

Loads CSV/Excel, profiles, detects relationships (multi-table),
analyzes, and generates Excel + PDF.
"""
import argparse
import os
import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.metric_registry import METRIC_REGISTRY

from scripts.core import result_schema
from scripts.core.data_intake import load_dataset, profile
from scripts.core.field_semantics import infer_semantics
from scripts.core.metric_registry import find_matching_metrics, detect_derived_metrics
from scripts.core.analysis_planner import plan_analysis
from scripts.core.relationship_detector import detect_relationships, build_join_plan, execute_join_plan, load_folder
from scripts.core.audit_logger import build_audit_log, save_audit_log
from scripts.renderers import excel_renderer, html_report_renderer, pdf_renderer


def _is_folder(path: str) -> bool:
    return os.path.isdir(path)


def build_report(df, input_path: str, mode: str, title: str = "",
                 relationships: dict = None, join_plan: list = None) -> dict:
    """Build a complete report dict from a DataFrame."""
    report = result_schema.make_empty_report()
    report["title"] = title or f"Analysis Report — {os.path.basename(input_path)}"
    report["dataset_path"] = input_path
    report["analysis_mode"] = mode
    report["language"] = "zh"

    # Step 1: Dataset Overview
    report["dataset_overview"] = profile(df, file_name=input_path)

    # Step 2: Field Semantics
    report["field_semantics"] = infer_semantics(df)

    # Step 3: Metrics
    metrics = find_matching_metrics(df)
    derived = detect_derived_metrics(df)
    report["metric_glossary"] = metrics + derived

    # Step 4: Analysis (pass field semantics for human-readable evidence text)
    analysis_results = plan_analysis(df, field_semantics=report.get("field_semantics"))
    report["tables"] = analysis_results["tables"]
    report["key_findings"] = analysis_results["findings"]
    report["thinking_models"] = analysis_results["thinking_models"]
    report["recommendations"] = analysis_results["recommendations"]
    report["data_quality"]["risk_checks"] = analysis_results["risk_checks"]

    # Multi-table relationship info
    if relationships:
        # Add a table showing the relationship structure
        tbl_data = []
        for name, tbl in relationships.get("tables", {}).items():
            tbl_data.append([
                tbl["name"], tbl["rows"], tbl["columns"],
                ", ".join(tbl.get("key_candidates", [])[:5]),
            ])
        report["tables"].insert(0, result_schema.table_sheet(
            name="数据表关系",
            headers=["表名", "行数", "列数", "候选键"],
            data=tbl_data,
        ))

        # Add join candidates info
        join_data = []
        for jc in relationships.get("join_candidates", []):
            join_data.append([
                jc["table_a"], jc["table_b"], jc["key"],
                jc["relationship"], f"{jc['overlap_a_pct']}% / {jc['overlap_b_pct']}%",
                jc.get("risk", "safe"),
            ])
        if join_data:
            report["tables"].append(result_schema.table_sheet(
                name="关联键检测",
                headers=["表A", "表B", "关联键", "关系类型", "重叠率(A/B)", "风险"],
                data=join_data,
            ))

        # Add join plan info
        if join_plan:
            plan_data = []
            for step in join_plan:
                plan_data.append([
                    f"Step {step['step']}",
                    step["table_a"], step["table_b"], step["key"],
                    step["join_type"], step.get("risk", "?"),
                ])
            if plan_data:
                report["tables"].append(result_schema.table_sheet(
                    name="关联计划",
                    headers=["步骤", "表A", "表B", "键", "关联类型", "风险"],
                    data=plan_data,
                ))

    # ── Mode-based trimming ──
    if mode == "beginner_summary":
        report["tables"] = report["tables"][:3]
        report["key_findings"] = report["key_findings"][:3]
        report["thinking_models"] = report["thinking_models"][:2]
        report["recommendations"] = report["recommendations"][:1]
        # Keep only the most severe risk checks (warn severity)
        report["data_quality"]["risk_checks"] = [
            r for r in report["data_quality"]["risk_checks"]
            if r.get("status") == "warn"
        ][:3]
    elif mode == "standard_report":
        # Keep full analysis output — no trimming
        pass
    # audit_report: keep everything (no trimming)

    # Beginner notes — dynamically derived from actual analysis results
    executed_methods = set()
    for tbl in report["tables"]:
        name = tbl.get("name", "")
        if "按" in name and "看" in name:
            executed_methods.add("分组聚合分析")
        if "趋势" in name:
            executed_methods.add("趋势分析")
        if "分布" in name:
            executed_methods.add("描述性统计分析")
    if report["data_quality"]["risk_checks"]:
        executed_methods.add("数据质量检查")

    if not executed_methods:
        executed_methods = {"分组聚合分析", "描述性统计分析"}

    metric_names = [m["name"] for m in report["metric_glossary"][:5]]

    # Derive learning patterns from thinking models
    thinking_pattern_labels = [tm["model_name"] for tm in report["thinking_models"]]

    # Generate "next time" steps based on what was done
    next_steps = []
    if any("按" in tbl.get("name", "") for tbl in report["tables"]):
        next_steps.append("看到数据中有类别列（如区域、品类）和数值列（如营收、成本），先做分组排名分析")
    if any("趋势" in tbl.get("name", "") for tbl in report["tables"]):
        next_steps.append("看到数据中有日期列，先按月汇总看趋势方向")
    if report["dataset_overview"].get("has_missing"):
        next_steps.append("检查缺失值比例，判断缺失是否携带业务含义")
    next_steps.append("不要只看总量——拆开看分组差异，总量会隐藏关键信息")

    report["beginner_notes"] = {
        "concepts_learned": ["业务指标的定义和计算口径", "数据质量对分析结论的影响"],
        "methods_learned": sorted(executed_methods),
        "metrics_learned": metric_names,
        "thinking_patterns": thinking_pattern_labels,
        "next_time_steps": next_steps,
        "conclusions_not_to_overinterpret": [
            "趋势分析描述过去，不等于预测未来",
            "分组差异不等于因果关系（如：区域差异不一定说明区域导致了营收差异）",
            "高营收不等于高利润，需要结合成本数据综合判断",
            "样本量太小时（<30条），统计结论不稳定",
        ],
    }

    return report


def _normalize_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Post-merge column normalization: rename suffixed metric columns back to base names.

    When execute_join_plan merges tables, shared columns get suffixed
    (e.g., churn_flag → churn_flag_ravenstack_subscriptions). This breaks
    metric_registry which looks for exact field names. This function
    detects such cases and creates base-name columns by coalescing values.
    """
    # Collect all metric-relevant field names from registry + derived metrics
    metric_fields = set()
    for m in METRIC_REGISTRY:
        metric_fields.update(m["required_fields"])
    # Derived metric field bases
    metric_fields.update({
        "Clicks", "clicks", "Impressions", "impressions",
        "Spent", "spent", "spend",
        "Total_Revenue", "total_revenue", "revenue", "Sales",
        "Net_Income", "net_income", "profit",
        "Total_Liabilities", "total_liabilities",
        "Total_Assets", "total_assets",
        "Total_Conversion", "Conversions", "conversions",
        "churn_flag", "Churn", "churn",
        "rating", "Rating",
    })

    df = df.copy()
    cols = list(df.columns)

    for base in sorted(metric_fields, key=len, reverse=True):
        if base in cols:
            continue  # exact column exists, no fix needed
        # Suffixed match: column starts with "base_" (e.g., churn_flag_ravenstack_xxx)
        matches = [c for c in cols if c.startswith(base + "_")]
        if not matches:
            continue
        # Coalesce values across all suffixed versions
        result = df[matches[0]].copy()
        for m in matches[1:]:
            result = result.fillna(df[m])
        df[base] = result

    return df


def main():
    parser = argparse.ArgumentParser(description="Universal Business Analysis Runner (Multi-Table)")
    parser.add_argument("--input", required=True, help="Path to CSV/Excel file or folder of CSV files")
    parser.add_argument("--mode", default="audit_report",
                        choices=["beginner_summary", "standard_report", "audit_report"],
                        help="Output mode")
    parser.add_argument("--output-dir", required=True, help="Directory for output files (required)")
    parser.add_argument("--title", default="", help="Report title (optional)")
    parser.add_argument("--no-excel", action="store_true", help="Skip Excel generation")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    df = None
    relationships = None
    join_plan = None

    # Determine base_name first, then create timestamped output subdirectory
    if _is_folder(input_path):
        base_name = f"{os.path.basename(input_path)}_merged"
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = os.path.abspath(os.path.join(args.output_dir, f"{base_name}_{ts}"))
    os.makedirs(output_dir, exist_ok=False)
    print(f"\nOutput directory: {output_dir}")

    if _is_folder(input_path):
        # ── Multi-table mode ──
        print(f"Loading folder: {input_path}")
        tables = load_folder(input_path)
        print(f"\nDetecting relationships...")
        relationships = detect_relationships(tables)

        print(f"\nRelationship Summary:")
        for name, tbl in relationships["tables"].items():
            print(f"  {name}: {tbl['rows']:,} rows, {tbl['columns']} cols, keys: {tbl['key_candidates']}")
        for jc in relationships["join_candidates"]:
            print(f"  JOIN: {jc['table_a']}.{jc['key']} ↔ {jc['table_b']}.{jc['key']} "
                  f"({jc['relationship']}, overlap {jc['overlap_a_pct']}%/{jc['overlap_b_pct']}%)")

        join_plan = build_join_plan(relationships)
        print(f"\nJoin Plan:")
        for step in join_plan:
            print(f"  Step {step['step']}: {step['note']}")

        print(f"\nExecuting join plan...")
        df = execute_join_plan(tables, join_plan)
        print(f"  Normalizing metric columns post-merge...")
        df = _normalize_metric_columns(df)
        print(f"  Merged dataset: {len(df):,} rows, {len(df.columns)} cols")
    else:
        # ── Single-file mode ──
        df = load_dataset(input_path)
        print(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")

    print(f"\nBuilding report (mode: {args.mode})...")
    report = build_report(df, input_path, args.mode, title=args.title,
                          relationships=relationships, join_plan=join_plan)

    if not args.no_excel:
        excel_path = os.path.join(output_dir, f"{base_name}_analysis.xlsx")
        print(f"Generating Excel: {excel_path}")
        excel_renderer.render(report, excel_path)
        print(f"  -> {excel_path}")

    if not args.no_pdf:
        pdf_path = os.path.join(output_dir, f"{base_name}_report.pdf")
        html_path = os.path.join(output_dir, f"{base_name}_report.html")
        print(f"Generating HTML report: {html_path}")
        try:
            _, html_out, engine = html_report_renderer.render_pdf(report, pdf_path, html_path=html_path)
            print(f"  -> {html_out}")
            print(f"Generating PDF ({engine}): {pdf_path}")
            print(f"  -> {pdf_path}")
        except Exception as exc:
            print(f"  HTML/CSS PDF renderer unavailable ({exc}); falling back to ReportLab.")
            html_report_renderer.render_html(report, html_path)
            print(f"  -> {html_path}")
            print(f"Generating PDF (reportlab fallback): {pdf_path}")
            pdf_renderer.render(report, pdf_path)
            print(f"  -> {pdf_path}")

    # ── Audit Log ──
    audit_log = build_audit_log(report, input_path, output_dir=output_dir,
                                base_name=base_name, args=args, df_columns=list(df.columns))
    audit_path = save_audit_log(audit_log, output_dir, base_name)
    print(f"Generating Audit Log: {audit_path}")
    print(f"  -> {audit_path}")

    print(f"\n{'='*60}")
    print(f"Report Summary")
    print(f"{'='*60}")
    overview = report["dataset_overview"]
    print(f"Dataset: {overview.get('file_name', 'N/A')}")
    print(f"Records: {overview['rows']:,}  |  Fields: {overview['columns']}")
    print(f"Findings: {len(report['key_findings'])}")
    print(f"Metrics: {len(report['metric_glossary'])}")
    print(f"Tables: {len(report['tables'])}")
    print(f"Risk checks: {len(report['data_quality']['risk_checks'])}")
    if relationships:
        print(f"Source tables: {len(relationships['tables'])}")
        print(f"Join candidates: {len(relationships['join_candidates'])}")
    print(f"{'='*60}")
    print(f"Done at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
