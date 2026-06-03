# Advanced Analysis Method Trigger Rules

This document defines when to recommend, execute, or skip each advanced analysis method.

All methods here are **Tier 2 or Tier 3** — they are NOT automatically executed.
See `analysis_method_selection.md` for Tier 1 (basic) methods and `analysis_boundaries.md` for overarching risk principles.

---

## 1. Correlation Analysis

**Applicable questions:**
- Do two or more numeric metrics move together?
- Do ad spend and sales change in sync?
- Is there a relationship between discount rate and AOV?
- Which numeric metrics are strongly related?

**Trigger conditions:**
- At least 2 numeric fields exist
- The numeric fields are NOT IDs, codes, or sequence numbers
- Sample size > 30 rows (recommended)

**Required fields:**
- At least two numeric business fields

**Default execution:** No
-- Tier 1 (basic analysis) does NOT include correlation.
-- In advanced mode, may be recommended.
-- Can be executed in `audit_report` mode or when user explicitly asks.

**User confirmation needed:** Not mandatory, but risks MUST be explained.

**Output:**
- Correlation coefficient matrix
- High-correlation field pairs (|r| > 0.7)
- Positive / negative correlation explanation
- Business meaning of observed relationships

**Risk warnings:**
- Correlation ≠ causation
- Outliers can distort the correlation coefficient
- ID codes should not participate in correlation analysis
- High correlation may be due to a common third variable (confounding)
- Pearson's r assumes linear relationship — non-linear relationships may be missed

**When NOT applicable:**
- Fewer than 2 numeric fields
- Numeric fields are actually IDs or codes
- Sample size too small

---

## 2. t-test

**Applicable questions:**
- Is the difference in average between two groups statistically meaningful?
- Do members and non-members have significantly different AOV?
- Do purchasing and non-purchasing users have significantly different session durations?
- Does Group A and Group B have significantly different sales?

**Trigger conditions:**
- A binary (two-category) grouping field exists
- A numeric metric field exists
- Both groups have adequate sample sizes

**Required fields:**
- Binary grouping field (2 unique values)
- Numeric metric field

**Default execution:** No
-- Not executed in beginner or standard modes.
-- Only in `audit_report` mode or when user explicitly asks "is this difference significant?"

**User confirmation needed:** Recommended — confirm the grouping field and metric field.

**Output:**
- Sample sizes for both groups
- Group means
- t-statistic
- p-value
- Whether the difference is statistically significant
- Business interpretation of the result

**Risk warnings:**
- p-value does NOT measure business importance — a tiny difference can be "significant" with large samples
- "Significant" ≠ "meaningful" in business terms
- Outliers can substantially affect group means
- The t-test assumes independence of observations — repeated measures or matched samples need different tests
- The t-test assumes approximate normality — heavily skewed data may need transformation

**When NOT applicable:**
- Grouping field is not binary (use ANOVA or chi-square instead)
- Metric field is not a continuous numeric variable
- Both groups have very small sample sizes
- Observations are not independent

---

## 3. Chi-square Test

**Applicable questions:**
- Is there a statistical association between two categorical variables?
- Is channel associated with conversion?
- Is region associated with churn?
- Is membership tier associated with purchase category?
- Is gender associated with product preference?

**Trigger conditions:**
- Two categorical fields exist, OR one categorical field + one binary outcome field
- Each combination has adequate frequency (>5 expected count per cell, recommended)

**Required fields:**
- Categorical field A
- Categorical field B (can be binary)

**Default execution:** No
-- Not executed by default.
-- Can be recommended in advanced mode.
-- Execute when user explicitly asks "is X related to Y?" or "is X significantly associated with Y?"

**User confirmation needed:** Recommended — confirm both categorical fields.

**Output:**
- Contingency table (cross-tab)
- Chi-square statistic
- p-value
- Whether a significant association exists
- Business interpretation

**Risk warnings:**
- Chi-square only indicates association, NOT causation
- With very large samples, even tiny differences become "significant"
- With very small samples, results are unstable
- Too many categories make interpretation difficult
- Low expected frequencies in cells violate the test assumption

**When NOT applicable:**
- Fewer than two categorical fields
- Cell frequencies too low
- Too many categories with no business meaning
- One variable has only 1 unique value

---

## 4. Linear Regression

**Applicable questions:**
- What factors influence a numeric outcome variable?
- What is the direction and strength of each factor's influence?
- Is sales affected by ad spend, discount rate, and foot traffic?
- What is the relationship between AOV and user tier, purchase frequency, and promotions?

**Trigger conditions:**
- A clear numeric target (outcome) variable exists
- At least one predictor variable exists
- Sample size is adequate (rule of thumb: 10-20 observations per predictor)
- Target variable is NOT an ID, code, or categorical field
- User has a reasonably clear analytical goal

