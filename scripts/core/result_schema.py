"""
Standard Result Schema

All analysis modules must return a dict matching this schema.
All renderers (excel, pdf) consume this schema.

This is the contract between analysis logic and output generation.
"""

RESULT_SCHEMA_VERSION = "0.2.0"

def make_empty_report() -> dict:
    """Return a fully-empty report skeleton with all fields."""
    return {
        # Metadata
        "schema_version": RESULT_SCHEMA_VERSION,
        "title": "",
        "dataset_path": "",
        "analysis_mode": "audit_report",  # beginner_summary | standard_report | audit_report
        "language": "zh",

        # Step 1: Dataset Overview (from data_intake)
        "dataset_overview": {
            "file_name": "",
            "rows": 0,
            "columns": 0,
            "fields": [],        # list of field names
            "field_types": {},   # {field_name: pandas_dtype_str}
            "has_missing": False,
            "missing_summary": [],  # [{field, missing_count, missing_pct}]
            "duplicate_rows": 0,
            "time_range": "",    # "2020-01 ~ 2023-12"
        },

        # Step 2: Field Semantics
        "field_semantics": [],  # [{field, inferred_meaning, confidence, evidence}]

        # Step 3: Data Quality
        "data_quality": {
            "risk_checks": [],  # [{check, status, detail, affected_analysis}]
        },

        # Step 4: Metric Glossary
        "metric_glossary": [],  # [{name, full_name, meaning, formula, current_value, business_use, limitation}]

        # Step 5: Key Findings
        "key_findings": [],     # [{title, data_evidence, business_interpretation, suggested_action, metric_to_track}]

        # Step 6: Thinking Models (always 5)
        "thinking_models": [],  # [{model_name, evidence, takeaway}]

        # Step 7: Recommendations
        "recommendations": [],  # [{title, action, metric_to_track, data_needed}]

        # Step 8: Raw Data Tables (for Excel sheets)
        "tables": [],           # [{name, data: [[...]], headers: [...]}]

        # Step 9: Beginner Notes
        "beginner_notes": {
            "concepts_learned": [],
            "methods_learned": [],
            "metrics_learned": [],
            "thinking_patterns": [],
            "next_time_steps": [],            # reusable workflow for similar datasets
            "conclusions_not_to_overinterpret": [],  # caveats
        },
    }


# ── Helper constructors ──

def finding(title, data_evidence, business_interpretation, suggested_action, metric_to_track="",
            what_it_cannot_prove="", how_to_reuse=""):
    return {
        "title": title,
        "data_evidence": data_evidence,
        "business_interpretation": business_interpretation,
        "suggested_action": suggested_action,
        "metric_to_track": metric_to_track,
        "what_it_cannot_prove": what_it_cannot_prove,
        "how_to_reuse": how_to_reuse,
    }


def thinking_model(model_name, evidence, takeaway):
    return {
        "model_name": model_name,
        "evidence": evidence,
        "takeaway": takeaway,
    }


def recommendation(title, action, metric_to_track, data_needed):
    return {
        "title": title,
        "action": action,
        "metric_to_track": metric_to_track,
        "data_needed": data_needed,
    }


def metric_entry(name, full_name, meaning, formula, current_value, business_use, limitation=""):
    return {
        "name": name,
        "full_name": full_name,
        "meaning": meaning,
        "formula": formula,
        "current_value": current_value,
        "business_use": business_use,
        "limitation": limitation,
    }


def field_semantic(field, inferred_meaning, confidence, evidence=""):
    return {
        "field": field,
        "inferred_meaning": inferred_meaning,
        "confidence": confidence,  # "high" | "medium" | "low"
        "evidence": evidence,
    }


def risk_check(check, status, detail, affected_analysis=""):
    return {
        "check": check,
        "status": status,  # "pass" | "warn" | "fail"
        "detail": detail,
        "affected_analysis": affected_analysis,
    }


def table_sheet(name, headers, data):
    """A 2D table for Excel rendering. data is list of lists."""
    return {
        "name": name,
        "headers": headers,
        "data": data,
    }
