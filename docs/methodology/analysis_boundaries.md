# Analysis Boundaries and Risk Principles

This document defines the analytical boundaries of this Skill — what it can and cannot claim, and the risk principles that govern all output.

## 1. Skill Scope Boundary

This Skill performs **descriptive business analysis and metric-driven interpretation**. It is NOT a statistical modeling platform.

### Within scope (Tier 1 — always available):
- Data profiling and quality assessment
- Descriptive statistics (mean, median, std, quartiles, sum, count)
- Grouped aggregation and ranking
- Trend observation (aggregated month-over-month changes)
- Metric computation from a predefined registry
- Business interpretation of observed patterns
- Beginner-friendly explanation and teaching

### Outside scope unless explicitly requested by user (Tier 2):
- Correlation analysis
- Statistical testing (t-test, chi-square)
- Regression modeling
- Clustering
- RFM / cohort / seasonality analysis
- Forecasting
- Sentiment analysis

### Outside scope — expert-mode only (Tier 3):
- Causal inference

### Permanently outside scope (not implemented):
- Deep learning / neural networks
- NLP beyond coarse sentiment
- Anomaly detection with statistical process control
- Survival analysis
- Bayesian modeling
- Reinforcement learning
- Real-time streaming analytics

## 2. Interpretation Boundaries

These rules govern how analysis results must be described.

### Correlation
- ✅ Allowed: "X and Y move in the same direction" / "X and Y are associated with each other"
- ❌ Forbidden: "X causes Y" / "X leads to Y" / "X drives Y" / "X is the reason for Y"

### Statistical Significance
- ✅ Allowed: "The difference between groups is statistically significant (p < 0.05)" + explanation
- ❌ Forbidden: "This is a very important finding because p < 0.05" / ending analysis at "p < 0.05"

### Prediction
- ✅ Allowed: "Based on historical patterns, the projected range for next month is X to Y"
- ❌ Forbidden: "Next month sales will be X" / "The model predicts X with certainty"

### Clustering
- ✅ Allowed: "Customers in this group tend to have high AOV and frequent purchases — they behave like premium loyalists"
- ❌ Forbidden: "Cluster 2 has centroids at (3.5, 2.1)" (this is meaningless to business users)

### Causal Claims
- ✅ Allowed: "After the campaign launch, Group A (exposed) showed a larger increase than Group B (control), suggesting the campaign may have contributed to the change"
- ❌ Forbidden: "The campaign caused a X% increase in sales"

## 3. p-value Interpretation Rules

p-value is one of the most commonly misunderstood statistical concepts. When p-values appear in output, these rules MUST be followed:

1. **Always explain what p-value means in plain language.** "p-value tells us how surprising the observed difference would be if there were truly no difference between groups."

2. **Always explain what p-value does NOT mean:**
   - p-value is NOT the probability that the null hypothesis is true
   - p-value is NOT the probability that the result is "real"
   - A small p-value does NOT mean the effect is large
   - A large p-value does NOT mean there is no effect

3. **Always contextualize with effect size.** "The difference is statistically significant (p = 0.02), but the actual gap is only $0.50 per order, which may not be meaningful for business decisions."

4. **Never use p < 0.05 as a mechanical decision rule.** "p = 0.049 is not meaningfully different from p = 0.051. Both should be interpreted with context, not a binary cutoff."

## 4. Data Condition Mandates

These are the minimum thresholds before an advanced method can be considered:

| Method | Minimum Sample | Minimum Fields | Other Requirements |
|--------|---------------|----------------|-------------------|
| Correlation | 30+ rows | 2 numeric | Fields must not be IDs |
| t-test | 10+ per group | 1 binary + 1 numeric | Groups independent |
| Chi-square | 5+ expected per cell | 2 categorical | Cells not empty |
| Linear Regression | 10-20 per predictor | 1 numeric target + 1+ predictor | No perfect collinearity |
| Logistic Regression | 10-20 per predictor per class | 1 binary target + features | Class balance not extreme (< 95/5) |
| Clustering | 50+ rows | 3+ numeric features | Features standardized |
| RFM | 100+ transactions | Customer ID + date + amount | Repeated transactions |
| Cohort | 2+ time periods | Customer ID + date | Repeated appearances |
| Seasonality | 2+ seasonal cycles | Date + numeric metric | Stable frequency |
| Forecasting | 30+ data points | Date + numeric metric | Stable frequency |
| Sentiment | 50+ text records | Text field | Adequate text length |
| Causal Inference | Depends on method | Treatment + outcome + confounders | Clear identification strategy |

## 5. Transparency Mandates

The following MUST be transparent in every output:

1. **What was done and why** — Every analysis step must have a stated reason.
2. **What was NOT done and why** — Methods that were skipped must be listed with reasons (output Part 10).
3. **What the data CAN support** — If data is insufficient for a method, explain what additional data would be needed.
4. **Where uncertainty exists** — Every finding that relies on inference or projection must acknowledge uncertainty.
5. **What assumptions were made** — Data cleaning choices, metric definitions, and analytical assumptions must be stated.

## 6. Risk Escalation Rules

When a user requests a risky analysis, the Agent must escalate appropriately:

### Level 1: Standard risk (describe and proceed)
- Correlation analysis
- Grouped comparison
- Descriptive statistics

### Level 2: Elevated risk (warn and confirm before proceeding)
- Regression analysis
- t-test / chi-square
- Clustering
- RFM / cohort
- Forecasting

### Level 3: High risk (require explicit user confirmation with understanding)
- Causal inference
- Any claim that "X causes Y"
- Any policy or investment recommendation based solely on this analysis
