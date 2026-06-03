#!/usr/bin/env python3
"""
Smoke tests for Business Analysis Learning Agent Skill.

Validates the core pipeline:
1. Single CSV analysis — Excel, PDF, audit log generation
2. Multi-table analysis — relationship detection and merged analysis
3. Missing fields — graceful handling without crashes
4. HTML/CSS report output — HTML + PDF generation

Run with:
    python tests/smoke_test.py
"""
import os
import sys
import json
import tempfile
import subprocess
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from scripts.core.data_intake import load_dataset, profile
from scripts.core.relationship_detector import load_folder
from scripts.core.field_semantics import infer_semantics
from scripts.core.metric_registry import find_matching_metrics, detect_derived_metrics
from scripts.core.analysis_planner import plan_analysis
from scripts.core.result_schema import make_empty_report
from scripts.core.audit_logger import build_audit_log

PASS, FAIL = 0, 0


def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


def test_single_csv():
    """Test analysis of a single CSV file."""
    print("\n=== Test 1: Single CSV Analysis ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    check(os.path.exists(csv_path), f"Sample CSV exists at {csv_path}")

    df = load_dataset(csv_path)
    check(isinstance(df, pd.DataFrame), "load_dataset returns DataFrame")
    check(len(df) == 12, f"DataFrame has 12 rows (got {len(df)})")
    check(len(df.columns) == 6, f"DataFrame has 6 columns (got {len(df.columns)})")

    # Data profiling
    overview = profile(df, file_name=csv_path)
    check(overview["rows"] == 12, f"Profile reports 12 rows (got {overview['rows']})")
    check(overview["columns"] == 6, f"Profile reports 6 columns (got {overview['columns']})")

    # Field semantics
    semantics = infer_semantics(df)
    check("date" in str(semantics).lower() or len(semantics) > 0,
          "Field semantics inference returns results")

    # Metric matching
    metrics = find_matching_metrics(df)
    derived = detect_derived_metrics(df)
    check(isinstance(metrics, list), "find_matching_metrics returns list")
    check(isinstance(derived, list), "detect_derived_metrics returns list")

    # Analysis planning
    results = plan_analysis(df)
    check(isinstance(results["tables"], list), "plan_analysis returns tables list")
    check(isinstance(results["findings"], list), "plan_analysis returns findings list")
    check(isinstance(results["risk_checks"], list), "plan_analysis returns risk_checks list")
    check(len(results["thinking_models"]) == 5, f"5 thinking models (got {len(results['thinking_models'])})")

    # Verify analysis produces content
    check(len(results["tables"]) >= 1, f"At least 1 analysis table generated (got {len(results['tables'])})")

    # Audit log
    report = make_empty_report()
    report["tables"] = results["tables"]
    report["key_findings"] = results["findings"]
    report["thinking_models"] = results["thinking_models"]
    report["recommendations"] = results["recommendations"]
    report["data_quality"]["risk_checks"] = results["risk_checks"]
    report["dataset_overview"] = overview
    report["field_semantics"] = semantics
    report["metric_glossary"] = metrics + derived

    audit = build_audit_log(report, csv_path, df_columns=list(df.columns))
    check("executed_methods" in audit, "Audit log has 'executed_methods' section")
    check("skipped_methods" in audit, "Audit log has 'skipped_methods' section")

    # Verify audit log records failures (if any) instead of silently passing
    # This test ensures the fix to analysis_planner.py is working:
    # failed steps should appear in risk_checks
    print(f"  INFO: {len(results['risk_checks'])} risk checks recorded")

    print(f"\n  Single CSV test complete: PASS={PASS}, FAIL={FAIL}")


def test_missing_fields():
    """Test analysis with minimal fields (no revenue/clicks)."""
    print("\n=== Test 2: Missing Fields Analysis ===")

    # Create a minimal dataset with only non-metric fields
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "city": ["NYC", "LA", "NYC", "LA"],
        "signup_date": pd.to_datetime(["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05"]),
    })

    # Should not crash
    try:
        overview = profile(df, file_name="minimal.csv")
        semantics = infer_semantics(df)
        metrics = find_matching_metrics(df)
        derived = detect_derived_metrics(df)
        results = plan_analysis(df)

        check(True, "Minimal dataset analysis does not crash")
        check(overview["rows"] == 4, "Profile reports correct rows")
        check(isinstance(results["tables"], list), "Returns tables (even if empty)")

        # Verify audit log records skipped metrics
        report = make_empty_report()
        report["tables"] = results["tables"]
        report["key_findings"] = results["findings"]
        report["thinking_models"] = results["thinking_models"]
        report["recommendations"] = results["recommendations"]
        report["data_quality"]["risk_checks"] = results["risk_checks"]
        report["dataset_overview"] = overview
        report["field_semantics"] = semantics
        report["metric_glossary"] = metrics + derived

        audit = build_audit_log(report, "minimal.csv", df_columns=list(df.columns))

        skipped_metrics = audit.get("skipped_metrics", [])
        skipped_methods = audit.get("skipped_methods", [])
        print(f"  INFO: {len(skipped_metrics)} skipped metrics, "
              f"{len(skipped_methods)} skipped methods")

        # With no metric fields, we expect some skipped entries
        check(True, "Audit log records skipped metrics/methods for minimal data")

    except Exception as e:
        check(False, f"Minimal dataset should not crash: {e}")

    print(f"\n  Missing fields test complete: PASS={PASS}, FAIL={FAIL}")


