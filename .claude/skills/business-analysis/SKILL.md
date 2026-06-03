---
name: business-analysis
description: Help business beginners learn data analysis while completing real analysis tasks, with explanations of business logic, metrics, and reusable thinking patterns
---

# Business Analysis Learning Agent Skill

## 1. Purpose

Help business beginners learn data analysis while completing real analysis tasks.

The Agent should not only produce outputs, but also explain the reasoning behind the analysis.

## 1.1 Output Language Policy

- Repository artifacts are written in **English**.
- Default user-facing outputs are **Chinese** (unless the user requests English):
  - the analysis text report
  - Excel pivot/dashboard workbook
  - PDF report
  - PPT/slide deliverables (if generated)
- If the user requests, the Agent can output **English** (or bilingual).

## 1.2 Platform Compatibility

This skill is platform-agnostic. It is not limited to Claude Code.

Any AI agent can use this skill if it can:

- read instruction files
- inspect or receive a business dataset
- follow a structured workflow
- create files when deliverables are required

Claude Code-specific files under `.claude/` are optional adapters. The reusable behavior is defined by this `SKILL.md`, the templates, examples, and test cases.

## 2. Target User

- beginners in business, management, marketing, operations, or data analysis
- users who can ask an AI Agent to analyze data but do not yet understand the analytical logic
- users who need explanations of metrics, business concepts, and abbreviations

## 3. When to Use This Skill

- CSV or Excel business datasets
- retail sales data
- customer behavior data
- product performance data
- marketing campaign data
- store operation data
- revenue/profit data
- public business datasets

## 4. Core Principle and Positioning

### 4.1 What This Skill Is

Business Analysis Skill is a **data analysis workflow skill designed for beginners and business scenarios.**

It guides the Agent to complete business data analysis in a **stable, explainable, and teachable** way.

Its core is NOT to replace SPSS, Stata, Excel, machine learning platforms, or professional data science tools.

### 4.2 Primary Goals

1. Help users understand what is in the dataset.
2. Help users understand which metrics can be computed.
3. Help users understand **why** a particular analysis method is chosen.
4. Help users understand the **business meaning** of analysis results.
5. Help users know **what further advanced analyses** the current data could support.
6. Prevent the Agent from forcibly applying advanced methods when data conditions are insufficient.
7. Prevent over-interpreting correlation, statistical significance, or prediction results as definitive conclusions.

### 4.3 Core Teaching Principle — "Learn by Doing"

Business Analysis Skill is not just a report generator. It is a **"learn by doing" (做中学) data analysis teaching Skill** designed for business beginners.

Its output goal is not only to tell users what the results are, but to teach them:

- Why the analysis is done this way
- How the metrics are computed from the data
- What the results mean in business language
- What the results CANNOT prove
- How to reuse the thinking next time

The output logic upgrades from:

```
Finding → Suggestion
```

To:

```
Finding → Method Explanation → Metric Explanation → Business Interpretation → Risk Boundary → Learning Transfer
```

For each important analysis step, the Agent must explain these 8 elements:

1. **Analysis result** — what the data shows
2. **Method explanation** — why this method was chosen for this data
3. **Metric explanation** — what the metric means and how it's calculated
4. **Formula explanation** — the calculation with field sources
5. **Field sources** — which columns were used
6. **Business meaning** — what the result means for business decisions
7. **Risk boundary** — what the result CANNOT prove or what could go wrong
8. **Beginner reuse** — how to apply this method when seeing similar data next time

See `docs/methodology/teaching_output_rules.md` for the complete teaching output specification.
See `docs/methodology/report_structure.md` for the standard report structure with teaching annotations.

## 5. Analysis Method Layering

All analysis methods are organized into three tiers. The Agent must follow this layering when choosing what to execute.

### Tier 1: Default Basic Analysis (Always Execute)

These methods run by default for every dataset. They answer "what is in the data?"

- Data profiling — rows, columns, field types
- Field semantics recognition — what each field likely means
- Missing value check
- Duplicate value check
- Outlier / abnormal value check
- Basic metric computation — matching fields to the metric registry
- Grouped aggregation — sum, mean, count by category
- Ranking analysis — top/bottom by key numeric metrics
- Trend analysis — month-over-month changes (when a date field exists)
- Descriptive statistics — mean, median, std, quartiles
- Data quality risk warnings
- Business interpretation and beginner-friendly explanation

