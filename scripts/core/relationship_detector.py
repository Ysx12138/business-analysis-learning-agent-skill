"""
Relationship Detector Module

Detects relationships between multiple tables (CSV files in a folder)
and generates a safe join plan.
"""
import os
import pandas as pd
from .data_intake import load_dataset, profile


def _detect_key_likelihood(series: pd.Series) -> str:
    """
    Determine if a column is likely a primary key, foreign key, or regular field.
    """
    name = str(series.name).lower()
    nunique = series.nunique()
    total = len(series)

    # By naming convention
    if name == "id" or name.endswith("_id"):
        # PK if high cardinality and all unique
        if nunique == total:
            return "primary_key"
        return "foreign_key"

    if name.startswith("id_") or name.endswith("_key"):
        if nunique == total:
            return "primary_key"
        return "foreign_key"

    # By data characteristics (high-cardinality numeric/text likely an ID)
    if nunique / total > 0.9 and nunique > 10:
        return "likely_id"

    return "regular"


def _detect_join_keys(tables: dict) -> list:
    """
    Given a dict of {name: DataFrame}, find all possible join keys.

    Returns a list of dicts:
      [{table_a, table_b, key_a, key_b, match_ratio, relationship}]
    """
    table_names = list(tables.keys())
    candidates = []

    for i in range(len(table_names)):
        for j in range(i + 1, len(table_names)):
            name_a = table_names[i]
            name_b = table_names[j]
            df_a = tables[name_a]
            df_b = tables[name_b]

            # Find shared column names
            shared_cols = set(df_a.columns) & set(df_b.columns)

            for col in shared_cols:
                values_a = set(df_a[col].dropna().unique())
                values_b = set(df_b[col].dropna().unique())

                if not values_a or not values_b:
                    continue

                overlap = values_a & values_b
                ratio_a = len(overlap) / len(values_a) if values_a else 0
                ratio_b = len(overlap) / len(values_b) if values_b else 0

                # Check key uniqueness: many_to_many if BOTH sides have duplicates
                unique_a = df_a[col].nunique() / len(df_a)
                unique_b = df_b[col].nunique() / len(df_b)

                # Determine relationship type
                if ratio_a >= 0.8 and ratio_b >= 0.8:
                    # High overlap in both directions → same value domain
                    if unique_a == 1.0 and unique_b == 1.0:
                        relationship = "one_to_one"
                    elif unique_a < 1.0 and unique_b == 1.0:
                        relationship = "many_to_one"
                    elif unique_a == 1.0 and unique_b < 1.0:
                        relationship = "one_to_many"
                    else:
                        # Both sides have duplicates → many-to-many explosion risk
                        relationship = "many_to_many"
                elif ratio_a >= 0.8:
                    relationship = "many_to_one"
                elif ratio_b >= 0.8:
                    relationship = "one_to_many"
                else:
                    continue

                candidates.append({
                    "table_a": name_a,
                    "table_b": name_b,
                    "key": col,
                    "overlap_a_pct": round(ratio_a * 100, 1),
                    "overlap_b_pct": round(ratio_b * 100, 1),
                    "relationship": relationship,
                    "rows_a": len(df_a),
                    "rows_b": len(df_b),
                    "estimated_join_rows": _estimate_join_rows(
                        df_a, df_b, col, relationship
                    ),
                })

    # Sort by strongest relationship (highest overlap)
    candidates.sort(key=lambda c: max(c["overlap_a_pct"], c["overlap_b_pct"]), reverse=True)

    # ── Also detect compound keys (column pairs) for tables with no good single-column join ──
    compound = _detect_compound_keys(tables, candidates)
    candidates.extend(compound)
    return candidates


