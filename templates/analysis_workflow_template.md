# Analysis Workflow Template

## Step 1: Understand the Task

User goal:
Dataset type:
Business context:
Assumptions:

## Step 2: Inspect the Dataset

Rows:
Columns:
Key fields:
Missing values:
Duplicate values:
Time range:
Important field meanings:

## Step 3: Dataset Risk Check

| Issue | Why It Matters | Affected Analysis | Treatment | Remaining Risk |
|---|---|---|---|---|

## Step 4: Cleaning Impact Assessment

| Cleaning Rule | Business Reason | Rows Removed | Percentage Removed | Affected Analysis | Treatment |
|---|---|---:|---:|---|---|

## Step 5: Map Fields to Analysis Logic

| Field | Metric | Business Question | Analysis Method |
|---|---|---|---|

## Step 6: Define Business Questions

| Business Question | Related Fields | Why It Matters |
|---|---|---|

## Step 7: Choose Analysis Methods

| Business Question | Method | Why This Method |
|---|---|---|

## Step 8: Analyze

Main analysis:
Supporting analysis:
Charts or tables:
Important observations:

## Step 9: Explain Core Metrics

| Metric | Formula | Current Calculation | Business Meaning | Beginner Note | Limitation |
|---|---|---|---|---|---|

## Step 10: Interpret

Data finding:
Business meaning:
Possible reason:
Suggested action:
Risk or limitation:

## Step 11: Recommend Actions

| Finding | Business Meaning | Recommended Action | Metric to Track | Data Needed |
|---|---|---|---|---|

## Step 12: Teach the User

Concepts learned:
Metrics learned:
Methods learned:
Reusable thinking pattern:
Recommended next analysis:

## Step 13: Generate Deliverables

### Excel Pivot Table Output (required for standard_report, audit_report / medium, advanced)

| Sheet Name | Content | Pivot Row | Pivot Column | Value Metric | Chart |
|---|---|---|---|---|---|
| | | | | | |

Spec to include:
- Each sheet is one analysis dimension
- Values must be float/int, not text
- Charts placed next to source data
- Dashboard sheet with headline KPIs and visual layout

### PDF Thinking Model Extraction (required for audit_report / advanced)

Content to include:
- All 5 thinking models applied (or 2-3 for medium)
- Data evidence for each model
- Beginner learning notes
- 5 self-check questions and answers
- Executive summary with key metrics

Format: structured report, roughly 10-15 pages
