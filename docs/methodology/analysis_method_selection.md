# Analysis Method Selection

This document explains which analysis methods are triggered under which data conditions, what code runs, what the output is, and what risks apply.

## Analysis Method Layering

All methods are organized into three tiers:

### Tier 1: Default Basic Analysis (Always Execute)

These methods run on every dataset by default. They answer "what is in the data?"

- Data profiling
- Field semantics recognition
- Missing/duplicate/outlier checks
- Basic metric computation (metric registry matching)
- Grouped aggregation and ranking
- Trend analysis (when date field exists)
- Descriptive statistics
- Data quality risk warnings
- Business interpretation and beginner explanation

### Tier 2: Advanced Analysis (Recommend, Do Not Auto-Execute)

These methods are recommended when data conditions are met, but NOT automatically executed. Each recommendation must explain why it is suitable, what it can/cannot answer, and what the risks are.

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

See `advanced_method_triggers.md` for detailed trigger rules for each method.

### Tier 3: Expert Analysis (Never Default, Strictly Conditional)

These methods require explicit user confirmation, clear variable definition, and adequate data structure.

- Causal inference — NEVER execute without explicit user request and defined treatment/outcome variables

## Tier 1: Basic Method Selection Rules

For each method, the selection logic considers: (a) whether data conditions are met, (b) why the method is suitable for the current data, (c) why it might be skipped, and (d) what beginners should understand about it.

