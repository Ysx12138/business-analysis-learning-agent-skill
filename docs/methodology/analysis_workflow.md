# Analysis Workflow

This document describes the complete analysis pipeline: what runs, in what order, which module is responsible, and what each step produces.

## Pipeline Overview

```
输入数据 (CSV/Excel)
    │
    ▼
[1] 数据读取 ─────────── data_intake.py / relationship_detector.py
    │
    ▼
[2] 数据画像 ─────────── data_intake.py
    │
    ▼
[3] 字段语义识别 ─────── field_semantics.py
    │
    ▼
[4] 指标匹配 ─────────── metric_registry.py
    │
    ▼
[5] 数据质量检查 ─────── analysis_planner.py
    │
    ▼
[6] 分组排名分析 ─────── analysis_planner.py
    │
    ▼
[7] 趋势分析 ─────────── analysis_planner.py  (仅当有时字段)
    │
    ▼
[8] 分布分析 ─────────── analysis_planner.py
    │
    ▼
[9] 思维模型生成 ─────── analysis_planner.py
    │
    ▼
[10] 建议生成 ────────── analysis_planner.py
    │
    ▼
[11] 统一 report schema ─ result_schema.py
    │
    ▼
[12] Excel 渲染 ──────── excel_renderer.py
[13] HTML/PDF 渲染 ────── html_report_renderer.py  (主路径: HTML → WeasyPrint/Playwright → PDF; pdf_renderer.py 仅后备)
[14] 演示文稿生成 ─────── Agent 读取 vendor/agent_presentation_skills/ 后执行（可选）
```

多表模式下，[1] 之前插入三步：

```
输入文件夹
    │
    ▼
load_folder() ────────── 遍历目录，每文件一个 DataFrame
    │
    ▼
detect_relationships() ─ 检测候选关联键、计算重叠率、分类关系
    │
    ▼
execute_join_plan() ──── 贪婪算法生成 join 计划，pandas.merge 逐步骤执行
    │
    ▼
[进入上述主流程]
```

## Step Details

### Step 1: 数据读取

| 项目 | 说明 |
|------|------|
| **模块** | `data_intake.py` — `load_dataset()` |
| **输入** | CSV 文件路径 或 Excel 文件路径 |
| **处理** | 按扩展名调用 `pd.read_csv()` 或 `pd.read_excel()` |
| **输出** | pandas DataFrame |
| **边界/风险** | 只支持 `.csv`, `.xlsx`, `.xls`；不支持 JSON, Parquet, SQL 等格式；大文件全部读入内存，无分块读取 |

**多表模式**使用 `relationship_detector.py` — `load_folder()`，遍历目录加载所有 CSV/Excel 文件，返回 `{表名: DataFrame}` 字典。

### Step 2: 数据画像

| 项目 | 说明 |
|------|------|
| **模块** | `data_intake.py` — `profile()` |
| **输入** | pandas DataFrame |
| **处理** | 计算行数、列数、字段类型字典；`df.isnull().sum()` 统计缺失值；`df.duplicated().sum()` 统计重复行；遍历 datetime 列取时间范围 |
| **输出** | `dataset_overview` dict：行数、列数、字段列表、字段类型、缺失值详情、重复行数、时间范围 |
| **边界/风险** | 时间范围只取第一个 datetime 列；缺失率计算基于总行数 |

### Step 3: 字段语义识别

| 项目 | 说明 |
|------|------|
| **模块** | `field_semantics.py` — `infer_semantics()` |
| **输入** | pandas DataFrame |
| **处理** | 对每个字段名执行正则匹配，与 130+ 预定义语义规则模式比对。匹配到则记录语义和置信度，未匹配则标记 "Unknown — review needed" |
| **输出** | `field_semantics` list：每个元素包含 field, inferred_meaning, confidence, evidence |
| **边界/风险** | 纯正则匹配，不分析数据内容；中文字段名无法识别；非标准缩写无法识别；置信度 `low` 的字段需要人工核实 |

### Step 4: 指标匹配

| 项目 | 说明 |
|------|------|
| **模块** | `metric_registry.py` — `find_matching_metrics()`, `detect_derived_metrics()` |
| **输入** | pandas DataFrame |
| **处理** | 遍历 14 个基础指标 + 衍生指标（CTR, CPC, 利润率, 负债率, 转化率）的 `field_priority` 列表，取第一个匹配到的字段名，调用 `formula_func` 计算值；再检查可计算的衍生指标（CTR, CPC, 利润率, 负债率, 转化率） |
| **输出** | `metric_glossary` list：每个元素包含 name, full_name, meaning, formula, current_value, business_use |
| **边界/风险** | 字段优先级列表决定匹配顺序；如果数据集缺少必要字段，该指标被静默跳过；衍生指标需要两个以上字段同时存在才能计算 |