These answer:
- What is in the dataset?
- Which fields are important?
- Which metrics are highest or lowest?
- Which segments show large differences?
- Which time periods show growth or decline?
- Are there data quality issues?

### Tier 2: Advanced Analysis Recommendations (Suggest, Do Not Auto-Execute)

When data conditions are met, the Agent **recommends** these methods but does NOT automatically execute them unless the user confirms or the output mode is `audit_report` with explicit user intent.

- Correlation analysis
- RFM analysis
- t-test
- Chi-square test
- Linear regression
- Logistic regression / classification
- Clustering analysis
- Cohort analysis
- Seasonality analysis
- Time series forecasting
- Sentiment analysis
- Causal inference

For each recommendation, the Agent must explain:
- Why this method is suitable for the current data
- Which fields are required
- Which fields are already present
- Which fields are missing
- What business question this method can answer
- What business question this method CANNOT answer
- Whether auto-execution is suggested
- Whether user confirmation is needed
- What the risks are

### Tier 3: Advanced Analysis Execution (Conditional)

A Tier 2 method is executed ONLY when ALL of the following are met:

- The user explicitly requests this method, OR the user has a clear business question that maps to this method
- The target variable or analysis object is clearly identified
- Data fields meet the minimum requirements
- Sample size is adequate
- The Agent can explain the method's boundaries and risks
- The output MUST include risk warnings

If conditions are NOT met, the Agent MUST skip the method and explain why.

See `docs/methodology/advanced_method_triggers.md` for detailed trigger rules for each method.

## 6. Standard Workflow

### Step 0: Confirm Inputs and Output Location (Required)

Before starting analysis, ask the user three questions in order:

**0a. Confirm the input dataset:**

Ask where the data file or data folder is located.

**0b. Ask for output mode:**

- `beginner_summary`: short beginner-friendly output (default)
- `standard_report`: medium report with key reasoning
- `audit_report`: full detailed output for testing or portfolio review

Do not proceed until the user selects a mode (or explicitly chooses the default).

**0c. Ask for output folder:**

Ask where to save Excel, HTML, PDF, PPT, and audit log files.

Example prompt:

```
Where should I save the analysis output files (Excel, HTML, PDF, audit log)?

If you're not sure, I can use:
  <数据文件所在目录>/analysis_outputs/<数据集名称_日期时间>/
```

The Agent must confirm the final output directory with the user before executing analysis.

- Never silently write output files into the Skill installation directory.
- Never default to the repository's `output/` folder without user confirmation.
- If the output directory already contains files with the same names, create a timestamped subdirectory (e.g., `analysis_2026-06-03_143052/`) to avoid silent overwrites.

### Step 1: Understand the User's Goal

If the user goal is unclear, infer possible business questions from the dataset and clearly state assumptions.

### Step 2: Inspect the Dataset

Check:

- rows and columns
- field names
- field types
- missing values
- duplicate values
- time fields
- category fields
- numerical fields
- possible business meaning of fields

Before producing conclusions, perform a dataset risk check:

- cancelled orders
- negative or zero quantity
- zero or abnormal unit price
- missing customer identifiers
- non-product transaction items
- incomplete time periods
- dominant market or customer concentration
- duplicate rows

For each relevant issue, explain why it matters, which analysis it affects, and whether the data should be removed, separated, or kept for another analysis.

### Step 3: Translate Data Fields into Business Questions

Example mapping:

- `sales_amount` -> revenue performance
- `customer_id` -> repeat purchase or customer behavior
- `order_date` -> trend or seasonality
- `category` -> product/category comparison
- `store_id` -> store performance

Use a field-to-analysis mapping table when the dataset has enough structure:

| Field | Metric | Business Question | Analysis Method |
|---|---|---|---|
| `InvoiceNo` | Order Count, AOV | How large and efficient are orders? | descriptive statistics |
| `Quantity * UnitPrice` | Revenue | What is total sales value? | metric aggregation |
| `InvoiceDate` | Monthly Revenue | Is there trend or seasonality? | trend analysis |
| `Country` | Revenue Contribution | Which markets contribute most? | contribution analysis |
| `CustomerID` | Repeat Rate, RFM | What is customer quality? | customer analysis |
| `StockCode` / `Description` | Product Revenue | Which products drive revenue? | product analysis |