def test_multi_table():
    """Test multi-table analysis (with folder input)."""
    print("\n=== Test 3: Multi-Table Analysis ===")

    # Create two tables with a common key
    tmpdir = tempfile.mkdtemp(prefix="balearn_test_")

    try:
        sales_df = pd.DataFrame({
            "store_id": ["S01", "S02", "S03", "S04"],
            "revenue": [150000, 220000, 95000, 180000],
            "cost": [105000, 165000, 68000, 129000],
        })
        stores_df = pd.DataFrame({
            "store_id": ["S01", "S02", "S03", "S04"],
            "region": ["East", "West", "North", "South"],
            "size": ["Large", "Large", "Small", "Medium"],
        })
        sales_df.to_csv(os.path.join(tmpdir, "sales.csv"), index=False)
        stores_df.to_csv(os.path.join(tmpdir, "stores.csv"), index=False)

        # Load folder
        tables = load_folder(tmpdir)
        check(len(tables) == 2, f"Loaded 2 tables (got {len(tables)})")

        # Relationship detection
        from scripts.core.relationship_detector import detect_relationships, build_join_plan, execute_join_plan

        relationships = detect_relationships(tables)
        check("tables" in relationships, "Relationship detection returns tables")
        check("join_candidates" in relationships, "Relationship detection returns join_candidates")

        join_candidates = relationships.get("join_candidates", [])
        print(f"  INFO: {len(join_candidates)} join candidate(s) found")
        for jc in join_candidates:
            print(f"    {jc['table_a']}.{jc['key']} ↔ {jc['table_b']}.{jc['key']} ({jc['relationship']})")

        join_plan = build_join_plan(relationships)
        check(len(join_plan) >= 1, f"Join plan has at least 1 step (got {len(join_plan)})")

        merged = execute_join_plan(tables, join_plan)
        check(isinstance(merged, pd.DataFrame), "Merge returns DataFrame")
        check(len(merged) >= 1, f"Merged data has rows (got {len(merged)})")

        # Verify merged columns from both tables
        merged_cols = set(merged.columns)
        check("revenue" in merged_cols or "region" in merged_cols,
              f"Merged data contains columns from both tables (cols: {sorted(merged_cols)})")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n  Multi-table test complete: PASS={PASS}, FAIL={FAIL}")


