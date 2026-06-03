"""
HTML/CSS business report renderer.

This renderer turns the report schema into a designed HTML report and, when
WeasyPrint is available, exports that HTML to a print-ready PDF. The existing
ReportLab renderer remains the fallback path.
"""
from __future__ import annotations

import ctypes.util
from html import escape
import os
import platform
from typing import Iterable


def _text(value) -> str:
    return escape(str(value if value is not None else ""))


def _moneyish(value) -> str:
    if isinstance(value, (int, float)):
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:,.2f}"
    return _text(value)


def _list_items(items: Iterable[str], empty: str = "暂无") -> str:
    items = list(items or [])
    if not items:
        return f"<li>{_text(empty)}</li>"
    return "".join(f"<li>{_text(item)}</li>" for item in items)


def _system_chromium_path() -> str | None:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _weasyprint_system_ready() -> bool:
    """Avoid noisy WeasyPrint imports when required native libraries are absent."""
    if platform.system() == "Darwin":
        return ctypes.util.find_library("gobject-2.0") is not None
    return True


def _metric_cards(metrics: list[dict]) -> str:
    if not metrics:
        return '<p class="muted">当前数据没有匹配到可稳定计算的核心指标。</p>'
    cards = []
    for metric in metrics[:6]:
        cards.append(
            f"""
            <article class="metric-card">
              <div class="metric-label">{_text(metric.get('name', 'Metric'))}</div>
              <div class="metric-value">{_text(metric.get('current_value', ''))}</div>
              <p>{_text(metric.get('meaning', ''))}</p>
              <div class="formula">{_text(metric.get('formula', ''))}</div>
            </article>
            """
        )
    return "\n".join(cards)


