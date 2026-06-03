# Business Analysis Learning Agent Skill

> 把一份真实数据集，变成一次可以完成、可以理解、也可以反复回看的商业分析练习。

很多商科生和数据分析初学者并不是没有数据，也不是没有 AI。

真正困难的是：当 AI 很快给出图表和结论之后，你依然不知道它为什么这样分析，不知道指标是怎么算出来的，也不知道下一次换一份数据后，自己还能不能再做一遍。

这个 Skill 想解决的，就是这段从“看见答案”到“真正学会”的距离。

## 核心理念：以练代学

它不是一份只让你阅读的教程，而是一套让你在真实任务中学习商业分析的工作流。

你提供一份 CSV、Excel 或多表业务数据，Agent 会陪你完成一次完整分析，同时解释每一步背后的思考：

```text
拿到真实数据
    ↓
理解字段和业务问题
    ↓
选择分析方法并计算指标
    ↓
解释数据发现、商业含义和风险边界
    ↓
生成可以回顾的训练产物
    ↓
把这套思路用到下一份数据
```

每一次使用，既是在完成一个分析任务，也是在完成一次商业分析训练。

## 为什么要开发这个 Skill

商业初学者常常会卡在这些地方：

- 会打开 Excel，却不知道面对一张表应该先看什么
- 听过 GMV、AOV、留存率、转化率，却不知道它们与哪些字段有关
- 能让 AI 生成结果，却无法判断结论是否可靠
- 看懂了这次报告，但换一份数据后仍然不知道如何开始
- 做完分析后没有留下适合复盘、展示或放进作品集的完整产物

因此，这个 Skill 不只输出“发现了什么”，还会继续解释：

- 为什么选择这个分析方法
- 指标由哪些字段计算得出
- 结果在商业场景中意味着什么
- 这个结果不能证明什么
- 下次遇到类似数据时，应该如何复用这套思路

> 分析输出会从“发现问题 → 给出建议”，升级为“分析发现 → 方法解释 → 指标解释 → 商业含义 → 风险边界 → 学习迁移”。完整教学规则见 `docs/methodology/teaching_output_rules.md`。

## 每次练习都会留下什么

学习不应该只停留在一次对话里。每次分析结束后，Skill 会生成一组可以保存、复盘和展示的训练产物：

| 训练产物 | 你可以用它做什么 |
| --- | --- |
| `*_analysis.xlsx` | 回看数据表、图表、KPI 仪表板和分析过程 |
| `*_report.html` | 在浏览器中阅读结构化的教学报告 |
| `*_report.pdf` | 像复习讲义一样回顾指标、发现、商业概念和思维模型 |
| `*_audit_log.json` | 检查执行了什么、跳过了什么，以及为什么 |
| HTML 演示文稿 | 用于汇报、分享或作品集展示 |

这些文件不是分析结束后的“附件”，而是学习过程的一部分。你可以在下一次练习前重新打开 PDF，回顾自己学过的指标、方法和判断边界。

## 它适合谁

- 正在学习商业分析、市场营销、运营、管理或财务分析的商科生
- 刚开始接触数据分析，不擅长 Python、SQL 或统计学的初学者
- 希望 AI 不只给答案，还能解释分析逻辑的用户
- 想通过真实项目积累商业分析作品集的人
- 希望用“做中学”方式训练分析思维的人

## 这个 Skill 能做什么

本 Skill 将 **Python 与 pandas 自动分析管线** 和 **Agent 主导的分析推理** 结合起来：

- 读取 CSV 和 Excel 数据
- 检查数据规模、字段、缺失值和重复值
- 根据字段命名模式推断字段的商业含义
- 从预设指标库中匹配当前数据可以计算的商业指标
- 执行分组排名、趋势、分布等基础描述性分析
- 检查常见的数据质量风险
- 生成 Excel、HTML、PDF 和 JSON 审计日志
- 通过 Agent 工作流生成 HTML 演示文稿
- 使用中文解释分析逻辑、指标定义和商业洞察

### 这个 Skill 不是什么

- 不是机器学习平台，Python 管线中不包含机器学习模型
- 不是自动建模工具，主管线不使用 `scikit-learn`、`statsmodels` 或 `Prophet`
- 不能替代 SPSS、Stata 或 SAS
- 不是“自动数据科学家”，所有分析逻辑均由规则驱动，并且可以审计