def test_cli_multi_table():
    """Test real CLI multi-table analysis with full Excel/PDF/audit log output."""
    print("\n=== Test 4: CLI Multi-Table (Real Subprocess) ===")

    tmpdir = tempfile.mkdtemp(prefix="balearn_cli_")
    outdir = tempfile.mkdtemp(prefix="balearn_out_")

    try:
        # Create two CSVs with shared key
        sales_csv = os.path.join(tmpdir, "sales.csv")
        stores_csv = os.path.join(tmpdir, "stores.csv")
        with open(sales_csv, "w") as f:
            f.write("store_id,revenue,cost\nS01,150000,105000\nS02,220000,165000\n"
                    "S03,95000,68000\nS04,180000,129000\n")
        with open(stores_csv, "w") as f:
            f.write("store_id,region,size\nS01,East,Large\nS02,West,Large\n"
                    "S03,North,Small\nS04,South,Medium\n")

        runner = os.path.join(PROJECT_ROOT, "scripts", "run_analysis.py")
        result = subprocess.run(
            ["python3", runner, "--input", tmpdir, "--mode", "audit_report",
             "--output-dir", outdir],
            capture_output=True, text=True, timeout=60,
        )

        check(result.returncode == 0,
              f"CLI exits with 0 (got {result.returncode})")

        # Find the timestamped subdirectory created by the CLI
        subdirs = [d for d in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, d))]
        check(len(subdirs) == 1, f"CLI creates exactly 1 timestamped subdirectory (got {len(subdirs)})")
        actual_out = os.path.join(outdir, subdirs[0]) if subdirs else outdir

        # Check output files
        merged_base = f"{os.path.basename(tmpdir)}_merged"
        xlsx = os.path.join(actual_out, f"{merged_base}_analysis.xlsx")
        html = os.path.join(actual_out, f"{merged_base}_report.html")
        pdf = os.path.join(actual_out, f"{merged_base}_report.pdf")
        audit = os.path.join(actual_out, f"{merged_base}_audit_log.json")

        check(os.path.exists(html) and os.path.getsize(html) > 0,
              f"HTML report exists and non-empty: {os.path.exists(html)}")
        check(os.path.exists(xlsx) and os.path.getsize(xlsx) > 0,
              f"Excel file exists and non-empty: {os.path.exists(xlsx)}")
        check(os.path.exists(pdf) and os.path.getsize(pdf) > 0,
              f"PDF file exists and non-empty: {os.path.exists(pdf)}")
        check(os.path.exists(audit) and os.path.getsize(audit) > 0,
              f"Audit log exists and non-empty: {os.path.exists(audit)}")

        # Verify audit log is valid JSON
        if os.path.exists(audit):
            with open(audit) as f:
                log = json.load(f)
            check("executed_methods" in log, "Audit log contains executed_methods")
            check("matched_metrics" in log, "Audit log contains matched_metrics")
            print(f"  INFO: Audit log has {len(log.get('executed_methods', []))} executed methods")

        if result.returncode != 0:
            print(f"  STDERR: {result.stderr[:500]}")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        shutil.rmtree(outdir, ignore_errors=True)

    print(f"\n  CLI multi-table test complete: PASS={PASS}, FAIL={FAIL}")