def _field_semantics_table(semantics: list[dict]) -> str:
    rows = []
    for item in semantics[:24]:
        rows.append(
            "<tr>"
            f"<td>{_text(item.get('field', ''))}</td>"
            f"<td>{_text(item.get('inferred_meaning', ''))}</td>"
            f"<td><span class=\"pill\">{_text(item.get('confidence', ''))}</span></td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="3">暂无字段语义识别结果</td></tr>')
    return "".join(rows)


def _findings(findings: list[dict]) -> str:
    if not findings:
        return '<p class="muted">当前数据没有生成关键发现。</p>'
    blocks = []
    for idx, finding in enumerate(findings, 1):
        blocks.append(
            f"""
            <article class="finding-block">
              <div class="eyebrow">Finding {idx}</div>
              <h3>{_text(finding.get('title', '关键发现'))}</h3>
              <div class="lesson-grid">
                <div>
                  <h4>分析结果</h4>
                  <p>{_text(finding.get('data_evidence', ''))}</p>
                </div>
                <div>
                  <h4>业务解释</h4>
                  <p>{_text(finding.get('business_interpretation', ''))}</p>
                </div>
                <div>
                  <h4>不能说明什么</h4>
                  <p>{_text(finding.get('what_it_cannot_prove', '这个发现需要结合更多字段验证，不能单独推出因果关系。'))}</p>
                </div>
                <div>
                  <h4>下次怎么复用</h4>
                  <p>{_text(finding.get('how_to_reuse', '下次看到类似字段组合时，先找维度字段和数值指标，再做分组比较。'))}</p>
                </div>
              </div>
              <div class="action-strip">
                <strong>建议动作</strong>
                <span>{_text(finding.get('suggested_action', ''))}</span>
              </div>
            </article>
            """
        )
    return "\n".join(blocks)


def _thinking_models(models: list[dict]) -> str:
    if not models:
        return '<p class="muted">暂无思维模型说明。</p>'
    cards = []
    for model in models[:5]:
        cards.append(
            f"""
            <article class="model-card">
              <h3>{_text(model.get('model_name', 'Thinking Model'))}</h3>
              <p>{_text(model.get('evidence', ''))}</p>
              <strong>{_text(model.get('takeaway', ''))}</strong>
            </article>
            """
        )
    return "\n".join(cards)


def _tables(tables: list[dict]) -> str:
    blocks = []
    for table in tables[:5]:
        headers = table.get("headers", [])
        data = table.get("data", [])
        if not headers or not data:
            continue
        header_html = "".join(f"<th>{_text(h)}</th>" for h in headers[:6])
        rows = []
        for row in data[:10]:
            cells = "".join(f"<td>{_moneyish(v)}</td>" for v in list(row)[:6])
            rows.append(f"<tr>{cells}</tr>")
        blocks.append(
            f"""
            <article class="table-card">
              <h3>{_text(table.get('name', 'Data Table'))}</h3>
              <table>
                <thead><tr>{header_html}</tr></thead>
                <tbody>{''.join(rows)}</tbody>
              </table>
              <p class="caption">展示前 {min(len(data), 10)} 行，用于阅读主要结构；完整表格见 Excel 工作簿。</p>
            </article>
            """
        )
    if not blocks:
        return '<p class="muted">暂无可展示的数据表。</p>'
    return "\n".join(blocks)


def _recommendations(recommendations: list[dict]) -> str:
    if not recommendations:
        return '<p class="muted">暂无行动建议。</p>'
    return "".join(
        f"""
        <article class="recommendation">
          <h3>{_text(item.get('title', '建议'))}</h3>
          <p>{_text(item.get('action', ''))}</p>
          <dl>
            <dt>追踪指标</dt><dd>{_text(item.get('metric_to_track', ''))}</dd>
            <dt>还需要的数据</dt><dd>{_text(item.get('data_needed', ''))}</dd>
          </dl>
        </article>
        """
        for item in recommendations
    )


def render_html(report: dict, output_path: str) -> str:
    overview = report.get("dataset_overview", {})
    metrics = report.get("metric_glossary", [])
    semantics = report.get("field_semantics", [])
    findings = report.get("key_findings", [])
    models = report.get("thinking_models", [])
    recommendations = report.get("recommendations", [])
    tables = report.get("tables", [])
    beginner = report.get("beginner_notes", {})
    risks = report.get("data_quality", {}).get("risk_checks", [])

    title = report.get("title") or "Business Analysis Learning Report"
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{_text(title)}</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 16mm 18mm;
      @bottom-center {{
        content: "Business Analysis Learning Skill · " counter(page);
        color: #8a8175;
        font-size: 9px;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: #23201d;
      background: #f7f3eb;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
      line-height: 1.62;
      font-size: 12px;
    }}
    .page-shell {{ background: #fffaf1; min-height: 100%; }}
    .cover {{
      min-height: 238mm;
      padding: 30mm 18mm 18mm;
      background: linear-gradient(135deg, #fff8e8 0%, #f1ede3 55%, #dfe8e2 100%);
      border-bottom: 1px solid #d8d0bf;
      page-break-after: always;
    }}
    .cover .kicker {{ color: #7a6a4f; text-transform: uppercase; letter-spacing: .12em; font-size: 10px; }}
    h1 {{
      margin: 8mm 0 6mm;
      color: #1b365d;
      font-size: 34px;
      line-height: 1.08;
      letter-spacing: 0;
      max-width: 150mm;
    }}
    .cover-subtitle {{ max-width: 132mm; color: #4e4942; font-size: 14px; }}
    .cover-stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5mm;
      margin-top: 18mm;
      max-width: 150mm;
    }}
    .stat, .metric-card, .finding-block, .model-card, .recommendation, .table-card, .lesson-panel {{
      background: rgba(255,255,255,.78);
      border: 1px solid #ddd4c3;
      border-radius: 10px;
      padding: 5mm;
      break-inside: avoid;
      box-shadow: 0 10px 28px rgba(62, 49, 29, .06);
    }}
    .stat span {{ display: block; color: #7b766e; font-size: 10px; }}
    .stat strong {{ display: block; color: #1b365d; font-size: 20px; margin-top: 1mm; }}
    main {{ padding: 12mm 14mm 18mm; }}
    section {{
      margin: 0 0 10mm;
      break-inside: avoid;
    }}
    .section-title {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 8mm;
      margin: 0 0 5mm;
      border-bottom: 1px solid #d8d0bf;
      padding-bottom: 2.5mm;
    }}
    .section-title h2 {{
      margin: 0;
      color: #1b365d;
      font-size: 20px;
      line-height: 1.2;
    }}
    .section-title p {{ margin: 0; color: #7a6f61; max-width: 80mm; }}
    .eyebrow {{ color: #9b7a37; font-size: 10px; text-transform: uppercase; letter-spacing: .1em; }}
    .metric-grid, .model-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 5mm;
    }}
    .metric-label {{ color: #776f62; font-size: 10px; }}
    .metric-value {{ color: #1b365d; font-size: 23px; font-weight: 700; margin: 1mm 0; }}
    .formula {{ margin-top: 3mm; color: #665d52; font-size: 10px; background: #f3eee4; padding: 2mm; border-radius: 6px; }}
    .lesson-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 4mm;
    }}
    h3 {{ margin: 1mm 0 3mm; color: #25211d; font-size: 15px; }}
    h4 {{ margin: 0 0 1.5mm; color: #1b365d; font-size: 11px; }}
    p {{ margin: 0 0 2.5mm; }}
    .action-strip {{
      margin-top: 4mm;
      padding: 3mm 4mm;
      border-left: 3px solid #c9a96e;
      background: #f6f0e4;
      display: grid;
      grid-template-columns: 24mm 1fr;
      gap: 4mm;
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
    th {{ background: #1b365d; color: white; text-align: left; padding: 2.5mm; }}
    td {{ border-bottom: 1px solid #e4dccf; padding: 2.2mm; vertical-align: top; }}
    .caption, .muted {{ color: #7f776c; font-size: 10px; }}
    .pill {{ display: inline-block; padding: .8mm 2mm; border-radius: 999px; background: #e9dfca; color: #6b5629; }}
    .learning-list {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 5mm;
    }}
    ul {{ margin: 0; padding-left: 5mm; }}
    li {{ margin-bottom: 1.5mm; }}
    dl {{ display: grid; grid-template-columns: 24mm 1fr; gap: 1mm 3mm; margin: 0; }}
    dt {{ color: #7a6f61; }}
    dd {{ margin: 0; }}
    .page-break {{ page-break-before: always; }}
  </style>
</head>
<body>
  <div class="page-shell">
    <header class="cover">
      <div class="kicker">Learning-oriented business analysis report</div>
      <h1>{_text(title)}</h1>
      <p class="cover-subtitle">这份报告不只给出结论，还会解释每一步为什么这样分析、指标从哪里来、结论不能说明什么，以及下次遇到类似数据怎么复用。</p>
      <div class="cover-stats">
        <div class="stat"><span>Records</span><strong>{_text(f"{overview.get('rows', 0):,}")}</strong></div>
        <div class="stat"><span>Fields</span><strong>{_text(overview.get('columns', 0))}</strong></div>
        <div class="stat"><span>Findings</span><strong>{_text(len(findings))}</strong></div>
      </div>
    </header>
    <main>
      <section>
        <div class="section-title">
          <h2>1. 数据表先看什么</h2>
          <p>商业分析不能一上来就看结论。先看字段、规模和风险，才知道后面的分析是否可靠。</p>
        </div>
        <div class="lesson-grid">
          <article class="lesson-panel">
            <h3>数据体检</h3>
            <p>文件：{_text(overview.get('file_name', 'N/A'))}</p>
            <p>记录数：{_text(f"{overview.get('rows', 0):,}")}；字段数：{_text(overview.get('columns', 0))}</p>
            <p>缺失值：{_text('有' if overview.get('has_missing') else '无')}；重复行：{_text(overview.get('duplicate_rows', 0))}</p>
          </article>
          <article class="lesson-panel">
            <h3>初学者解释</h3>
            <p>数据体检像体检报告。缺失、重复、异常值会影响排名、趋势和建议，所以分析前必须先确认数据健康度。</p>
          </article>
        </div>
      </section>

      <section>
        <div class="section-title">
          <h2>2. 这张表适合分析什么</h2>
          <p>字段决定分析上限。时间字段适合看趋势，类别字段适合看分组差异，数值字段适合算指标。</p>
        </div>
        <table>
          <thead><tr><th>字段</th><th>推断含义</th><th>置信度</th></tr></thead>
          <tbody>{_field_semantics_table(semantics)}</tbody>
        </table>
      </section>

      <section>
        <div class="section-title">
          <h2>3. 核心指标课</h2>
          <p>指标不是数字标签，而是业务问题的量化方式。先理解公式和字段来源，再谈好坏。</p>
        </div>
        <div class="metric-grid">{_metric_cards(metrics)}</div>
      </section>

      <section>
        <div class="section-title">
          <h2>4. 关键发现与教学解释</h2>
          <p>每个发现都包含证据、解释、边界和复用方法，避免把数据差异误读成因果关系。</p>
        </div>
        {_findings(findings)}
      </section>

      <section>
        <div class="section-title">
          <h2>5. 分析表怎么看</h2>
          <p>这里展示主要表格片段。完整数据请看 Excel；PDF 重点负责解释，而不是塞满所有数据。</p>
        </div>
        {_tables(tables)}
      </section>

      <section>
        <div class="section-title">
          <h2>6. 思维模型</h2>
          <p>好的商业分析不是只会算，而是知道如何拆解、比较、验证和防止过度解读。</p>
        </div>
        <div class="model-grid">{_thinking_models(models)}</div>
      </section>

      <section>
        <div class="section-title">
          <h2>7. 行动建议</h2>
          <p>建议必须能追溯到数据发现。执行前还要确认成本、资源、样本量和业务背景。</p>
        </div>
        {_recommendations(recommendations)}
      </section>

      <section class="page-break">
        <div class="section-title">
          <h2>8. 本次分析学到了什么</h2>
          <p>这部分是给初学者的复盘：下次拿到类似数据，应该知道先看什么、怎么分析、哪里不能过度解读。</p>
        </div>
        <div class="learning-list">
          <article class="lesson-panel">
            <h3>本次学到的方法</h3>
            <ul>{_list_items(beginner.get('methods_learned', []))}</ul>
          </article>
          <article class="lesson-panel">
            <h3>学到的指标</h3>
            <ul>{_list_items(beginner.get('metrics_learned', []))}</ul>
          </article>
          <article class="lesson-panel">
            <h3>下次怎么做</h3>
            <ul>{_list_items(beginner.get('next_time_steps', []))}</ul>
          </article>
          <article class="lesson-panel">
            <h3>不要过度解读</h3>
            <ul>{_list_items(beginner.get('conclusions_not_to_overinterpret', []))}</ul>
          </article>
        </div>
      </section>
    </main>
  </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def render_pdf(report: dict, output_path: str, html_path: str | None = None) -> tuple[str, str, str]:
    """Render HTML first, then export PDF with WeasyPrint."""
    if html_path is None:
        base, _ = os.path.splitext(output_path)
        html_path = f"{base}.html"

    render_html(report, html_path)

    weasy_error = "native libraries not detected"
    if _weasyprint_system_ready():
        try:
            from weasyprint import HTML

            HTML(filename=html_path).write_pdf(output_path)
            return output_path, html_path, "weasyprint"
        except Exception as exc:
            weasy_error = exc

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            executable_path = _system_chromium_path()
            launch_kwargs = {"executable_path": executable_path} if executable_path else {}
            browser = playwright.chromium.launch(**launch_kwargs)
            page = browser.new_page(viewport={"width": 1240, "height": 1754})
            page.goto(f"file://{os.path.abspath(html_path)}", wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
        return output_path, html_path, "playwright"
    except Exception as exc:
        raise RuntimeError(
            f"HTML-to-PDF export failed. WeasyPrint: {weasy_error}. Playwright: {exc}"
        ) from exc