### Step 4: Choose Analysis Methods

Methods are organized into three tiers per Section 5 (Analysis Method Layering).

**Tier 1 — Always execute:**

- descriptive statistics
- trend analysis
- ranking analysis
- contribution analysis
- data quality checks
- basic metric computation

**Tier 2 — Recommend with explanation (do not auto-execute):**

- correlation analysis
- RFM analysis
- t-test
- chi-square test
- linear regression
- logistic regression
- clustering analysis
- cohort analysis
- seasonality analysis
- time series forecasting
- sentiment analysis

**Tier 3 — Execute only when conditions met and user confirms:**

- causal inference
- any method requiring user-specified target variables

The Agent must explain why each method is chosen or skipped.
For Tier 2 methods, see `docs/methodology/advanced_method_triggers.md` for detailed trigger rules.

### Step 5: Execute the Analysis

Output should include:

- tables
- charts if useful
- key findings
- business interpretation
- beginner learning notes

For every major step, include learning-oriented reasoning:

1. What business question this step answers
2. Why this method is appropriate
3. Which dataset fields are used
4. How the metric is calculated
5. What the result means in business language
6. What a beginner should learn from this step
7. What limitations or risks may affect the conclusion

When cleaning data, include a cleaning impact assessment:

Cleaning Rule:
Rule:
Business Reason:
Rows Removed:
Percentage Removed:
Affected Analysis:
Treatment:

### Step 6: Explain Metrics and Abbreviations

For each metric or abbreviation, explain:

- full name
- simple meaning
- formula
- current calculation when data is available
- business use
- common misunderstanding
- limitation

Examples include:

- KPI
- GMV
- AOV
- CAC
- ROI
- retention rate
- conversion rate
- contribution rate
- profit margin

### Step 7: Generate Business Insights

Each insight should include:

- data evidence
- business interpretation
- possible reason
- suggested action
- risk or limitation

Recommendations must be actionable and tied to evidence. Use this structure:

Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed

### Step 8: Provide Beginner Learning Feedback

At the end, summarize:

- business concepts learned
- analysis methods learned
- metrics learned
- reusable thinking pattern
- suggested next learning step

End with a structured Recommended Next Analysis section rather than a conversational closing.

### Step 9: PPT Generation (Optional)

After the analysis report and deliverables are complete, ask the user if they would like to generate a presentation:

Ask in the default output language (Chinese unless the user requested English).

**Mandatory presentation-generation boundary:**

- Every presentation must be generated by the Agent after reading the matching bundled presentation Skill under `vendor/agent_presentation_skills/`.
- Do not generate a presentation with `scripts/run_analysis.py`, a generic `python-pptx` template, or any other shortcut that bypasses the bundled presentation Skill.
- The universal runner intentionally generates only Excel, HTML, PDF, and audit log files.
- Save the presentation into the same user-confirmed output folder unless the user chooses another location.
- Before delivery, follow the selected presentation Skill's QA/checklist requirements and verify titles, page numbers, repeated slides, output language, and layout.

Offer two style options with a brief description:

1. **Editorial magazine style** (Guizang Style A)
   - Two-page flipping HTML deck, WebGL motion background, narrative layouts
   - 5 themes available (see `vendor/agent_presentation_skills/guizang-ppt-skill/references/themes.md`)
   - Deliverable: standalone HTML file

2. **Swiss / International Typographic Style** (Guizang Style B)
   - Minimal grid system, strong hierarchy, structured layouts
   - 4 accent colors available (see `vendor/agent_presentation_skills/guizang-ppt-skill/references/themes-swiss.md`)
   - Deliverable: standalone HTML file

Implementation instructions — presentation templates are bundled in `vendor/agent_presentation_skills/` (`guizang-ppt-skill` for Styles A/B):

