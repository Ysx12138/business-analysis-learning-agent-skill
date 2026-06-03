# MVP Evaluation Checklist

Use this checklist to validate whether one run meets minimum quality.

## A. Task Understanding

- [ ] Output mode is stated or can be inferred
- [ ] Output length matches selected mode
- [ ] Business goal is clearly stated
- [ ] Dataset context is summarized
- [ ] Assumptions are explicitly stated when needed

## B. Dataset Interpretation

- [ ] Key fields are identified
- [ ] Field business meanings are explained
- [ ] Data quality checks are mentioned (missing values, duplicates, types)
- [ ] Dataset risk check is included
- [ ] Each relevant risk explains why it matters and which analysis it affects
- [ ] Field-to-metric-to-business-question mapping is included

## C. Method Reasoning

- [ ] Business questions are listed
- [ ] Method is mapped to each business question
- [ ] Method choice is justified
- [ ] Each major step explains the business question it answers
- [ ] Each major step explains fields used and beginner learning point

## D. Cleaning Logic

- [ ] Cleaning rules are listed
- [ ] Business reason is explained for each cleaning rule
- [ ] Rows removed and percentage removed are shown when possible
- [ ] The output states whether removed data should be separated for another analysis
- [ ] The effect of cleaning on conclusions is explained

## E. Findings and Business Interpretation

- [ ] Key findings are evidence-based
- [ ] Business interpretation is provided for each major finding
- [ ] Facts, interpretation, and assumptions are separated
- [ ] Limitations are explicitly stated

## F. Metrics and Abbreviations

- [ ] Metrics are explained in plain language
- [ ] Abbreviations are expanded at first use
- [ ] Core metrics include formula
- [ ] Core metrics include current calculation when data is available
- [ ] Common misunderstanding is addressed for key metrics
- [ ] Metric limitations are stated

## G. Recommendations

- [ ] Recommendations follow Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed
- [ ] Recommendations are tied to dataset evidence
- [ ] Recommended next analysis is structured, not conversational

## H. Beginner Learning Outcome

- [ ] Beginner learning notes are included
- [ ] Reusable thinking pattern is summarized
- [ ] Suggested next learning step is provided
- [ ] At least 1 thinking model is taught (see `templates/thinking_models_template.md`)

## I. Fail Conditions

Mark as failed if any of the following happens:

- [ ] Output ignores the selected output mode
- [ ] Output gives full audit detail when `beginner_summary` was requested
- [ ] Output only contains code/charts without explanation
- [ ] Output uses unexplained jargon
- [ ] Output makes causal claims without evidence
- [ ] Output provides generic advice not tied to dataset
- [ ] Output deletes data without explaining business reason and impact
- [ ] Output reports core metrics without formulas or calculation logic
- [ ] Output ends with casual chat instead of structured recommended next analysis

## Result

- [ ] PASS
- [ ] FAIL

Reviewer:
Date:
Case:
Notes:
