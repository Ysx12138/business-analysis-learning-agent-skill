# Report Structure

This document defines the standard report structure for the Business Analysis Learning Agent Skill. All output modes (`beginner_summary`, `standard_report`, `audit_report`) follow this structure with different levels of detail.

## Report Sections

```
# Data Analysis Learning Report

## 1. What to Look at First in the Data
### 1.1 Data Scale
### 1.2 Field Types
### 1.3 Missing and Duplicate Values
### 1.4 Beginner Note: Why do a data health check before analysis?

## 2. What This Dataset Is Suitable For
### 2.1 Field Semantic Recognition
### 2.2 Computable Metrics
### 2.3 Metrics NOT Suitable
### 2.4 Beginner Note: Fields determine the upper limit of analysis

## 3. Basic Metric Analysis
Each metric uses the teaching template from `teaching_output_rules.md`:
### Metric Name
#### Analysis Result
#### What This Metric Means
#### Why Compute It
#### Formula
#### Field Sources
#### How to Interpret the Result
#### What It Cannot Prove
#### How to Reuse Next Time

## 4. Grouping and Ranking Analysis
Each grouping uses the teaching template:
#### Analysis Result
#### Why Group by This Field
#### What Problem This Method Solves
#### Calculation Logic
#### How to Interpret the Result
#### Business Application
#### Common Beginner Mistake
#### How to Reuse Next Time

## 5. Trend Analysis
Each trend uses the teaching template:
#### Analysis Result
#### Why Analyze by Time
#### Time Field Used
#### Numeric Metric Used
#### Calculation Logic
#### What Rise or Decline Means
#### Is This a Prediction? (No.)
#### How to Reuse Next Time

## 6. Key Findings
Each finding uses the teaching template:
#### Finding
#### Evidence Source
#### What It Means
#### What It Does NOT Mean
#### How to Verify Further

## 7. Business Recommendations
Each recommendation:
#### Recommendation
#### Based on Which Finding
#### Why This Is Reasonable
#### What to Confirm Before Acting
#### Risk

## 8. Further Analysis Directions
What additional analyses the current data could support, and why.

## 9. Skipped Analyses and Reasons
Which analyses were not done, and why they are not suitable for the current data.

## 10. What You Learned in This Analysis
In beginner-accessible language:
- Methods used in this analysis
- What each method solves
- What to look for first when seeing similar data next time
- Which conclusions should not be over-interpreted
```

## Mode-Based Detail Control

| Section | beginner_summary | standard_report | audit_report |
|---------|-----------------|-----------------|--------------|
| 1. Data Health Check | Short (3-5 lines) | Full profile table | Full + risk details |
| 2. Field Semantics | Top 5 fields only | All fields | All + confidence + evidence |
| 3. Basic Metrics | Top 3 metrics, short explanation | All matched metrics with formula | All + derived + skipped reasons |
| 4. Grouping Analysis | Top 1-2 groupings | All groupings | All + method reasoning |
| 5. Trend Analysis | Only if strong trend | Full trend table | Full + caveats |
| 6. Key Findings | Top 3, short | All findings | All + full teaching template |
| 7. Recommendations | Top 1 | All | All + risk per recommendation |
| 8. Further Analysis | 1 suggestion | 2-3 suggestions | Full list with prerequisites |
| 9. Skipped Analyses | Mention 1-2 | List all skipped | Full explanation per skipped |
| 10. Learning Summary | 3 concepts + 1 pattern | All concepts + 3 patterns | Full with self-check questions |

## Teaching Annotations Per Section

Every section that contains analysis output must carry these annotations (inline, not as separate blocks):

1. **Method tag** — which analysis method produced this output
2. **Field tag** — which fields were used
3. **Boundary tag** — what this finding cannot prove
4. **Reuse tag** — how to apply this method next time

These annotations should be part of the natural language flow, not separate boilerplate sections.

Example (Chinese):
```
按区域分组后，West 区营收（220K）显著高于 North 区（95K），差距 2.3 倍。
这用的是"分组排名分析"方法，输入字段是 region（地理区域）和 revenue（营收）。
这说明区域是营收差异的重要维度，但不能证明区域本身导致了差异——
门店规模和区域经济水平可能是同时影响两者的因素。
下次当你看到数据中同时有类别字段和数值字段时，就可以用同样的方法做分组对比。
```
