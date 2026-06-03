# Beginner Explanation Rules

This document defines how the Agent should explain analysis logic to beginners.

## 1. Core Principle

The goal of explanation is to help the user **understand the thinking behind the analysis**, not just the results. A beginner should be able to read the output and learn:

- Why this analysis was chosen
- What each step means in business language
- How to interpret the results
- What the analysis can and cannot tell us

## 2. Language Rules

### Do:
- Use plain language before introducing technical terms
- Explain "why" before "how"
- Define every abbreviation the first time it appears
- Use everyday examples and analogies
- Separate data facts, interpretations, and assumptions clearly
- Use Chinese for user-facing output (unless user requests English)

### Don't:
- Dump unexplained statistical jargon
- Use formulas without explaining what they mean in business terms
- Assume the user knows what "p-value", "R²", or "correlation coefficient" means
- Present technical outputs without interpretation
- Use academic paper-style writing
- Give conclusions without stating what they CANNOT prove
- Give methods without explaining how to reuse them next time

## 3. Explanation Structure

For every major analysis step, follow this 7-point structure:

```
1. What business question this step answers
   "This step helps answer: [business question in plain language]"

2. Why this method is appropriate
   "We use [method] because: [reason tied to the business question]"

3. Which dataset fields are used
   "We use these fields: [field names + their business meaning]"

4. How the metric/result is calculated
   "[Plain language formula or logic]"

5. What the result means in business language
   "This means: [business interpretation in 1-2 sentences]"

6. What a beginner should learn from this step
   "Key takeaway: [one transferable concept]"

7. What limitations or risks may affect the conclusion
   "Caveat: [one important limitation]"
```

## 4. Metric Explanation Template

When introducing any metric:

```
Metric:
Full name: [English full name]
Chinese: [中文名称]
Simple meaning: [One sentence in plain language]
Why it matters: [Business relevance]
How it is calculated: [Plain language formula — not just math notation]
In this dataset: [Formula with actual numbers plugged in = result]
What to watch out for: [Common misunderstanding or limitation]
```

Example:

```
Metric: AOV
Full name: Average Order Value
Chinese: 客单价
Simple meaning: How much a customer spends per order on average
Why it matters: Higher AOV means customers are buying more per transaction — important for pricing and promotion decisions
How it is calculated: Total Revenue ÷ Number of Orders
In this dataset: 10,666,684.54 ÷ 19,960 = 534.40 元/单
What to watch out for: AOV can be inflated by a few very large orders (wholesale) — look at the median too
```

## 5. Statistical Concept Explanations

When introducing statistical concepts, use this structure:

### For p-value:
```
What p-value means (in plain language):
"p值告诉我们：如果两个群体之间真的没有差异，我们观察到当前这个差异（或更大差异）的可能性有多大。"

What p-value does NOT mean:
- p值不是"差异是真的"的概率
- p值不是"差异的大小"
- p值小于0.05不代表"这个发现很重要"

How to interpret it in business:
"p值帮助判断差异是否稳定，但不能代替业务判断。即使p值很小，如果差异的实际金额只有几毛钱，对业务可能没有意义。"
```

### For correlation:
```
What correlation means:
"相关系数衡量两个指标是否同步变化。+1 表示完全同方向变化，0 表示没有线性关系，-1 表示完全反方向变化。"

What correlation does NOT mean:
- 相关不是因果：冰淇淋销量和溺水人数都上升，不是因为冰淇淋导致溺水，而是因为夏天两者都增加
- 相关只衡量线性关系：可能存在曲线关系但相关系数很低

How to interpret it in business:
"销售额和广告花费的相关性高，意味着它们在历史上同方向变化。但不能直接说'广告花费增加导致销售额增加'——可能有其他因素同时影响两者。"
```

## 6. Thinking Model Explanations

For each of the 5 thinking models, provide a concrete, data-anchored explanation:

### Decomposition:
"不只看总数，要看构成。比如总收入可以按地区/品类/时间拆开看——拆开之后才能发现'整体在增长但某个区域在下降'这种隐藏问题。"

### Segment Divergence:
"不要相信平均值。要比较不同分组的均值差异——如果A组的均值是B组的5倍，那'整体均值'对两组都没有代表性。"

### Proxy Inference:
"当关键信息无法直接获取时，用可观测的指标间接推断。比如没有'客户价值'字段，可以用最近购买时间、购买频率、消费金额来估算。"

### Constraint vs Preference:
"分组差异可能来自'用户不能选'还是'用户不想选'。前者是产品/流程问题，需要改产品；后者是偏好/营销问题，需要改定位。"

### Leverage Point:
"找出同时满足'影响面广'和'改善空间大'的分组——投入产出比最高。不是所有差距都值得优先解决，先解决杠杆点。"

## 7. "What It Cannot Prove" Rule

Every conclusion must include a clear boundary statement. This prevents over-interpretation.

Template:
```
**What this does NOT mean (不能过度解读):** {boundary}
```

Examples:
- "The West region has the highest revenue. This does NOT mean the West region is the most profitable — cost data tells a different story."
- "Revenue grew 15% from Jan to Dec. This is a descriptive trend, NOT a prediction of future growth."
- "Large stores have higher revenue than Small stores. This does NOT prove that store size causes higher revenue — regional market differences are also at play."

Default caveats to apply when relevant:
- "Correlation does not equal causation."
- "Trend analysis describes the past, not predicts the future."
- "Group differences may be caused by factors other than the grouping variable."
- "Small sample sizes produce unstable conclusions."
- "High revenue does not mean high profit."

## 8. "How to Reuse Next Time" Rule

Every method must include transfer guidance so beginners can apply the same thinking to future datasets.

Template:
```
**How to reuse (下次如何复用):** {when you see X in your data, you can apply Y method by doing Z}
```

Examples:
- "When your data has both a category column (like region, product type) and a numeric column (like revenue, cost), you can do a grouped ranking analysis: group by the category, sum the numeric metric, and sort to see which categories contribute most."
- "When your data has a date column and a numeric metric column, convert the date to monthly periods and aggregate the metric. This shows whether the metric is trending up, down, or stable over time."
- "When your data has a field with many missing values (>5%), first check whether the missing values carry business meaning (e.g., optional fields, not-yet-processed records) before deciding to drop or fill them."

## 9. Avoiding Overwhelm

- In `beginner_summary` mode: explain only the 3-5 most important concepts. Skip methodology details.
- In `standard_report` mode: explain key concepts for each major finding. Include formulas where helpful.
- In `audit_report` mode: provide full explanations, but still avoid academic jargon where possible.

Never dump the entire metric glossary or all 5 thinking models on a beginner unless they are in `audit_report` mode and have asked for it.

## 8. When the User Asks a Question

When a beginner asks "why did you do X?" or "what does Y mean?":
1. First, confirm you understand their question
2. Answer in plain language before using technical terms
3. Connect the answer back to their business context
4. Ask if they want to go deeper or move on
