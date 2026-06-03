"""
Audit Logger

Builds and saves an audit log JSON for each analysis run.
Records what was executed, what was skipped, and why.

This is a lightweight Phase 1 implementation — post-hoc inference
from the report dict rather than inline instrumentation.
"""

import json
import os
from datetime import datetime

import numpy as np

from .metric_registry import METRIC_REGISTRY
from .result_schema import RESULT_SCHEMA_VERSION


def _to_json_safe(obj):
    """Recursively convert numpy/pandas types to JSON-serializable Python types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, np.ndarray):
        return [_to_json_safe(v) for v in obj.tolist()]
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_json_safe(v) for v in obj]
    if hasattr(obj, "isoformat"):  # covers datetime, Timestamp
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(list(obj))
    if isinstance(obj, (bool, int, float, str, type(None))):
        return obj
    return str(obj)


def _infer_executed_methods(report: dict, df_columns: set = None) -> list:
    """Infer which analysis methods were executed based on report contents."""
    methods = []
    table_names = [t["name"] for t in report.get("tables", [])]
    field_semantics = report.get("field_semantics", [])

    date_fields = [s["field"] for s in field_semantics
                   if s["inferred_meaning"] in ("Date field", "Time field")]
    cat_fields = [s["field"] for s in field_semantics
                  if s["inferred_meaning"] in (
                      "Category / department", "Type / classification",
                      "Geographic region", "Age group / demographic",
                      "Gender", "Contract / plan type")]

    # Risk check
    if report.get("data_quality", {}).get("risk_checks"):
        methods.append({
            "method_name": "data_quality_risk_check",
            "trigger_condition": "Always executed",
            "used_fields": [],
            "output": f"{len(report['data_quality']['risk_checks'])} risk(s) detected",
        })

    # Grouped ranking
    ranking_tables = [t for t in table_names if "看" in t or "合计" in str(report.get("tables", []))]
    if ranking_tables:
        cat_str = ", ".join(cat_fields[:3]) if cat_fields else "(auto-detected)"
        methods.append({
            "method_name": "grouped_ranking_analysis",
            "trigger_condition": f"Categorical field(s) exist: {cat_str}",
            "used_fields": cat_fields[:3],
            "output": f"{len(ranking_tables)} ranking table(s) generated",
        })

    # Trend analysis
    trend_tables = [t for t in table_names if "趋势" in t]
    if trend_tables:
        date_str = ", ".join(date_fields[:1]) if date_fields else "(auto-detected)"
        methods.append({
            "method_name": "trend_analysis",
            "trigger_condition": f"Date field exists: {date_str}",
            "used_fields": date_fields[:1],
            "output": f"{len(trend_tables)} trend table(s) generated",
        })

    # Distribution analysis
    dist_tables = [t for t in table_names if "分布" in t]
    if dist_tables:
        methods.append({
            "method_name": "distribution_analysis",
            "trigger_condition": "Numeric field(s) exist",
            "used_fields": [],
            "output": f"{len(dist_tables)} distribution table(s) generated",
        })

    return methods


def _infer_skipped_methods(report: dict, df_columns: set = None) -> list:
    """Infer which methods were NOT executed and why."""
    skipped = []
    table_names = [t["name"] for t in report.get("tables", [])]
    field_semantics = report.get("field_semantics", [])

    has_date = any(
        s["inferred_meaning"] in ("Date field", "Time field")
        for s in field_semantics
    )
    has_cat = df_columns is not None and any(
        s["inferred_meaning"] in (
            "Category / department", "Type / classification",
            "Geographic region", "Age group / demographic",
            "Gender", "Contract / plan type")
        for s in field_semantics
    )

    if not has_date:
        skipped.append({
            "method_name": "trend_analysis",
            "required_condition": "A datetime column must exist in the dataset",
            "reason": "No date/time field detected",
        })

    if not has_cat:
        skipped.append({
            "method_name": "grouped_ranking_analysis",
            "required_condition": "At least one categorical field with 2-50 unique values",
            "reason": "No suitable categorical field detected",
        })

    return skipped


def _infer_skipped_metrics(df_columns: set) -> list:
    """Check which metrics in the registry could NOT be matched."""
    skipped = []
    for metric in METRIC_REGISTRY:
        matched = [f for f in metric["field_priority"] if f in df_columns]
        if not matched:
            skipped.append({
                "metric_name": metric["name"],
                "required_fields": list(metric["required_fields"]),
                "missing_fields": list(metric["required_fields"]),
                "reason": "No matching field found in dataset",
            })
    return skipped


def build_audit_log(report: dict, input_path: str, output_dir: str = None,
                    base_name: str = None, args=None,
                    df_columns: list = None) -> dict:
    """
    Build a structured audit log from the report and available metadata.

    Parameters
    ----------
    report : dict
        The full report dict built by build_report().
    input_path : str
        Original input path.
    output_dir : str, optional
        The actual output directory where files are written (timestamped subdirectory).
    base_name : str, optional
        Base filename used for all output files.
    args : argparse.Namespace, optional
        CLI arguments (for flags like no_excel and no_pdf).
    df_columns : list, optional
        Original DataFrame column names (for skipped-metric inference).
    """
    overview = report.get("dataset_overview", {})
    data_quality = report.get("data_quality", {})
    risks = data_quality.get("risk_checks", [])

    cols_set = set(df_columns) if df_columns else set(overview.get("fields", []))

    executed = _infer_executed_methods(report, cols_set)
    skipped_methods = _infer_skipped_methods(report, cols_set)
    skipped_metrics = _infer_skipped_metrics(cols_set) if cols_set else []

    # Use the real output_dir and base_name for accurate file paths
    out_dir = output_dir or getattr(args, "output_dir", "output") if args else "output"
    bn = base_name or os.path.splitext(os.path.basename(input_path))[0]
    no_excel = getattr(args, "no_excel", False) if args else False
    no_pdf = getattr(args, "no_pdf", False) if args else False
    outputs = [
        {"type": "excel", "path": os.path.abspath(os.path.join(out_dir, f"{bn}_analysis.xlsx")),
         "status": "skipped" if no_excel else "generated"},
        {"type": "html", "path": os.path.abspath(os.path.join(out_dir, f"{bn}_report.html")),
         "status": "skipped" if no_pdf else "generated"},
        {"type": "pdf", "path": os.path.abspath(os.path.join(out_dir, f"{bn}_report.pdf")),
         "status": "skipped" if no_pdf else "generated"},
    ]

    # Risk detail
    risk_detail = []
    for r in risks:
        risk_detail.append({
            "risk_type": r.get("check", ""),
            "field": r.get("check", "").replace("Negative values in ", "").replace("Missing values in ", "").replace("High zero-rate in ", ""),
            "severity": r.get("status", "warn"),
            "evidence": r.get("detail", ""),
            "suggestion": r.get("affected_analysis", ""),
        })

    log = {
        "schema_version": "0.1.0",
        "result_schema_version": RESULT_SCHEMA_VERSION,
        "input_file": os.path.abspath(input_path),
        "run_timestamp": datetime.now().isoformat(),
        "analysis_mode": report.get("analysis_mode", ""),
        "output_directory": os.path.abspath(out_dir),
        "dataset_profile": {
            "rows": overview.get("rows", 0),
            "columns": overview.get("columns", 0),
            "field_names": overview.get("fields", []),
            "field_types": overview.get("field_types", {}),
            "missing_values": {
                m["field"]: {"count": m["missing_count"], "pct": m["missing_pct"]}
                for m in overview.get("missing_summary", [])
            },
            "duplicate_rows": overview.get("duplicate_rows", 0),
            "time_range": overview.get("time_range", ""),
        },
        "field_semantics": [
            {
                "field": s["field"],
                "inferred_meaning": s["inferred_meaning"],
                "confidence": s["confidence"],
                "matched_rule": s.get("evidence", ""),
            }
            for s in report.get("field_semantics", [])
        ],
        "matched_metrics": [
            {
                "metric_name": m["name"],
                "formula": m.get("formula", ""),
                "used_fields": [],
                "current_value": m.get("current_value", ""),
            }
            for m in report.get("metric_glossary", [])
        ],
        "skipped_metrics": skipped_metrics,
        "executed_methods": executed,
        "skipped_methods": skipped_methods,
        "data_quality_risks": risk_detail,
        "output_files": outputs,
    }

    return log


def save_audit_log(audit_log: dict, output_dir: str, base_name: str) -> str:
    """
    Save the audit log as a JSON file.

    Returns the full path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{base_name}_audit_log.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(_to_json_safe(audit_log), f, ensure_ascii=False, indent=2)
    return file_path