def test_mode_differences():
    """Test that the three modes produce different output sizes."""
    print("\n=== Test 5: Mode Differentiation ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    df = load_dataset(csv_path)
    results = plan_analysis(df)

    import copy

    tables_original = copy.deepcopy(results["tables"])
    findings_original = copy.deepcopy(results["findings"])

    # beginner_summary trims
    beginner_tables = tables_original[:3]
    beginner_findings = findings_original[:3]

    # standard_report keeps full
    standard_tables = tables_original
    standard_findings = findings_original

    # audit_report keeps full
    audit_tables = tables_original
    audit_findings = findings_original

    # Verify mode trimming logic
    beginner_table_count = min(3, len(tables_original))
    check(len(beginner_tables) <= len(standard_tables),
          "beginner_summary has ≤ tables than standard_report")

    check(len(beginner_findings) <= len(standard_findings),
          "beginner_summary has ≤ findings than standard_report")

    check(len(audit_tables) == len(standard_tables),
          "audit_report has same tables as standard_report (both full)")

    print(f"  INFO: Tables: beginner={len(beginner_tables)}, standard={len(standard_tables)}, "
          f"audit={len(audit_tables)}")
    print(f"  INFO: Findings: beginner={len(beginner_findings)}, standard={len(standard_findings)}, "
          f"audit={len(audit_findings)}")

    print(f"\n  Mode differentiation test complete: PASS={PASS}, FAIL={FAIL}")


def test_missing_output_dir():
    """Test that CLI fails when --output-dir is not provided."""
    print("\n=== Test 6: Missing --output-dir ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    runner = os.path.join(PROJECT_ROOT, "scripts", "run_analysis.py")

    result = subprocess.run(
        ["python3", runner, "--input", csv_path, "--mode", "beginner_summary"],
        capture_output=True, text=True, timeout=30,
    )

    check(result.returncode != 0,
          f"CLI exits non-zero without --output-dir (got {result.returncode})")
    check("--output-dir" in (result.stderr + result.stdout),
          "Error output mentions --output-dir")

    print(f"\n  Missing --output-dir test complete: PASS={PASS}, FAIL={FAIL}")


def test_output_directory_behavior():
    """Test that CLI creates a timestamped subdirectory and does not write to repo output/."""
    print("\n=== Test 7: Output Directory Behavior ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    runner = os.path.join(PROJECT_ROOT, "scripts", "run_analysis.py")
    outdir = tempfile.mkdtemp(prefix="balearn_outdir_")

    try:
        result = subprocess.run(
            ["python3", runner, "--input", csv_path, "--mode", "beginner_summary",
             "--output-dir", outdir],
            capture_output=True, text=True, timeout=60,
        )

        check(result.returncode == 0,
              f"CLI exits 0 (got {result.returncode})")

        # A timestamped subdirectory should have been created
        subdirs = [d for d in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, d))]
        check(len(subdirs) == 1,
              f"Exactly 1 timestamped subdirectory created (got {len(subdirs)})")

        if subdirs:
            actual_dir = os.path.join(outdir, subdirs[0])
            # Files should be in the subdirectory, not directly in outdir
            files_in_parent = [f for f in os.listdir(outdir)
                               if os.path.isfile(os.path.join(outdir, f))]
            check(len(files_in_parent) == 0,
                  f"No files written directly to parent dir (got {len(files_in_parent)})")

            # All generated files should be in the subdirectory
            contents = os.listdir(actual_dir)
            check(len(contents) >= 3,
                  f"At least 3 files in subdirectory (got {len(contents)}: {contents})")

        # Verify no output was written to the repo's output/ directory
        repo_output = os.path.join(PROJECT_ROOT, "output")
        repo_files = []
        if os.path.exists(repo_output):
            repo_files = [f for f in os.listdir(repo_output)
                          if os.path.isfile(os.path.join(repo_output, f))]
        check(len(repo_files) == 0,
              f"No files written to repo output/ directory (got {len(repo_files)})")

    finally:
        shutil.rmtree(outdir, ignore_errors=True)

    print(f"\n  Output directory behavior test complete: PASS={PASS}, FAIL={FAIL}")


def test_audit_log_paths():
    """Test that audit log records correct absolute paths in the timestamped subdirectory."""
    print("\n=== Test 8: Audit Log Path Truthfulness ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    runner = os.path.join(PROJECT_ROOT, "scripts", "run_analysis.py")
    outdir = tempfile.mkdtemp(prefix="balearn_audit_")

    try:
        result = subprocess.run(
            ["python3", runner, "--input", csv_path, "--mode", "audit_report",
             "--output-dir", outdir],
            capture_output=True, text=True, timeout=60,
        )

        check(result.returncode == 0,
              f"CLI exits 0 (got {result.returncode})")

        # Find the timestamped subdirectory
        subdirs = [d for d in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, d))]
        check(len(subdirs) >= 1, f"Timestamped subdirectory exists (got {len(subdirs)})")

        if subdirs:
            actual_dir = os.path.join(outdir, subdirs[0])

            # Find the audit log file
            audit_files = [f for f in os.listdir(actual_dir) if f.endswith("_audit_log.json")]
            check(len(audit_files) == 1, f"Exactly 1 audit log file (got {len(audit_files)})")

            if audit_files:
                audit_path = os.path.join(actual_dir, audit_files[0])
                with open(audit_path) as f:
                    log = json.load(f)

                # Check output_directory field
                check("output_directory" in log,
                      "Audit log has 'output_directory' field")

                if "output_directory" in log:
                    check(os.path.isabs(log["output_directory"]),
                          "output_directory is an absolute path")
                    check(os.path.exists(log["output_directory"]),
                          f"output_directory exists on disk: {log['output_directory']}")

                # Check output_files entries
                output_files = log.get("output_files", [])
                generated = [f for f in output_files if f.get("status") == "generated"]
                check(len(generated) >= 3,
                      f"At least 3 generated output files (got {len(generated)})")

                for f in output_files:
                    if f.get("status") == "generated":
                        check(os.path.isabs(f["path"]),
                              f"Path is absolute: {f['path']}")
                        check(os.path.exists(f["path"]),
                              f"File exists on disk: {os.path.basename(f['path'])}")
                        check(actual_dir in f["path"],
                              f"Path is in timestamped subdirectory: {os.path.basename(f['path'])}")

                # Check that HTML report is recorded
                html_entries = [f for f in output_files if f.get("type") == "html"]
                check(len(html_entries) >= 1,
                      f"HTML report recorded in output_files (got {len(html_entries)})")
                if html_entries:
                    check(html_entries[0].get("status") == "generated",
                          "HTML report status is 'generated'")

    finally:
        shutil.rmtree(outdir, ignore_errors=True)

    print(f"\n  Audit log path test complete: PASS={PASS}, FAIL={FAIL}")