**Required fields:**
- Numeric target variable
- One or more predictor variables

**Default execution:** No
-- Not executed by default.
-- Only in `audit_report` mode or when user explicitly asks about "what factors influence X?"

**User confirmation needed:**
- MUST confirm the target variable
- Should confirm the predictor variables

**Output:**
- Regression equation
- Coefficients (direction and magnitude)
- p-values for each coefficient
- R² (explained variance)
- Variable influence direction (positive / negative)
- Business interpretation
- Model limitations

**Risk warnings:**
- Regression by default captures association, NOT causation
- Multicollinearity (correlated predictors) makes coefficient interpretation unreliable
- Outliers can heavily influence coefficients
- Omitted variable bias — missing important predictors distorts all estimates
- Categorical variables need proper encoding (dummy variables)
- Extrapolation beyond the observed data range is unreliable
- R² does not tell you whether the model is "correct"

**When NOT applicable:**
- No clear target variable
- Target variable is not numeric
- Sample size too small relative to number of predictors
- Most fields are IDs or codes

---

## 5. Logistic Regression / Classification

**Applicable questions:**
- Predict a binary outcome, or analyze which factors are associated with that outcome.
- Will a user churn?
- Will a user make a purchase?
- Will a lead convert?
- Is an order at risk?

**Trigger conditions:**
- A clear binary target variable exists
- Multiple usable feature fields exist
- Sample size is adequate
- Class distribution is not extremely imbalanced (e.g., not 99% vs 1%)

**Required fields:**
- Binary target variable
- Feature fields (numeric or properly encoded categorical)

**Default execution:** No
-- Not executed by default.
-- Only when user explicitly asks for prediction or classification.

**User confirmation needed:**
- MUST confirm the target variable
- MUST explain train/test split approach

**Output:**
- Model objective
- Fields used
- Train/test split description
- Accuracy, recall, precision, F1
- AUC (if applicable)
- Important feature explanation (if available)
- Business interpretation

**Risk warnings:**
- Predictive ability ≠ causal explanation
- Class imbalance inflates accuracy — a model predicting "no churn" for everyone can appear 90% accurate
- Never evaluate on training data — must use a held-out test set
- Model results need business context to interpret
- Features that are "predictive" may not be "actionable"
- Temporal leakage — future information in training data makes predictions unreliable

**When NOT applicable:**
- No target variable
- Target variable is not binary
- Sample size too small
- Extreme class imbalance without handling

---

## 6. Clustering Analysis

**Applicable questions:**
- Group customers, products, stores, or orders into segments based on similar characteristics.
- Can customers be grouped into value tiers?
- Can products be grouped into sales performance types?
- Can stores be grouped into operational types?

**Trigger conditions:**
- Multiple numeric feature fields exist
- Sample size is adequate (> 50, recommended)
- Fields are NOT IDs or codes
- There is a genuine business need for segmentation

**Required fields:**
- Multiple numeric feature fields
- Optional: customer ID, product ID, or store ID as labels

**Default execution:** No
-- Not executed by default.
-- Can be suggested in recommendation mode.
-- Can be executed in `audit_report` mode.

**User confirmation needed:** Recommended — confirm the segmentation target and feature fields.

**Output:**
- Number of clusters (K)
- Sample size per cluster
- Feature means per cluster
- Business persona per cluster (describe in plain language)
- Segment interpretation

**Risk warnings:**
- Clustering results are NOT natural truths — they depend on K, algorithm, and standardization
- K must be justified — do not pick arbitrarily
- Standardization (z-score) substantially affects results — state how features were scaled
- Clusters MUST be translated into business language — "Cluster 2 has high AOV and high frequency" not "Cluster 2 has centroids at (3.5, 2.1)"
- Different clustering algorithms (KMeans, DBSCAN, hierarchical) give different results

**When NOT applicable:**
- Only one numeric field
- Fields are mostly IDs or codes
- Sample size too small
- No clear segmentation objective

---

## 7. RFM Analysis

**Applicable questions:**
- Customer value segmentation for transactional data.
- Which customers purchased recently?
- Which customers purchase frequently?
- Which customers spend the most?
- Which customers are high-value, dormant, or at-risk?

**Trigger conditions:**
- Customer ID field exists
- Order/purchase date field exists
- Monetary field exists (order amount, sales, payment amount)
- A customer may appear in multiple rows (repeated transactions)

**Required fields:**
- Customer ID
- Transaction/order date
- Monetary amount field

**Default execution:** No
-- If fields match with high confidence, may auto-execute in `audit_report` mode.
-- In beginner/standard modes, recommend but do not auto-execute.

**User confirmation needed:** Not mandatory if field confidence is high. Required if field names are non-standard.