> 当数据条件满足且用户确认后，Agent 可以使用可用工具执行相关性分析、RFM 等进阶方法。这些方法由 Agent 主导，不属于 Python 主管线的自动执行范围。三级方法体系见 `SKILL.md`。

## 工作流程

```text
CSV/Excel → 数据读取 → 字段语义识别 → 指标匹配 → 分析规划 → HTML/PDF/Excel/审计日志
```

整个分析过程遵循稳定、可检查的规则驱动管线：

1. **数据读取**：使用 `load_dataset()` 或 `load_folder()`，通过 pandas 读取 CSV 或 Excel
2. **数据体检**：检查记录数、字段数、缺失值和重复值
3. **字段语义识别**：使用命名模式将字段名映射为可能的商业含义
4. **指标匹配**：根据指标库匹配可计算指标，并在字段满足时计算 CTR、CPC、利润率等指标
5. **质量检查**：检查负数、零值比例和缺失比例等风险
6. **排名分析**：使用分组聚合识别表现最好和最差的业务分组
7. **趋势分析**：按月汇总数据并计算环比变化
8. **分布分析**：计算均值、中位数、标准差和四分位数
9. **思维模型**：根据分析结果生成可复用的商业分析思维模型
10. **统一结果结构**：将分析结果写入所有输出渲染器共同使用的数据结构
11. **输出渲染**：生成 Excel、设计型 HTML 报告和 PDF 报告
12. **审计日志**：记录执行了什么、匹配了什么、跳过了什么，以及跳过原因

每一步都对应 `scripts/core/` 或 `scripts/renderers/` 中的具体模块。详细方法说明见 `docs/methodology/`。

### PDF 生成方式

PDF 会先以 HTML/CSS 商业报告的形式生成，再使用 WeasyPrint 或 Playwright 的浏览器 PDF 引擎导出。

当 HTML 转 PDF 不可用时，系统会使用旧版 ReportLab 渲染器作为最终备用方案。这个设计可以提升报告可读性，减少每个章节强制单独分页造成的大量空白，并允许用户通过生成的 `*_report.html` 文件检查和调整排版。

## 示例输出

`sample_outputs/final_demo/` 目录中提供了无需运行工具即可浏览的完整示例：

| 示例 | 包含内容 | 说明 |
| --- | --- | --- |
| `final_demo/retail_demo/` | Excel、PDF、审计日志 | 零售销售分析示例 |
| `final_demo/multi_table_demo/` | Excel、PDF、审计日志、HTML 演示文稿 | 多表关联分析示例 |

示例文件通常包括：

- `*_analysis.xlsx`：数据表、图表和 KPI 仪表板
- `*_report.html`：用于浏览器阅读和 PDF 排版检查的教学型报告
- `*_report.pdf`：从 HTML 报告导出的 PDF
- `*_audit_log.json`：已执行、已跳过和建议执行方法的完整审计记录

更多说明见 `sample_outputs/README.md`。

## 项目结构

```text
├── README.md
├── QUICKSTART.md
├── SKILL.md                         跨平台 Agent 行为说明
├── AGENT_INSTRUCTIONS.md            非 Claude Agent 的独立指令文件
├── requirements.txt
├── scripts/
│   ├── run_analysis.py              通用命令行入口
│   ├── core/                        数据读取、字段语义、指标和分析规划
│   ├── renderers/                   Excel、HTML 和 PDF 输出渲染器
│   ├── legacy/                      历史验证脚本，不属于当前主管线
│   └── README.md
├── templates/                       教学与报告模板
├── examples/                        Agent 和用户参考示例
├── test_cases/                      测试数据集
├── docs/
│   ├── methodology/                 方法论详细文档
│   └── archive/                     历史文档和历史输出
├── sample_outputs/                  GitHub 展示示例，不属于运行时输出
├── vendor/agent_presentation_skills/  内置演示文稿设计依赖
├── .claude/                         可选的 Claude Code 适配器
└── LICENSE
```

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- 安装依赖：

```bash
pip install -r requirements.txt
```

### 分析单个 CSV 文件

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/your/data.csv" \
  --mode beginner_summary \
  --output-dir ~/Desktop/my_analysis
```

### 分析包含多个 CSV 的文件夹

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/data/folder/" \
  --mode audit_report \
  --output-dir ~/Desktop/multi_table_analysis
```

### 运行基础验证

