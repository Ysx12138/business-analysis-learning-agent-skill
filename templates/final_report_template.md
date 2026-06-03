# Business Data Analysis Report Template

Use this template for `standard_report` and `audit_report`.

For `beginner_summary`, use `templates/output_modes_template.md`.

## 1. Task Understanding

<!-- Brief summary of the business question and analysis goal -->

## 2. Dataset Overview

<!-- File name, rows, columns, time range, fields -->

## 3. Dataset Risk Check

| Issue | Why It Matters | Affected Analysis | Treatment | Remaining Risk |
|---|---|---|---|---|

## 4. Cleaning Impact Assessment

| Cleaning Rule | Business Reason | Rows Removed | Percentage Removed | Affected Analysis | Treatment |
|---|---|---|---:|---:|---|---|

## 5. Field to Business Question Mapping

| Field | Metric | Business Question | Analysis Method |
|---|---|---|---|

## 6. Key Business Questions

<!-- Prioritized list of business questions this analysis answers -->

## 7. Analysis Methods

| Question | Method | Why This Method |
|---|---|---|

## 8. Key Metrics and Calculations

For each metric, include the full teaching chain:

### 指标：{metric_name}

#### 分析结果
<!-- The actual calculated value -->

#### 这个指标是什么意思？
<!-- Plain-language explanation for beginners -->

#### 为什么要计算它？
<!-- Business context: what decision does this metric inform -->

#### 公式是什么？
<!-- Exact calculation formula -->

#### 用到了哪些字段？
<!-- Which columns from the dataset were used -->

#### 结果怎么理解？
<!-- How to read the number: is higher better? What's a good benchmark? -->

#### 它不能说明什么？
<!-- Boundaries: what conclusion should NOT be drawn from this metric alone -->

#### 下次怎么复用？
<!-- When you see similar data, when should you calculate this metric -->

## 9. Key Findings

For each finding, include the full teaching chain:

### 发现：{finding_title}

#### 分析结果
<!-- The finding itself -->

#### 证据来自哪里？
<!-- Data table reference, specific numbers -->

#### 这个结果说明什么？
<!-- Business interpretation -->

#### 它不能说明什么？
<!-- Boundary: what this finding does NOT prove -->

#### 下一步如何验证？
<!-- How to confirm or deepen this finding -->

#### 下次怎么复用？
<!-- Transferable pattern for similar data -->

## 10. Grouping / Ranking Analysis

### 为什么要按这个字段分组？
<!-- Why segment by this dimension -->

### 这个方法解决什么问题？
<!-- What question does ranking/grouping answer -->

### 计算逻辑是什么？
<!-- How aggregation works: sum, mean, count -->

### 结果怎么理解？
<!-- How to read the ranking table -->

### 初学者容易误解什么？
<!-- Common pitfalls for beginners -->

### 下次怎么复用？
<!-- When you have categorical + numeric fields in a new dataset -->

## 11. Trend Analysis

### 为什么要按时间分析？
<!-- Why time dimension matters for business decisions -->

### 计算逻辑是什么？
<!-- How date grouping and aggregation works -->

### 上升或下降说明什么？
<!-- Business implications of direction -->

### 这是不是预测？
<!-- Past trend != future prediction. Clarify the boundary. -->

### 下次怎么复用？
<!-- When you see date + numeric fields together -->

## 12. Business Interpretation

<!-- Executive summary connecting findings to business decisions -->

## 13. Recommendations

| Finding | Business Meaning | Recommended Action | Metric to Track | Data Needed |
|---|---|---|---|---|

## 14. Metrics and Concepts Explained

<!-- Glossary: metric name, abbreviation, formula, plain-language explanation -->

## 15. Beginner Learning Notes

### 本次分析学到了什么？

### 本次用了哪些方法？
<!-- List of analysis methods applied -->

### 每种方法解决什么问题？
<!-- One sentence per method: what question it answers -->

### 下次看到类似数据应该怎么开始？
<!-- Step-by-step reusable workflow for beginners -->

### 哪些结论不能过度解读？
<!-- Caveats and boundaries specific to this analysis -->

## 16. Limitations

<!-- Known data limitations, methodological constraints -->

## 17. Recommended Next Analysis

| Analysis | Purpose | Required Fields | Expected Output | Business Value |
|---|---|---|---|---|