def _detect_compound_keys(tables: dict, single_col_candidates: list) -> list:
    """
    After single-column key detection, check column pairs as compound keys.

    This handles cases like (Store, Date) where neither column alone is unique
    but together they form a valid join key.
    """
    table_names = list(tables.keys())
    compound_candidates = []

    for i in range(len(table_names)):
        for j in range(i + 1, len(table_names)):
            name_a = table_names[i]
            name_b = table_names[j]

            df_a = tables[name_a]
            df_b = tables[name_b]

            # Find shared columns (need at least 2)
            shared = list(set(df_a.columns) & set(df_b.columns))
            if len(shared) < 2:
                continue

            # Try column pairs as compound keys
            for ci in range(len(shared)):
                for cj in range(ci + 1, len(shared)):
                    col_i = shared[ci]
                    col_j = shared[cj]

                    # Skip if either column is boolean or near-boolean (< 3 unique)
                    if df_a[col_i].nunique() < 3 or df_a[col_j].nunique() < 3:
                        continue

                    # Build compound key sets (drop rows where either key is null)
                    mask_a = df_a[col_i].notna() & df_a[col_j].notna()
                    mask_b = df_b[col_i].notna() & df_b[col_j].notna()
                    keys_a = set(zip(df_a.loc[mask_a, col_i], df_a.loc[mask_a, col_j]))
                    keys_b = set(zip(df_b.loc[mask_b, col_i], df_b.loc[mask_b, col_j]))

                    if not keys_a or not keys_b:
                        continue

                    overlap = keys_a & keys_b
                    ratio_a = len(overlap) / len(keys_a) if keys_a else 0
                    ratio_b = len(overlap) / len(keys_b) if keys_b else 0

                    if ratio_a < 0.7 or ratio_b < 0.7:
                        continue  # not enough overlap

                    # Compound uniqueness (sets already deduped)
                    unique_a = len(keys_a) / len(df_a)
                    unique_b = len(keys_b) / len(df_b)

                    if unique_a >= 0.9 and unique_b >= 0.9:
                        relationship = "one_to_one"
                    elif unique_a < 0.9 and unique_b >= 0.9:
                        relationship = "many_to_one"
                    elif unique_a >= 0.9 and unique_b < 0.9:
                        relationship = "one_to_many"
                    else:
                        relationship = "many_to_many"

                    compound_key = f"{col_i} + {col_j}"
                    compound_candidates.append({
                        "table_a": name_a,
                        "table_b": name_b,
                        "key": compound_key,
                        "key_columns": [col_i, col_j],
                        "overlap_a_pct": round(ratio_a * 100, 1),
                        "overlap_b_pct": round(ratio_b * 100, 1),
                        "relationship": relationship,
                        "rows_a": len(df_a),
                        "rows_b": len(df_b),
                        "estimated_join_rows": _estimate_join_rows(
                            df_a, df_b, compound_key, relationship
                        ),
                        "is_compound": True,
                    })

    return compound_candidates


def _estimate_join_rows(df_a, df_b, key, relationship) -> int:
    """Estimate row count after join (for risk detection)."""
    # key can be a column name or a compound key string like "col_a + col_b"
    # For compound keys, use the first column as a rough estimate
    if relationship == "one_to_one":
        return max(len(df_a), len(df_b))
    elif relationship == "many_to_one":
        return len(df_a)
    elif relationship == "one_to_many":
        return len(df_b)
    # many_to_many: estimate using first column cardinality
    col = key.split(" + ")[0] if isinstance(key, str) else key[0]
    nunique = max(df_a[col].nunique(), 1)
    return len(df_a) * len(df_b) // nunique


class JoinRisk:
    SAFE = "safe"
    MODERATE = "moderate"
    HIGH = "high"


def detect_relationships(tables: dict) -> dict:
    """
    Main entry point. Takes {table_name: DataFrame} and returns a full analysis.

    Returns:
    {
        "tables": [{name, rows, cols, fields}],
        "join_candidates": [{table_a, table_b, key, overlap_a_pct, overlap_b_pct, relationship, estimated_join_rows, risk}],
        "profiles": {name: profile_dict},
    }
    """
    # Profile each table
    profiles = {}
    for name, df in tables.items():
        profiles[name] = {
            "name": name,
            "rows": len(df),
            "columns": len(df.columns),
            "fields": list(df.columns),
            "field_types": {c: str(df[c].dtype) for c in df.columns},
            "key_candidates": [c for c in df.columns
                               if _detect_key_likelihood(df[c]) in ("primary_key", "foreign_key", "likely_id")],
        }

    # Find join keys
    join_candidates = _detect_join_keys(tables)
    for jc in join_candidates:
        risk = JoinRisk.SAFE
        est = jc["estimated_join_rows"]
        max_rows = max(jc["rows_a"], jc["rows_b"])
        if est > max_rows * 5:
            risk = JoinRisk.HIGH
        elif est > max_rows * 2:
            risk = JoinRisk.MODERATE
        jc["risk"] = risk

    return {
        "tables": profiles,
        "join_candidates": join_candidates,
    }


def _is_id_key(key: str) -> bool:
    """Check if a column is likely a real foreign/primary key (not a low-cardinality attribute)."""
    name = key.lower()
    return name.endswith("_id") or name.endswith("_key") or name == "id"