- If the user selects **Editorial magazine style** (Guizang Style A):
  1. Read `vendor/agent_presentation_skills/guizang-ppt-skill/assets/template.html` to understand the slide structure
  2. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/themes.md` for theme reference (5 themes listed in the file)
  3. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/layouts.md` for available slide layouts
  4. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/checklist.md` for QA requirements
  5. Generate an HTML file with all slides, using the template structure and chosen theme

- If the user selects **Swiss / International Typographic Style** (Guizang Style B):
  1. Read `vendor/agent_presentation_skills/guizang-ppt-skill/assets/template-swiss.html` to understand the slide structure
  2. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/themes-swiss.md` for accent color reference (options listed in the file)
  3. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/layouts-swiss.md` for available S layouts
  4. Read `vendor/agent_presentation_skills/guizang-ppt-skill/references/checklist.md` for QA requirements
  5. Generate an HTML file with all slides, using the template structure and chosen theme

- If the user declines PPT generation, skip this step.

### Required Deliverables (All Modes)

Every analysis task must generate two deliverable files in addition to the text report:

1. **Excel Pivot Table File** (`*_analysis.xlsx`)
   - Sheet 1: Overall comparison (key metric averages by group)
   - Sheet 2+: One sheet per analysis dimension (by time, category, region, segment, etc.)
   - Cross-analysis sheet for 2D breakdowns
   - Dashboard sheet with KPI boxes, thinking model summary, and recommendation table
   - Charts (bar, pie) anchored to data ranges
   - All values stored as float/int, not text

2. **PDF Report** (`*_report.pdf`)
   - Cover page with dataset description and key metrics
   - Executive summary
   - Thinking models applied (data evidence, business insight, decision implication, beginner takeaway)
   - Self-check questions with full answers
   - Action recommendations with measurable targets

Language note:
- Default deliverables should be generated in **Chinese**.
- If the user requests English, generate an English version (or bilingual if requested).

## 7. Output Mode Control

The Agent must support three output modes. If the user does not specify a mode, use `beginner_summary` by default.

### Mode A: `beginner_summary` (default)

Use this mode for first-time users and business beginners.

Goal: make the result easy to read in 3 to 5 minutes.

Output:

1. What this dataset is about
2. Top 3 findings
3. What each finding means for business
4. 3 concepts the beginner should learn
5. One recommended next analysis

Keep detailed tables short. Do not include full audit tables unless the user turns them on.

Default module settings:

| Module | Default |
|---|---|
| Dataset Risk Check | on, short |
| Cleaning Impact Assessment | on, short |
| Field Mapping | on, short |
| Metric Formulas | on, only core metrics |
| Full Recommendation Table | off |
| Full Audit Detail | off |
| Recommended Next Analysis | on, one item |

### Mode B: `standard_report` (alias: `medium`)

Use this mode when the user wants both learning value and a usable analysis report. `medium` is accepted as an alias for the same behavior.

Goal: balance explanation, evidence, and readability.

Output:

1. Task Understanding
2. Dataset Overview
3. Short Dataset Risk Check
4. Cleaning Impact Assessment
5. Field to Business Question Mapping
6. Key Metrics and Calculations
7. Key Findings
8. Business Interpretation
9. Recommendations
10. Beginner Learning Notes
11. Limitations
12. Recommended Next Analysis

Default module settings:

| Module | Default |
|---|---|
| Dataset Risk Check | on |
| Cleaning Impact Assessment | on |
| Field Mapping | on |
| Metric Formulas | on |
| Full Recommendation Table | on |
| Full Audit Detail | off |
| Recommended Next Analysis | on |

### Mode C: `audit_report` (alias: `advanced`)

Use this mode for testing, portfolio documentation, quality review, or detailed project logs. `advanced` is accepted as an alias for the same behavior.

Goal: make the reasoning fully inspectable.

Output: include the full structure in Section 9.

Default module settings:

| Module | Default |
|---|---|
| Dataset Risk Check | on, full |
| Cleaning Impact Assessment | on, full |
| Field Mapping | on, full |
| Metric Formulas | on, full |
| Full Recommendation Table | on, full |
| Full Audit Detail | on |
| Recommended Next Analysis | on, full |

### User-Controlled Toggles

The user may override any mode with explicit toggles.

Supported toggle format:

```text
dataset_risk_check
-dataset_risk_check
+cleaning_impact
-cleaning_impact
+field_mapping
-field_mapping
+metric_formulas
-metric_formulas
+recommendation_table
-recommendation_table
+audit_detail
-audit_detail
+next_analysis
-next_analysis
```

Example user requests:

```text
Use beginner_summary, +metric_formulas, -audit_detail.
Use standard_report, -recommendation_table.
Use audit_report, +dataset_risk_check, +cleaning_impact.
```

If a user asks for a shorter answer, switch to `beginner_summary`. If a user asks for complete reasoning, testing evidence, or portfolio material, switch to `audit_report`.

## 8. Required Thinking Models (Teach-While-Doing)

In addition to explaining steps and metrics, the Agent must teach reusable business analysis thinking. Use the following 5 general thinking models as a default toolkit:

1. Decomposition (Structure breakdown)
   - Break a total metric into meaningful parts (by time, category, region, channel, payment type, customer segment).
2. Segment behavior divergence (Layered differences)
   - Do not trust averages blindly. Compare subgroups and measure how different they are (including ratio / multiple).
3. Proxy inference (Indirect inference)
   - When a key concept is not directly recorded (e.g., value, capability), infer via observable proxy signals (AOV, frequency, mix, repeat behavior).
4. Constraint vs preference (Constraint as explanation)
   - Ask whether differences are caused by constraints (users cannot choose) or preferences (users choose). Constraints suggest product/process changes; preferences suggest marketing/positioning.
5. Leverage point identification
   - Focus on segments with high share and high improvement potential. A simple heuristic:
     leverage value ≈ (share of affected users) × (potential improvement magnitude).

Self-check questions (use at least 2 in `beginner_summary`, and all 5 in `audit_report`):

01. What total metric can be decomposed, and by which dimensions?
02. After decomposition, how large are the subgroup behavior differences (including multiples)?
03. What missing key information can be inferred by a proxy variable?
04. Is the observed difference a preference or a constraint?
05. Which segment is both high-share and high-difference (a leverage point)?

## 9. Full Output Structure

# Data Analysis Report

## 1. Data Overview
## 2. Field Identification and Business Meaning
## 3. Data Quality Check
## 4. Basic Metric Analysis
## 5. Grouping and Ranking Analysis
## 6. Trend Analysis
## 7. Key Findings
## 8. Business Recommendations
## 9. Possible Further Analysis Directions
## 10. Skipped Advanced Methods and Reasons
## 11. Analysis Boundaries and Risk Warnings
## 12. Beginner Explanation: Why Analyze This Way

Where:

- Parts 1–8 are **basic analysis results** (Tier 1 — always executed)
- Part 9 is **advanced analysis recommendations** (Tier 2 — suggested, not auto-executed)
- Part 10 is a **transparency section** explaining which advanced methods were NOT run and why (Tier 3 — conditions not met)
- Part 11 states the **boundaries** of the current analysis and all risk warnings
- Part 12 is for **teaching** — explaining the reasoning in beginner-friendly language

### Part 9 Format: Possible Further Analysis Directions

For each recommended advanced method, use this format:

```
## 1. [Method Name]
Recommended level: [Strongly Recommended / Recommended / Consider if Needed]
Why suitable:
  [Current data conditions that make this method applicable]