| 数据条件 | 分析方法 | 代码实现 | 输出结果 | 风险提示 | 为什么适合 (Why) | 为什么跳过 (Why Skip) | 初学者理解 (Beginner Note) |
|----------|----------|----------|----------|----------|------------------|---------------------|---------------------------|
| 类别字段 + 数值字段同时存在 | 分组排名分析 | `df.groupby(cat_col)[num_col].agg(["sum","mean","count"]).sort_values("sum", ascending=False)` | Top/Bottom 排名表 + finding（含差距倍数） | 类别过多时排名表过长，限制前 3 个类别 × 前 2 个数值；空组被 pandas 排除 | 类别字段代表一个可拆解的维度（如区域、品类），数值字段代表可衡量的业务结果（如营收、成本）。分组排名能直接展示"谁贡献多、谁贡献少"。 | 没有合适的类别字段（无 object 列、唯一值太多或太少），或数值字段在排除后为空。 | 当你想知道"哪个部门/区域/产品卖得最多"时，就用分组排名。下次看到数据中有类别列和数字列，就可以用这个方法。 |
| 时间字段（datetime64）+ 数值字段同时存在 | 趋势分析 | `df["_period"] = df[date_col].dt.to_period("M").astype(str); df.groupby("_period")[num_col].sum()` | 月度趋势表 + finding（首尾变化百分比） | 不是时间序列预测；首尾比较不能代表整体趋势；数据跨度过短时无意义 | 趋势是商业分析中最基本的问题——"业务是在变好还是变坏？"月度趋势图能直观回答这个问题。 | 数据集中没有日期字段，或日期字段无法被 pandas 解析为 datetime64 类型。 | 趋势分析描述过去的变化方向，不等于预测未来。下次看到数据中有日期列，先按月汇总看趋势——上涨、下跌、还是波动？ |
| 数值字段存在 | 分布分析 | `df[num_col].describe()` | count, mean, std, min, 25%, 50%, 75%, max | 限制前 2 个数值字段；极端值影响均值和标准差 | 描述统计让你快速了解数值字段的"长相"——中心在哪、散布多宽、有没有极端值。这些是后续所有分析的基础。 | 数值字段在排除后为空。 | 均值会被极端值拉偏——如果 max 是 min 的 100 倍，中位数比均值更能代表"典型值"。下次先看 min/max/median 再决定用什么统计量。 |
| Clicks + Impressions 字段同时存在 | CTR 计算 | `SUM(Clicks) / SUM(Impressions) × 100` | 点击率百分比 | Impressions 为 0 时跳过 | 衍生指标。CTR 衡量广告素材的吸引力。 | 需要 Clicks 和 Impressions 两个字段同时存在，缺一不可。 | CTR 高只说明素材吸引点击，不说明点击后是否转化。下次评估广告效果时，CTR 和转化率要一起看。 |
| Spent + Clicks 字段同时存在 | CPC 计算 | `SUM(Spent) / SUM(Clicks)` | 单次点击成本 | Clicks 为 0 时跳过 | 衍生指标。CPC 衡量每次点击的成本效率。 | 需要 Spent 和 Clicks 两个字段同时存在。 | CPC 低不等于效果好——如果点击后没人转化，低成本点击也是浪费。 |
| Total_Revenue + Net_Income 字段同时存在 | 利润率计算 | `(Net_Income / Total_Revenue) × 100` | 利润率百分比 | 口径不一致时结果失真；取最后一个年份/期间的值 | 衍生指标。利润率衡量"每赚 100 元收入，能留下多少利润"。 | 需要收入字段和利润字段同时存在。 | 不同行业的利润率差异很大（零售 2-5%，SaaS 70-80%），跨行业对比没有意义。 |
| Total_Liabilities + Total_Assets 字段同时存在 | 负债率计算 | `(Total_Liabilities / Total_Assets) × 100` | 负债率百分比 | 取最后一个年份/期间的值 | 衍生指标。负债率衡量公司的财务杠杆。 | 需要负债字段和资产字段同时存在。 | 负债率高不一定危险——如果能用借来的钱赚到比利息更高的回报，负债是好的。 |
| Total_Conversion + Clicks 字段同时存在 | 转化率计算 | `SUM(Total_Conversion) / SUM(Clicks) × 100` | 转化率百分比 | Clicks 为 0 时跳过 | 衍生指标。转化率衡量"点击后有多少人完成了目标动作"。 | 需要转化字段和点击字段同时存在。 | 转化率的定义因业务不同（购买、注册、下载），跨数据对比时先确认转化定义是否一致。 |
| 负值比例 > 1% | 数据质量风险检查 | `(df[col] < 0).sum() / len(df)` | 风险告警 | 部分业务字段允许负数（如退货金额、利润调整），会被误告警 | 负值检测帮助发现数据中的异常——营收和成本通常不应为负数。 | 不跳过质量检查：数据质量检查是 Tier 1 必须执行的。 | 不是所有负值都是错误——退货、退款、利润亏损都可能产生合法的负数。先理解字段含义再判断。 |
| 零值比例 > 30% 且字段名含 spent/cost | 数据质量风险检查 | `(df[col] == 0).sum() / len(df)` | 风险告警 | 阈值 30% 是硬编码的；如果有意投放了零预算广告系列，会被误告警 | 大量零值可能说明数据不完整或统计口径问题。 | 不跳过质量检查。 | 零值是数据中最容易忽视的问题——大量零值会拉低均值，掩盖真实活跃数据的特征。 |
| 缺失率 > 5% | 数据质量风险检查 | `df[col].isnull().sum() / len(df)` | 风险告警 | 缺失可能有业务含义（如未填写的可选字段） | 高缺失率会显著影响分析的样本量和可信度。 | 不跳过质量检查。 | 缺失值不一定是"数据错误"——可选字段、隐私字段可能天生就有高缺失率。分析前先理解为什么会有缺失。

## Details by Analysis Module

### 分组排名分析

**触发条件：** 至少有一个类别字段（object 类型 + 唯一值 2-50 个）和一个数值字段。

**执行逻辑：**
1. 从所有类别字段中取前 3 个
2. 从所有数值字段中取前 2 个
3. 对每个组合执行 `groupby().agg(["sum", "mean", "count"])`
4. 按 sum 降序排列
5. 如果结果 >= 3 行，取 Top 1 和 Bottom 1 计算差距倍数
6. 生成 finding

**输出形式：** 每个组合一张排名表 + 一条 finding。

**限制：**
- 类别字段的唯一值数量限制在 2-50，不在这个范围内的字段不参与分组分析
- 限制前 3 个类别和前 2 个数值字段，超出部分不分析
- 差距倍数是简单的 `top_val / bottom_val`，不处理除零

### 趋势分析

**触发条件：** 至少有一个 datetime64 类型字段和一个数值字段。