**Output:**
- Recency (days since last purchase)
- Frequency (number of purchases in period)
- Monetary (total spend in period)
- RFM scores (1-5 scoring per dimension)
- Customer segments (e.g., Champions, Loyal, At Risk, Hibernating, Lost)
- Segment interpretation with business language
- Operational recommendations per segment

**Risk warnings:**
- RFM is designed for transactional data — not applicable to all datasets
- No customer ID → cannot compute RFM
- No date field → cannot compute Recency
- No monetary field → cannot compute Monetary
- RFM segments need business calibration — the 1-5 scoring thresholds should align with business context
- RFM is descriptive, not predictive — it shows current state, not future behavior

**When NOT applicable:**
- Not transactional data
- No customer ID
- No date field
- No monetary field
- Each customer appears only once

---

## 8. Cohort Analysis

**Applicable questions:**
- Analyze retention or repeat purchase behavior of users who first appeared or first purchased in different time periods.
- Which month's new customers have the best quality?
- How does retention differ across acquisition cohorts?
- Do new users continue to purchase in month 2, 3, 4?

**Trigger conditions:**
- Customer ID field exists
- Date/time field exists
- A customer may appear multiple times
- Time span is adequate (at least 2-3 periods of observation)

**Required fields:**
- Customer ID
- Date/time field
- Transaction or behavior records

**Default execution:** No
-- Not executed by default.
-- Suggest in recommendation mode.
-- Execute when user is interested in retention or repeat purchase.

**User confirmation needed:** Recommended — confirm the cohort definition (e.g., first purchase month).

**Output:**
- Cohort groups (by acquisition period)
- Retention matrix (cohort × period)
- Repeat purchase matrix (if applicable)
- Cohort comparison
- Business interpretation

**Risk warnings:**
- Time span too short → cohort analysis is meaningless (need at least 2-3 post-cohort periods)
- Unstable customer IDs (e.g., guest checkout creating new IDs) distort retention
- Missing transaction data can make a customer appear "retained" or "lost" incorrectly
- Declining retention does not necessarily mean the product worsened — seasonality, cohort size, or market changes can be factors

**When NOT applicable:**
- No customer ID
- No date field
- Each customer appears only once
- Time span too short (single period)

---

## 9. Seasonality Analysis

**Applicable questions:**
- Identify trend, seasonal fluctuations, and irregular fluctuations in a time series.
- Does sales exhibit seasonality?
- Which months are naturally higher or lower?
- Is a current decline a trend issue or a seasonal dip?

**Trigger conditions:**
- A date/time field exists
- A continuous numeric metric exists
- Time span covers multiple seasonal cycles (at least 2 years for annual seasonality)
- Time frequency is relatively stable

**Required fields:**
- Date/time field
- Numeric metric field

**Default execution:** No
-- Not executed by default.
-- Recommend when time span is adequate (>2 years).
-- Execute when user is interested in cyclical patterns.

**User confirmation needed:** Recommended — confirm the target metric and time granularity.

**Output:**
- Trend component
- Seasonal component
- Residual (irregular) component
- Cycle interpretation
- Business recommendations

**Risk warnings:**
- Seasonality analysis is NOT forecasting — it decomposes historical patterns
- Time span too short → seasonal patterns are unreliable
- Missing periods need to be handled (interpolation introduces assumptions)
- Irregular frequency can distort results
- Structural breaks (e.g., COVID, policy changes) can make historical seasonality patterns irrelevant

**When NOT applicable:**
- No date field
- Time span too short (< 2 seasonal cycles)
- Data frequency is inconsistent
- Numeric metric is not continuous

---

## 10. Time Series Forecasting

**Applicable questions:**
- Forecast future trends based on historical time series patterns.
- What might next month's sales be?
- How might order volume change over the next few periods?
- Is there a sustained growth or decline trend?

**Trigger conditions:**
- A date/time field exists
- A continuous numeric metric exists
- Historical period is adequate (rule of thumb: at least 30-50 data points)
- Time frequency is stable
- User explicitly requests forecasting

**Required fields:**
- Date/time field
- Numeric metric field

**Default execution:** NO — NEVER execute by default.
-- MUST require user explicit confirmation.
-- MUST explain uncertainty.

**User confirmation needed:** MANDATORY.
-- MUST confirm the target metric.
-- MUST confirm the forecast horizon.
-- MUST confirm the user understands this is a projection, not a fact.

**Output:**
- Historical trend
- Forecast results
- Prediction interval (if available)
- Uncertainty explanation
- Risk warnings (prominently displayed)

**Risk warnings:**
- Forecasts rely on the assumption that historical patterns will continue — structural changes invalidate them
- Too few data points → forecasts are highly unreliable
- Black swan events (pandemic, regulatory change, competitor entry) cannot be inferred from historical data
- Forecasts are NOT definitive conclusions — always state the uncertainty range
- Out-of-sample forecast error grows with horizon — longer forecasts are less reliable
- "The model predicts X" implies false certainty — use "the model projects X, with a likely range of Y to Z"