### Step 5: 数据质量检查

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | pandas DataFrame，识别出的 numeric_cols |
| **处理** | 遍历数值列：检查负值比例 >1% → 告警；检查零值比例 >30% 且字段名含 spent/cost → 告警；遍历所有列：检查缺失率 >5% → 告警 |
| **输出** | `risk_checks` list：每个元素包含 check, status, detail, affected_analysis |
| **边界/风险** | 阈值是硬编码的（1%, 30%, 5%）；有些业务字段允许负值（如退货金额）会被误告警 |

### Step 6: 分组排名分析

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | 类别字段列表（cat_cols）、数值字段列表（numeric_cols） |
| **处理** | 对每个类别字段 × 数值字段组合执行 `groupby().agg(["sum", "mean", "count"])`，按 sum 降序排列。取 Top 1 vs Bottom 1 计算差距倍数，生成 finding |
| **输出** | 数据表（每张 = 一个类别+数值组合的排名表）+ finding（Top/Bottom 差距） |
| **边界/风险** | 限制前 3 个类别字段 × 前 2 个数值字段；类别过多时排名表可能过长；空分组会被 pandas 自动排除 |

### Step 7: 趋势分析

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | 日期字段列表（date_cols）、数值字段列表（numeric_cols） |
| **处理** | `dt.to_period("M")` 聚合到月份级别，`groupby().sum()` 计算月度趋势。对比首尾月份值计算变化百分比，生成 finding |
| **输出** | 趋势数据表 + finding（增长/下降趋势） |
| **边界/风险** | 只取第一个日期字段 × 第一个数值字段；这只是一种聚合后的趋势观察，不是时间序列预测；首尾值比较不能代表整体趋势；数据跨度过短时趋势无意义 |

### Step 8: 分布分析

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | 数值字段列表（numeric_cols） |
| **处理** | 对每个数值字段执行 `df.describe()`，输出 count, mean, std, min, 25%, 50%, 75%, max |
| **输出** | 分布统计表 |
| **边界/风险** | 限制前 2 个数值字段；极端值会扭曲均值和标准差；小样本（<30 行）的描述统计稳定性有限 |

### Step 9: 思维模型生成

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | cat_cols, numeric_cols, findings |
| **处理** | 5 个固定思维模型模板，填入数据集的分类维度和数值字段数量作为证据 |
| **输出** | 5 个 thinking_model dict |
| **边界/风险** | 模板是固定的，证据描述是参数化的，不会根据数据自适应。这意味着不同数据集可能生成措辞相似的思维模型，只是填入了不同的字段名和数量 |

### Step 10: 建议生成

| 项目 | 说明 |
|------|------|
| **模块** | `analysis_planner.py` — `plan_analysis()` 内部 |
| **输入** | findings_list, risk_list |
| **处理** | 如果有 findings → 生成"关注 Top-Bottom 差距"建议；始终生成"建立监控机制"建议；如果有 risk → 生成"数据质量改进"建议 |
| **输出** | recommendations list |
| **边界/风险** | 模板化程度高；建议内容不会超出"关注差距-监控-改进质量"三个方向 |

### Step 11-14: 渲染输出

三个渲染器各自独立消费 `report` dict，互不影响：

| 渲染器 | 模块 | 格式 | 库 | 说明 |
|--------|------|------|-----|------|
| Excel | `excel_renderer.py` | `.xlsx` | openpyxl | 每张 table 一个 sheet + 看板页 |
| HTML/PDF | `html_report_renderer.py` | `.html` / `.pdf` | HTML/CSS + WeasyPrint / Playwright | 主 PDF 路径：HTML 报告 → WeasyPrint/Playwright → PDF；`pdf_renderer.py` (reportlab) 仅作后备 |
| 演示文稿 | Agent + `vendor/agent_presentation_skills/` | `.html` / 可编辑演示文稿 | 内置设计 Skill | 必须通过 Agent 工作流生成，runner 不提供 PPT 快捷路径 |

---

## 多表模式（额外步骤）

### 关系检测

| 项目 | 说明 |
|------|------|
| **模块** | `relationship_detector.py` — `detect_relationships()` |
| **输入** | `{表名: DataFrame}` 字典 |
| **处理** | 两两配对查找共享列名；计算值集合重叠率（交集 ÷ 并集）；按 `nunique/len` 分类关系类型 |
| **输出** | tables 概要 + join_candidates 列表（含重叠率、关系类型、风险等级） |
| **边界/风险** | 只能检测同名列名关联；不支持不同列名的键匹配；复合键最多检测列对，不支持三列以上 |

### Join 计划与执行

| 项目 | 说明 |
|------|------|
| **模块** | `relationship_detector.py` — `build_join_plan()`, `execute_join_plan()` |
| **输入** | relationships 分析结果 |
| **处理** | 贪婪算法：ID 键优先 → 复合键优先 → 每个表最多 join 一次 → pandas.merge 逐步骤执行 → >50x 行爆炸跳过 |
| **输出** | 合并后的 DataFrame |
| **边界/风险** | 无法处理循环依赖；50x 阈值是硬编码的；列名冲突通过表名后缀处理，后缀可能破坏指标匹配（已在 `_normalize_metric_columns()` 中修复） |