**执行逻辑：**
1. 取第一个日期字段和第一个数值字段
2. 按月份分组求和（`dt.to_period("M")`）
3. 比较首尾月份的值
4. 如果首月值不为 0，计算变化百分比
5. 生成 finding（增长/下降）

**输出形式：** 月度趋势表 + 一条 finding。

**限制：**
- 只取第一个日期字段，如有多个日期字段只分析一个
- 只取第一个数值字段
- 首尾比较法不稳健——如果首月或末月本身是异常值，会误导结论
- 无法检测季节性模式（需要至少 2 年数据才能看出季节周期）

### 分布分析

**触发条件：** 至少有一个数值字段。

**执行逻辑：** 对每个数值字段执行 `df.describe()`。

**输出形式：** 描述统计表（count, mean, std, min, 25%, 50%, 75%, max）。

**限制：**
- 限制前 2 个数值字段
- 极端值会影响 mean 和 std
- 小样本下四分位数的参考价值有限

## Tier 2 & 3: Advanced Method Rules

For each advanced method, see `docs/methodology/advanced_method_triggers.md` for:

- Applicable business questions
- Trigger conditions
- Required fields
- Default execution policy
- User confirmation requirements
- Output specification
- Risk warnings
- When NOT applicable

### Summary Table

| Method | Tier | Default Execute? | User Confirm? | Key Requirement |
|--------|------|-----------------|---------------|-----------------|
| Correlation | 2 | No (recommend) | Not mandatory | 2+ numeric fields |
| t-test | 2 | No (conditional) | Recommended | Binary group + numeric |
| Chi-square | 2 | No (recommend) | Recommended | 2 categorical fields |
| Linear Regression | 2 | No (conditional) | MUST confirm target | Numeric target + predictors |
| Logistic Reg. | 2 | No (conditional) | MUST confirm target | Binary target + features |
| Clustering | 2 | No (recommend) | Recommended | 3+ numeric features |
| RFM | 2 | Auto if high-confidence | Not mandatory if high conf. | Customer ID + date + amount |
| Cohort | 2 | No (recommend) | Recommended | Customer ID + date |
| Seasonality | 2 | No (recommend) | Recommended | Date + numeric, 2+ cycles |
| Forecasting | 2 | NEVER auto | MANDATORY | Date + numeric, 30+ points |
| Sentiment | 2 | No (recommend) | Recommended | Text field |
| Causal Inference | 3 | NEVER auto | MANDATORY | Treatment + outcome + confounders |

## Python Pipeline Implementation Boundaries

The Python pipeline (`scripts/run_analysis.py`) implements Tier 1 methods only. The following methods have NO code implementation in the Python pipeline and rely on the Agent's (LLM's) analytical capability when conditions are met:

| Method | Pipeline Status | Agent Path |
|--------|----------------|------------|
| Correlation | Not in pipeline | Agent can compute `df.corr()` |
| t-test | Not in pipeline | Agent can use `scipy.stats.ttest_ind` |
| Chi-square | Not in pipeline | Agent can use `scipy.stats.chi2_contingency` |
| Linear Regression | Not in pipeline | Agent can use `statsmodels` or `sklearn` |
| Logistic Regression | Not in pipeline | Agent can use `sklearn.linear_model` |
| Clustering | Not in pipeline | Agent can use `sklearn.cluster` |
| RFM | Not in pipeline | Agent can compute from customer + date + amount |
| Cohort | Not in pipeline | Agent can compute from customer + date cohorts |
| Seasonality | Not in pipeline | Agent can use `statsmodels.tsa.seasonal_decompose` |
| Forecasting | Not in pipeline | Agent can use appropriate time series libraries |
| Sentiment | Not in pipeline | Agent can process text with available tools |
| Causal Inference | Not in pipeline | Agent MUST NOT attempt without explicit user request |
| Correlation Matrix | Not in pipeline | Agent can compute `df.corr()` |
| Seasonal Decomposition | Not in pipeline | Agent can use `statsmodels` |

Important: The Agent must follow SKILL.md Section 5 (Analysis Method Layering) and Section 14 (Advanced Analysis Principles) when executing any method not in the pipeline. All Tier 2/3 risk warnings and confirmation rules apply regardless of whether the analysis is done by the pipeline or the Agent.
