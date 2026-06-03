# Audit Log Design

## Purpose

审计日志的目标是让用户能够追溯每次分析执行的全部决策过程：

- Skill 为什么选择某个指标
- 使用了哪些字段
- 使用了什么公式
- 哪些分析被执行
- 哪些分析被跳过
- 为什么跳过
- 数据质量风险
- 最终输出文件

## Current Status

**Phase 1（轻量级输出）已在 v0.7 实现。** 参见 `scripts/core/audit_logger.py`，该模块在 `run_analysis.py` 主流程末尾被调用，每次运行自动输出 `*_audit_log.json`。

Phase 2（仪表化）和 Phase 3（全链路事件日志）为后续计划，尚未实现。

## Proposed Audit Log JSON Structure

```json
{
  "schema_version": "0.1.0",
  "input_file": "",
  "run_timestamp": "",
  "analysis_mode": "",

  "dataset_profile": {
    "rows": 0,
    "columns": 0,
    "field_names": [],
    "field_types": {},
    "missing_values": {},
    "duplicate_rows": 0,
    "time_range": ""
  },

  "field_semantics": [
    {
      "field": "",
      "inferred_meaning": "",
      "confidence": "high|medium|low",
      "matched_rule": ""
    }
  ],

  "matched_metrics": [
    {
      "metric_name": "",
      "formula": "",
      "used_fields": [],
      "current_value": null
    }
  ],

  "skipped_metrics": [
    {
      "metric_name": "",
      "required_fields": [],
      "missing_fields": [],
      "reason": ""
    }
  ],

  "executed_methods": [
    {
      "method_name": "grouped_ranking|trend_analysis|distribution_analysis|risk_check",
      "trigger_condition": "",
      "used_fields": [],
      "output_table_name": ""
    }
  ],

  "skipped_methods": [
    {
      "method_name": "",
      "required_condition": "",
      "reason": ""
    }
  ],

  "data_quality_risks": [
    {
      "risk_type": "negative_values|high_zero_rate|high_missing_rate",
      "field": "",
      "severity": "warn",
      "evidence": "",
      "suggestion": ""
    }
  ],

  "output_files": [
    {
      "type": "excel|pdf|ppt",
      "path": "",
      "status": "generated|skipped"
    }
  ]
}
```

## Implementation Plan

### Phase 1: Lightweight Output (本轮实现)

新增 `scripts/core/audit_logger.py`，提供：

```
build_audit_log(report, input_path, config) → dict
save_audit_log(audit_log, output_dir) → str (file path)
```

在 `run_analysis.py` 末尾调用，生成 `audit_log.json`。

覆盖范围：
- 输入文件信息 ✅
- 数据集画像 ✅（从 `report["dataset_overview"]` 获取）
- 字段语义 ✅（从 `report["field_semantics"]` 获取）
- 匹配到的指标 ✅（从 `report["metric_glossary"]` 获取）
- 数据质量风险 ✅（从 `report["data_quality"]["risk_checks"]` 获取）
- 输出文件路径 ✅（主流程已知）
- 跳过的指标 — 基于注册表字段检测逻辑反推 ⚠️
- 执行/跳过的方法 — 基于分析计划器逻辑反推 ⚠️

Phase 1 能做到的是：把已有的信息（dataset_overview, field_semantics, metric_glossary, risk_checks）组织成审计日志格式，并用一批静态检查函数推算哪些指标被跳过、哪些方法没执行。

### Phase 2: Full Instrumentation（后续计划）

在 `metric_registry.py`、`analysis_planner.py`、`field_semantics.py` 中植入主动日志回传：

```
# metric_registry.py 中增加
skipped = []
for metric in METRIC_REGISTRY:
    matched = [f for f in metric["field_priority"] if f in df.columns]
    if not matched:
        skipped.append({
            "metric": metric["name"],
            "required_fields": list(metric["required_fields"]),
            "reason": "No matching field found in dataset"
        })
```

这样跳过日志在分析阶段就生成了，不需要事后反推。

### Phase 3: Full Audit Trail（长期）

在分析管线的每个步骤注入事件日志：

```
["data_intake", "field_semantics", "metric_matching",
 "risk_check", "ranking_analysis", "trend_analysis",
 "distribution_analysis", "model_generation", "recommendation_generation",
 "excel_render", "html_render", "pdf_render"]
```

每个事件记录：
- timestamp
- step_name
- status (started/completed/failed/skipped)
- duration_seconds
- output_preview
- warnings

## File Location

审计日志文件路径：
```
<user-confirmed-output-dir>/<input_base_name>_<timestamp>/<input_base_name>_audit_log.json
```

与 Excel/HTML/PDF 同目录。每次分析生成一个独立的 JSON 文件。演示文稿由
Agent 调用内置演示文稿 Skill 生成，不属于 CLI 审计日志的直接渲染步骤。

## Access Pattern

用户可以通过以下方式查看审计日志：

1. 直接打开 JSON 文件（用任意文本编辑器）
2. 在分析完成后的对话摘要中，Agent 可以总结审计日志的关键信息
3. 后续可以通过 CLI 参数 `--audit` 或 `--verbose` 控制审计日志的详细程度

## Design Principle

审计日志应该是：

- **机器可读**：JSON 格式，便于后续分析、可视化或导入其他工具
- **人类可读**：关键字段使用自然语言描述，不只有编码
- **完整但不过度**：记录决策和结果，但不记录全部原始数据
- **可追加**：多次分析的审计日志可以累加，不会覆盖