```bash
python3 scripts/run_analysis.py \
  --input test_cases/sample_retail_sales.csv \
  --mode beginner_summary \
  --output-dir /tmp/balearn_smoke_test
```

每次运行会生成以下文件：

| 文件 | 说明 |
| --- | --- |
| `*_analysis.xlsx` | 包含数据表、图表和仪表板的 Excel 工作簿 |
| `*_report.html` | 用于浏览器阅读和 PDF 排版检查的 HTML 教学报告 |
| `*_report.pdf` | 从 HTML/CSS 报告导出的 PDF |
| `*_audit_log.json` | 记录已执行、已跳过和建议方法的 JSON 审计日志 |

### 可用输出模式

| 模式 | 适用场景 |
| --- | --- |
| `beginner_summary` | 初次使用，输出简短且易于理解 |
| `standard_report` | 平衡解释深度和阅读效率 |
| `audit_report` | 用于作品集、验收或完整审查 |

### 输出语言

所有面向用户的输出默认使用中文。用户也可以通过 Agent 工作流要求英文或中英双语输出。

## Agent 兼容性

本项目被设计为跨平台 Agent Skill，可用于：

- Claude Code，通过 `.claude/` 适配器使用
- Claude 桌面版或网页版
- ChatGPT 数据分析工具
- Gemini 或其他支持读取指令文件的 Agent

Claude Code 用户在打开本仓库后，可以运行 `/balearn`。

其他 Agent 可以使用 `AGENT_INSTRUCTIONS.md` 作为起始指令。

## 演示文稿生成

推荐通过交互式 Agent 工作流生成演示文稿，具体规则见 `SKILL.md` 的演示文稿步骤：

1. 首先完成分析，并生成 Excel、HTML、PDF 和审计日志
2. Agent 询问用户是否需要演示文稿
3. 如果需要，用户从两种风格中选择：
   - **Guizang A，电子杂志风**：适合叙事表达，支持翻页式 HTML 和 WebGL 背景
   - **Guizang B，瑞士国际主义风**：强调网格、层级和结构化信息
4. Agent 生成独立的 HTML 演示文稿

演示文稿模板位于 `vendor/agent_presentation_skills/`。

演示文稿属于 **仅由 Agent 生成的产物**。通用命令行工具不会直接生成 PPTX，也不提供 `--ppt` 快捷参数。这样可以确保每一份演示文稿都由 Agent 在阅读所选演示文稿 Skill 后生成，并遵循其设计规范和验收清单。

## 适用场景

- 营销活动分析
- 零售销售分析
- 客户流失分析
- 产品表现分析
- 财务指标分析
- 多表商业数据整合

## 设计原则

- 分析过程也是学习过程，先解释为什么，再说明怎么做
- 将数据字段连接到真实商业问题
- 区分数据证据、商业解释和假设
- 始终考虑初学者的理解成本
- 输出具有专业质量的 Excel、HTML 和 PDF

## 项目亮点

- **跨平台 Agent Skill**：适用于 Claude Code、ChatGPT、Gemini 或其他能够读取指令文件的 Agent
- **面向初学者的商业语言**：使用易于理解的中文解释指标、方法和发现
- **完整可审计管线**：每一步都记录在 JSON 审计日志中
- **多表关联能力**：识别关联字段、判断表关系，并谨慎合并相关数据集
- **专业输出产物**：生成带 KPI 仪表板的 Excel、设计型 HTML 报告、PDF 和 JSON 审计日志
- **三级学习路径**：从基础描述性分析逐步延伸到进阶方法，并根据数据条件决定是否执行

## 当前限制

- **不是机器学习平台**：Python 管线由规则驱动，不包含机器学习模型
- **不是因果推断工具**：可以识别模式和关联，但不能直接证明因果关系
- **统计分析深度有限**：回归、时间序列预测和聚类等进阶方法需要 Agent 参与并获得用户确认
- **当前仅支持 CSV 和 Excel**：不能直接连接数据库、API 或云存储
- **以内存方式处理数据**：超大数据集可能耗尽可用内存
- **字段语义依赖命名模式**：非标准字段名可能无法被准确识别

## 许可证

主项目使用 MIT 许可证，详见 `LICENSE`。

内置的第三方演示文稿 Agent Skill 保留其原始许可证，其中 `guizang-ppt-skill` 使用 GNU AGPL-3.0 许可证。详细说明见 `THIRD_PARTY_NOTICES.md`。