**When NOT applicable:**
- No date field
- Too few data points (< 30)
- Time frequency is inconsistent
- User has not explicitly requested forecasting

---

## 11. Sentiment Analysis

**Applicable questions:**
- Perform coarse-grained sentiment orientation analysis on text fields such as reviews, feedback, and comments.
- Is overall user feedback positive or negative?
- Which reviews likely express dissatisfaction?
- Does sentiment differ across products or channels?

**Trigger conditions:**
- A text field exists
- The text field appears to contain reviews, feedback, comments, or notes
- Text length and sample size are adequate
- Text is in a language the Agent can reasonably process

**Required fields:**
- Text field (reviews, feedback, comments)
- Optional: product, channel, date, or other grouping fields

**Default execution:** No
-- Not executed by default.
-- Suggest in recommendation mode.
-- Execute when user explicitly wants to analyze reviews/comments.

**User confirmation needed:** Recommended — confirm the text field meaning.

**Output:**
- Sentiment distribution (positive / neutral / negative)
- Positive/negative examples
- Sentiment comparison by group (product, channel, etc.)
- Text analysis risk statement

**Risk warnings:**
- Generic sentiment analysis may not suit specific industries (e.g., "sick" in gaming reviews = good, in healthcare reviews = bad)
- Sarcasm, irony, and short text are prone to misclassification
- Mixed-language text (Chinese + English) may reduce accuracy
- Sentiment analysis results should be spot-checked with manual review
- Rating-based sentiment (1-5 stars) is more reliable than text-based for structured review data

**When NOT applicable:**
- No text field
- Text field is just codes or short labels
- Sample size too small

---

## 12. Causal Inference

**Applicable questions:**
- When there is a clear business hypothesis and variable design, attempt to analyze whether a treatment variable influences an outcome variable.
- Did a specific campaign actually increase conversion?
- Did a discount cause a change in sales?
- Did a new strategy improve retention?

**Trigger conditions:**
- A clear treatment variable exists (e.g., campaign exposure, policy change)
- A clear outcome variable exists
- Possible confounder variables can be identified
- User provides explicit business hypothesis
- Data structure supports causal analysis (e.g., pre-post, treatment-control groups)

**Required fields:**
- Treatment variable (binary: treated vs not treated)
- Outcome variable
- Confounder variables (at minimum, acknowledge which are missing)

**Default execution:** NEVER — do NOT execute by default.
-- This is expert-mode only.
-- In routine business analysis, only suggest the method conceptually.

**User confirmation needed:** MANDATORY.
-- MUST confirm the causal question.
-- MUST confirm the treatment and outcome variable definitions.
-- MUST explain that observational data alone cannot prove causation.

**Output:**
- Causal question definition
- Treatment variable
- Outcome variable
- Control variables
- Method assumptions (explicitly listed)
- Result interpretation
- STRONG risk warning (must be prominent)

**Risk warnings:**
- Causal inference CANNOT be automated from field names alone — it requires domain knowledge and explicit assumptions
- Observational data (no randomization) makes causal claims inherently uncertain
- Unmeasured confounders can completely invalidate results
- "X is associated with Y" is NOT "X causes Y" — do not dress up correlation as causation
- Even with advanced methods (DID, IV, RDD, propensity score matching), residual confounding is always possible
- The burden of proof for causal claims is MUCH higher than for descriptive claims

**When NOT applicable:**
- User has no clear causal question
- No treatment variable
- No outcome variable
- Confounders cannot be identified or acknowledged as missing
- Data is simple cross-sectional descriptive data
- User does not understand or accept the methodological limitations

---

## Summary: Default Execution Rules

| Method | Tier | Default Execute? | User Confirm? | Minimum Fields |
|--------|------|-----------------|---------------|----------------|
| Correlation | 2 | No (recommend) | Not mandatory | 2 numeric |
| t-test | 2 | No (conditional) | Recommended | Binary group + numeric |
| Chi-square | 2 | No (recommend) | Recommended | 2 categorical |
| Linear Regression | 2 | No (conditional) | MUST confirm target | Numeric target + 1+ predictor |
| Logistic Regression | 2 | No (conditional) | MUST confirm target | Binary target + features |
| Clustering | 2 | No (recommend) | Recommended | Multiple numeric |
| RFM | 2 | Auto if high-confidence fields | Not mandatory if high confidence | Customer ID + date + amount |
| Cohort | 2 | No (recommend) | Recommended | Customer ID + date |
| Seasonality | 2 | No (recommend) | Recommended | Date + numeric |
| Forecasting | 2 | NEVER auto | MANDATORY | Date + numeric |
| Sentiment | 2 | No (recommend) | Recommended | Text field |
| Causal Inference | 3 | NEVER auto | MANDATORY | Treatment + outcome + confounders |