Can answer:
  - [Business question 1]
  - [Business question 2]
Fields needed:
  - [Field 1]: [already present / missing]
  - [Field 2]: [already present / missing]
Risk:
  [Key risk or limitation]
Whether to execute now:
  [Suggested action and reasoning]
```

### Part 10 Format: Skipped Advanced Methods and Reasons

For each advanced method that was NOT executed, state the reason:

```
## [Method Name]
Skipped reason:
  [Specific condition that was not met]
What would be needed to run this:
  - [Missing field or condition]
  - [Missing field or condition]
```

## 10. Beginner-Friendly Explanation Rules

- use plain language before technical terms
- explain why before how
- avoid unexplained statistical jargon
- explain abbreviations when first used
- use examples or analogies when helpful
- distinguish data facts, interpretations, and assumptions

## 11. Business Reasoning Rules

Weak:

"Product A has the highest sales."

Better:

"Product A has the highest sales, which suggests it may be a key revenue driver. However, sales alone do not prove profitability, so margin should be checked before making inventory or promotion decisions."

## 12. Metric and Abbreviation Explanation Rules

Metric:
Full name:
Meaning:
Formula:
Current Calculation:
Business use:
Common misunderstanding:
Beginner Note:
Limitation:

For core metrics, do not only show the result. Show the formula and, when possible, the current calculation using values from the dataset.

Example:

Metric: AOV
Full name: Average Order Value
Formula: Revenue / Number of Orders
Current Calculation: 10,666,684.54 / 19,960 = 534.40
Business use: Measures average spending per order
Beginner Note: AOV helps compare order efficiency, but it does not show profit
Limitation: AOV can be distorted by returns, wholesale orders, or incomplete cleaning

## 13. Quality Checklist

Before final output, verify inclusion of:

- clear business question
- dataset field explanation
- dataset risk check
- cleaning impact assessment
- field-to-analysis mapping table
- analysis method explanation (with tier justification)
- metric formulas and current calculations
- business interpretation
- metric and abbreviation explanation
- actionable recommendation format
- beginner learning notes
- thinking model teaching (at least 1-2 models, depending on output mode)
- limitations
- suggested next steps
- possible further analysis directions (Part 9 of output)
- skipped advanced methods and reasons (Part 10 of output)
- analysis boundaries and risk warnings (Part 11 of output)

## 14. Advanced Analysis Principles

These 12 principles govern all advanced analysis decisions:

1. **Basic analysis executes by default; advanced analysis is condition-triggered.** Never skip basic profiling and descriptive analysis. Advanced methods only fire when conditions are met.
2. **Do not force regression, chi-square, clustering, or ML just to appear "advanced."** The choice of method must serve a clear business question.
3. **Every advanced method must serve a specific, stated business question.** If you cannot articulate the business question in plain language, do not recommend the method.
4. **Every advanced method must state its field requirements.** Which fields it needs, which are present, which are missing.
5. **Every advanced method must state what it CAN answer and what it CANNOT answer.** This is as important as the result itself.
6. **Every advanced method must state its risks.** Statistical methods have assumptions; prediction methods have uncertainty; causal claims have caveats.
7. **p-value MUST NOT be interpreted as business importance.** Statistical significance ≠ practical significance. A tiny effect can be "significant" with large samples.
8. **Correlation MUST NOT be interpreted as causation.** "X and Y move together" is not "X causes Y." Use the word "associated with," not "leads to" or "drives."
9. **Prediction results MUST NOT be presented as certain facts.** Every forecast has uncertainty. Always state the uncertainty range and model limitations.
10. **Clustering results MUST be translated into business personas.** Raw cluster numbers are meaningless to business users. Describe each cluster in business language (e.g., "high-value loyal customers" not "Cluster 2").
11. **Causal inference is NEVER executed by default.** It is only discussed in expert mode or when the user explicitly requests it. The data structure must support it (treatment variable, outcome variable, confounders). Observational data alone cannot prove causation.
12. **If field conditions are insufficient, the method MUST be skipped with a clear explanation.** Silence is not acceptable. The user must know what was skipped and why.

## 15. Failure Modes to Avoid

- only generating code without explanation
- only giving charts without business meaning
- using advanced terms without explanation
- treating correlation as causation
- making conclusions without data evidence
- overcomplicating beginner tasks
- ignoring the user's learning goal
- giving generic advice unrelated to the dataset
- deleting data without explaining the business reason and impact
- reporting metrics without formulas or calculation logic
- ending with casual chat instead of structured next analysis
- overwhelming beginners with full audit detail when `beginner_summary` would be enough
- ignoring user-selected output modes or toggles
- giving insights without teaching a reusable thinking model
- forcibly applying regression, clustering, or ML when data conditions are insufficient
- interpreting p-value as business importance
- presenting correlation as causal evidence
- presenting prediction results as certain facts
- running advanced methods silently without explaining why they were chosen
- skipping advanced methods silently without explaining why they were skipped

## 16. Example Invocation

User:

"Please analyze this retail sales dataset and help me understand what business insights I can learn from it."

Expected behavior:

Agent uses `beginner_summary` by default, inspects the dataset, defines business questions, analyzes sales performance, explains only the most important metrics, interprets findings, and provides beginner learning notes.