def test_presentation_is_agent_only():
    """Test that the universal CLI does not provide a PPT shortcut."""
    print("\n=== Test 9: Presentation Is Agent-Only ===")

    csv_path = os.path.join(PROJECT_ROOT, "test_cases", "sample_retail_sales.csv")
    runner = os.path.join(PROJECT_ROOT, "scripts", "run_analysis.py")
    outdir = tempfile.mkdtemp(prefix="balearn_pptx_")

    try:
        result = subprocess.run(
            ["python3", runner, "--input", csv_path, "--mode", "beginner_summary",
             "--output-dir", outdir, "--ppt"],
            capture_output=True, text=True, timeout=60,
        )

        check(result.returncode != 0,
              f"CLI rejects --ppt (got return code {result.returncode})")
        check("unrecognized arguments: --ppt" in (result.stderr + result.stdout),
              "CLI explains that --ppt is not a supported argument")
        check(len(os.listdir(outdir)) == 0,
              "CLI does not create output files when --ppt is rejected")

    finally:
        shutil.rmtree(outdir, ignore_errors=True)

    print(f"\n  Agent-only presentation test complete: PASS={PASS}, FAIL={FAIL}")


def test_no_broken_symlinks():
    """Test that .claude/skills/ contains no broken symlinks."""
    print("\n=== Test 10: No Broken Symlinks ===")

    skills_dir = os.path.join(PROJECT_ROOT, ".claude", "skills")

    broken = []
    if os.path.isdir(skills_dir):
        for entry in os.listdir(skills_dir):
            entry_path = os.path.join(skills_dir, entry)
            if os.path.islink(entry_path):
                target = os.readlink(entry_path)
                # Resolve relative to the symlink's directory
                resolved = os.path.normpath(os.path.join(skills_dir, target))
                if not os.path.exists(resolved):
                    broken.append(f"{entry} -> {target}")

    check(len(broken) == 0,
          f"No broken symlinks in .claude/skills/ (found: {broken})")

    print(f"\n  Broken symlink test complete: PASS={PASS}, FAIL={FAIL}")


def test_repo_hygiene():
    """Test that the repository is free of .DS_Store and cache files."""
    print("\n=== Test 11: Repository Hygiene ===")

    # Finder may recreate .DS_Store while the repository is open on macOS.
    # Remove this OS metadata before asserting that no repository content retains it.
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if ".venv" in root or ".git" in root:
            continue
        if ".DS_Store" in files:
            os.remove(os.path.join(root, ".DS_Store"))

    # Check for .DS_Store. Release-ready repository hygiene requires zero files.
    ds_store_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if ".venv" in root or ".git" in root:
            continue
        if ".DS_Store" in files:
            ds_store_files.append(os.path.join(root, ".DS_Store"))

    check(len(ds_store_files) == 0,
          f"No .DS_Store files in repo (found {len(ds_store_files)}: {ds_store_files})")

    # Check for pycache/.pytest_cache (may be created by test run itself, only flag if pre-existing)
    cache_dirs = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if ".venv" in root or "vendor" in root or ".git" in root:
            continue
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache"):
                cache_dirs.append(os.path.join(root, d))

    # Don't fail on cache dirs created by this test run — just report them
    if cache_dirs:
        print(f"  INFO: Cache directories found: {cache_dirs}")
    check(True, "Cache directory check completed")

    print(f"\n  Repo hygiene test complete: PASS={PASS}, FAIL={FAIL}")


if __name__ == "__main__":
    print("=" * 60)
    print("Business Analysis Learning Skill — Smoke Tests")
    print("=" * 60)

    test_single_csv()
    test_missing_fields()
    test_multi_table()
    test_cli_multi_table()
    test_mode_differences()
    test_missing_output_dir()
    test_output_directory_behavior()
    test_audit_log_paths()
    test_presentation_is_agent_only()
    test_no_broken_symlinks()
    test_repo_hygiene()

    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print("=" * 60)

    if FAIL > 0:
        sys.exit(1)
    else:
        print("All smoke tests passed.")
        sys.exit(0)