def build_join_plan(relationships: dict) -> list:
    """
    Build an efficient join plan using only ID-based keys.

    Greedy algorithm:
      - Filter to real foreign keys (ending in _id, _key)
      - Pick the most-connected table as anchor
      - Each table is joined at most once
      - Only strongest join per table pair is kept

    Returns a list of join steps:
      [{step, table_a, table_b, key, join_type, risk}]
    """
    candidates = relationships.get("join_candidates", [])
    if not candidates:
        return []

    # ── Build candidate pool ──
    # 1. ID-based keys (account_id, subscription_id, etc.)
    # 2. Non-ID keys with safe relationship types (one_to_many, many_to_one, one_to_one)
    #    that are not high-risk and not boolean/low-cardinality flags
    id_joins = [c for c in candidates if _is_id_key(c["key"])]
    _safe_rels = {"one_to_many", "many_to_one", "one_to_one"}
    non_id_joins = [
        c for c in candidates if not _is_id_key(c["key"])
        and c["risk"] != JoinRisk.HIGH
        and c["relationship"] in _safe_rels
        and (c["overlap_a_pct"] >= 50 or c["overlap_b_pct"] >= 80)
    ]

    # Combine: prefer ID keys, fall back to safe non-ID joins
    pool = id_joins + non_id_joins if id_joins else non_id_joins

    if not pool:
        return []

    # ── Count connections per table ──
    conn = {}
    for c in pool:
        conn[c["table_a"]] = conn.get(c["table_a"], 0) + 1
        conn[c["table_b"]] = conn.get(c["table_b"], 0) + 1

    # Pick anchor: the table with the most connections
    anchor = max(conn, key=conn.get)

    # ── Sort: compound keys first (more selective), then by overlap ──
    pool.sort(key=lambda c: (
        0 if c.get("is_compound") else 1,
        -(c["overlap_a_pct"] + c["overlap_b_pct"]),
    ))

    # ── Greedy each-table-once plan ──
    plan = []
    joined = {anchor}
    step = 0
    changed = True
    while changed:
        changed = False
        for c in pool:
            a_in = c["table_a"] in joined
            b_in = c["table_b"] in joined

            if a_in and b_in:
                continue          # both already in the merged result
            if not a_in and not b_in:
                continue          # neither is reachable yet

            step += 1
            # source = the table already in merged, target = new table
            if a_in and not b_in:
                source, target = c["table_a"], c["table_b"]
            else:
                source, target = c["table_b"], c["table_a"]

            entry = {
                "step": step,
                "table_a": source,
                "table_b": target,
                "key": c["key"],
                "join_type": "left",
                "risk": c["risk"],
                "note": f"Join {source} → {target} on {c['key']}. Estimated rows: {c['estimated_join_rows']:,}",
            }
            if c.get("is_compound"):
                entry["key_columns"] = c.get("key_columns", [])
            if c["risk"] == JoinRisk.HIGH:
                entry["join_type"] = "SKIPPED (high risk)"
                entry["risk"] = "high"
                entry["note"] = f"High risk join — {source} ↔ {target} on {c['key']}. Estimated {c['estimated_join_rows']:,} rows. Manual review needed."
            plan.append(entry)

            joined.add(target)
            changed = True

    return plan


def execute_join_plan(tables: dict, plan: list) -> pd.DataFrame:
    """
    Execute a join plan and return the merged DataFrame.

    First step: merge tables[table_a] with tables[table_b].
    Subsequent steps: merge running result with tables[table_b] (the new table).
    If all joins are skipped/fail, falls back to the anchor table.
    """
    if not plan:
        first_name = list(tables.keys())[0]
        return tables[first_name]

    anchor = plan[0]["table_a"]
    merged = None
    for step in plan:
        if step["risk"] == "high":
            print(f"  SKIP: {step['note']}")
            continue

        # First step: read both from tables; subsequent: merged is the left side
        if merged is None:
            df_a = tables[step["table_a"]]
        else:
            df_a = merged

        df_b = tables[step["table_b"]]
        key = step["key"]
        key_cols = step.get("key_columns", key)  # list for compound, str for single

        # Check for column name conflicts beyond the key
        cols_a = set(df_a.columns)
        cols_b = set(df_b.columns)
        conflict_cols = (cols_a & cols_b) - ({key} if isinstance(key, str) else set(key_cols))

        if conflict_cols:
            suffix_a = f"_{step['table_a']}"
            suffix_b = f"_{step['table_b']}"
            new_merged = df_a.merge(df_b, on=key_cols, how=step["join_type"],
                                    suffixes=(suffix_a, suffix_b))
        else:
            new_merged = df_a.merge(df_b, on=key_cols, how=step["join_type"])

        # Sanity check: if rows blow up >50x the larger input, skip this join
        max_input = max(len(df_a), len(df_b))
        if len(new_merged) > max_input * 50:
            print(f"  SKIP: Step {step['step']} blew up ({len(new_merged):,} rows vs {max_input:,} max input). "
                  f"Key '{key}' is not selective enough after prior joins.")
            if merged is None:
                merged = df_a  # keep the left table as-is
            continue

        merged = new_merged
        print(f"  JOIN: {step['note']} -> {len(merged)} rows")

    return merged if merged is not None else tables[anchor]


def load_folder(path: str) -> dict:
    """
    Load all CSV and Excel files from a folder into a {name: DataFrame} dict.
    """
    tables = {}
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")

    for fname in sorted(os.listdir(path)):
        if fname.startswith("."):
            continue
        fpath = os.path.join(path, fname)
        if fname.endswith(".csv") or fname.endswith(".xlsx") or fname.endswith(".xls"):
            name = os.path.splitext(fname)[0]
            tables[name] = load_dataset(fpath)
            print(f"  Loaded: {fname} ({len(tables[name]):,} rows, {len(tables[name].columns)} cols)")

    if not tables:
        raise ValueError(f"No CSV or Excel files found in: {path}")

    return tables
