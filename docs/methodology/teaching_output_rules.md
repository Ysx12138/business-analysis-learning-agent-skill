# Teaching Output Rules

This document defines how the Skill produces teaching-oriented output — not just analysis results, but explanations that help a business beginner understand the reasoning and reuse it next time.

## 1. Core Principle

The Skill's output goal is not just to tell the user **what the result is**, but to teach them **why the analysis is done this way, and how to reuse the thinking next time**.

Every output must upgrade from:

```
Finding → Suggestion
```

To:

```
Finding → Method Explanation → Metric Explanation → Business Interpretation → Risk Boundary → Learning Transfer
```

## 2. Ten Teaching Output Rules

1. **Never output only results** — always explain how the result was derived.
2. **Never give only metric values** — always explain what the metric means.
3. **Never give only business suggestions** — always explain the connection between the suggestion and the data evidence.
4. **Every formula must state its field sources** — which columns were used to compute it.
5. **Every analysis method must explain why it is suitable** for the current data.
6. **Every conclusion must state what it CANNOT prove** — correlation is not causation, trend is not prediction.
7. **All explanations must be beginner-accessible** — avoid unexplained professional jargon.
8. **If a technical term is used, it must be explained** in plain language first.
9. **Output must include "how to reuse next time"** transfer guidance.
10. **Do not output only charts and conclusions** without explaining the method.

## 3. Per-Metric Explanation Requirements

Every metric in the output must explain:

| Field | Content |
|-------|---------|
| **Metric definition** | What the metric is in plain language |
| **Business meaning** | Why this metric matters in business |
| **Formula** | The calculation logic with field sources |
| **Field sources** | Which specific columns in the dataset |
| **Applicable scenarios** | When this metric is useful |
| **Inapplicable scenarios** | When this metric is NOT useful |
| **Common misunderstanding** | What beginners often get wrong |
| **How to reuse next time** | When you see similar fields, you can compute this metric |

### Template

```
### Metric: {metric_name}

**Definition (定义):** {one sentence in plain language}

**Business Meaning (业务含义):** {why it matters}

**Formula (公式):** {formula}

**Field Sources (字段来源):**
- `{field_a}` — {business meaning of field_a}
- `{field_b}` — {business meaning of field_b}

**How to Interpret (如何理解):** {what the current value means in business terms}

**What It Cannot Prove (不能说明什么):** {boundary — what this metric does NOT tell you}

**Common Misunderstanding (常见误区):** {what beginners often get wrong}

**How to Reuse (下次如何复用):** {when you see similar fields in another dataset, you can compute this metric by...}
```

## 4. Per-Method Explanation Requirements

Every analysis method in the output must explain:

| Field | Content |
|-------|---------|
| **Why this method** | Why it was chosen for the current data |
| **What problem it solves** | The business question it answers |
| **Input fields** | Which fields were used |
| **How to read the output** | What the result means |
| **What it cannot prove** | The boundary of this method |
| **Common beginner mistake** | What beginners easily misunderstand |

### Template

```
### Method: {method_name}

**Why This Method (为什么选这个方法):** {reason tied to data conditions}

**What Problem It Solves (解决什么问题):** {business question in plain language}

**Input Fields (输入字段):**
- `{field}` — {business meaning}

**How to Read the Output (结果怎么看):** {explanation of the output format and its meaning}

**What It Cannot Prove (不能说明什么):** {boundary}

**Common Beginner Mistake (初学者容易误解什么):** {one key pitfall}

**How to Reuse (下次如何复用):** {when your data has a category field and a numeric field, you can do this analysis}
```

## 5. Per-Finding Explanation Requirements

Every finding in the output must explain:

| Field | Content |
|-------|---------|
| **Data evidence** | Which data this finding is based on |
| **What it means** | Business interpretation |
| **What it does NOT mean** | Boundary and limitation |
| **How to verify further** | Next step to validate |

### Template

```
### Finding: {title}

**Evidence (证据):** {specific numbers and field sources}

**What It Means (说明什么):** {business interpretation}

**What It Does NOT Mean (不说明什么):** {boundary — e.g., "this does not prove that region causes the revenue difference"}

**How to Verify Further (下一步如何验证):** {suggested follow-up analysis}

**How to Reuse (下次如何复用):** {when you see similar data patterns, you can apply this kind of comparison}
```

## 6. Skipped Analysis Explanation Requirements

When a method is skipped, the explanation must include:

```
### Skipped: {method_name}

**Why Skipped (为什么跳过):** {specific missing field, insufficient sample, or unclear business question}

**What Would Be Needed (需要补充什么):** {data or user confirmation needed}

**Beginner Note (初学者说明):** {why it's correct to skip this — in plain language}
```

## 7. Learning Summary Requirements

At the end of every report, include a "What You Learned" section:

```
## What You Learned in This Analysis

### Methods Used (本次用了哪些方法)
- {method_1}: {what it does in one sentence}
- {method_2}: {what it does in one sentence}

### Reusable Thinking Patterns (可复用的思维模式)
- Decomposition: don't look at totals alone — break them down by meaningful dimensions
- Segment Divergence: don't trust averages — compare subgroups
- ...

### Next Time You See Similar Data (下次看到类似数据)
1. First, check field names and types
2. Look for date fields — check trends
3. Look for category fields — check group differences
4. Look for numeric fields — check totals, averages, and distributions
5. Look for customer ID fields — check customer behavior
6. Look for amount and quantity fields — compute business metrics
7. Don't force analysis when fields don't support it

### Conclusions NOT to Over-Interpret (不能过度解读的结论)
- High revenue does not mean high profit
- Correlation is not causation
- Trend analysis is not prediction
- Group differences do not prove that the group factor causes the result
- Small sample sizes produce unstable conclusions
```

## 8. Language Style Rules

1. Use plain language before introducing technical terms.
2. Explain every technical term the first time it appears.
3. Every formula must have a plain-language explanation alongside it.
4. Do not just say "significant," "correlated," or "trend" — explain what these words mean.
5. Do not write in academic paper style.
6. Do not write empty business cliches.
7. Every suggestion must be traceable back to a data finding.
8. Every finding must be traceable back to a field or metric.
9. Clearly separate: "data fact," "business interpretation," "assumption," and "limitation."
10. Default output language is Chinese, unless the user requests English or bilingual.

## 9. Mode-Based Verbosity Control

| Mode | Teaching Depth |
|------|---------------|
| `beginner_summary` | Short teaching notes (1-2 sentences per finding). Focus on the top 3 concepts. Skip full method explanations. |
| `standard_report` | Medium teaching notes. Include metric definitions, method reasons, and one caveat per finding. |
| `audit_report` | Full teaching output. Complete per-metric, per-method, and per-finding templates. All 5 thinking models with evidence. |

## 10. Anti-Patterns (What NOT to Do)

- Output a finding without explaining which field/metric it came from
- Output a metric value without explaining the formula
- Say "this is significant" without explaining what "significant" means
- Say "we recommend X" without tracing it back to a specific data finding
- Use "correlation analysis shows..." without warning that correlation is not causation
- Skip method explanation because "the user just wants the answer"
- Generate identical beginner_notes regardless of dataset content
