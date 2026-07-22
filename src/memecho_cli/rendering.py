"""Render memEcho result contracts as readable Markdown or standalone HTML."""

from collections import defaultdict
from html import escape


def items(value):
    return value if isinstance(value, list) else []


def text(value, fallback="未提供"):
    return fallback if value is None or value == "" else str(value)


def bounded(value, low=0.0, high=1.0, fallback=0.0):
    try:
        return max(low, min(high, float(value)))
    except (TypeError, ValueError):
        return fallback


def participant_names(result):
    return {
        item["id"]: item.get("name") or item["id"]
        for item in items(result.get("participants"))
        if isinstance(item, dict) and item.get("id")
    }


def person(participant_id, names):
    return names.get(participant_id, participant_id or "未标记参与者")


def ascii_axis(value, width=21):
    """Map -1..1 to an ASCII-only axis with a visible zero point."""
    try:
        value = max(-1.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        value = 0.0
    position = round((value + 1) / 2 * (width - 1))
    cells = ["."] * width
    cells[width // 2] = "|"
    cells[position] = "*"
    return "[" + "".join(cells) + f"] {value:+.2f}"


def ascii_confidence(value, width=10):
    try:
        value = max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        value = 0.0
    filled = round(value * width)
    return "[" + "#" * filled + "." * (width - filled) + f"] {value:.0%}"


def bullets(values, empty="无"):
    values = items(values)
    return "\n".join(f"- {text(value)}" for value in values) if values else f"- {empty}"


def evidence_label(item):
    label = item.get("segment_id") or item.get("id") or "未标记片段"
    start = item.get("start_ms")
    if isinstance(start, (int, float)):
        seconds = int(start // 1000)
        label += f" · {seconds // 60:02d}:{seconds % 60:02d}"
    return label


def render_markdown(result, title=None):
    """Return Markdown with compact ASCII visual summaries."""
    title = title or result.get("title") or "memEcho 对话分析报告"
    names = participant_names(result)
    scope = result.get("scope") if isinstance(result.get("scope"), dict) else {}
    minutes = result.get("minutes") if isinstance(result.get("minutes"), dict) else {}
    lines = [
        f"# {title}", "", "> VAD 表示对当前表达的推断，不是心理诊断或隐藏意图判断。", "",
        "## 分析范围、目标人物与可信度", "",
        f"- 分析模式：`{text(result.get('analysis_mode'))}`",
        f"- 已使用信号：{', '.join(map(str, items(scope.get('signals_used')))) or '未标记'}",
        f"- 缺失信号：{', '.join(map(str, items(scope.get('signals_missing')))) or '无'}", "",
        "```text", "REPORT CONFIDENCE", ascii_confidence(scope.get("quality", 0)), "```", "",
        "## 内容纪要", "", "### 摘要", "", text(minutes.get("summary")), "",
        "### 关注重点", "", bullets(minutes.get("focus")), "",
        "### 共识", "", bullets(minutes.get("consensus")), "",
        "### 未解决分歧", "", bullets(minutes.get("disagreements")), "",
        "### 明确动作", "",
    ]
    actions = items(minutes.get("explicit_actions"))
    lines.extend(
        f"- [x] {text(action.get('text'))}（负责人：{person(action.get('owner'), names)}；状态：confirmed；证据：{', '.join(action.get('evidence_refs', [])) or '未标记'}）"
        for action in actions
    )
    if not actions:
        lines.append("- 无明确承诺动作")
    lines.extend(["", "### 建议（未确认）", ""])
    recommendations = items(minutes.get("recommendations"))
    lines.extend(
        f"- [ ] {text(action.get('text'))}（状态：proposed；证据：{', '.join(action.get('evidence_refs', [])) or '未标记'}）"
        for action in recommendations
    )
    if not recommendations:
        lines.append("- 无")

    lines.extend(["", "## 内容解析：事实 / 观点 / 态度", ""])
    analyses = items(result.get("content_analysis"))
    if not analyses:
        lines.append("无可展示的参与者内容解析。")
    for analysis in analyses:
        lines.extend([
            f"### {person(analysis.get('participant_id'), names)}", "",
            "**事实主张（分类不等于核实）**", bullets(analysis.get("fact_claims")), "",
            "**观点**", bullets(analysis.get("opinions")), "",
            "**态度**", bullets(analysis.get("attitudes")), "",
            "**相互影响小结**", bullets(analysis.get("influence_summary")), "",
        ])

    lines.extend(["## VAD 走向", "", "图例：`*` 为当前值，`|` 为零点，横轴范围为 -1 到 +1。", ""])
    grouped = defaultdict(list)
    for point in items(result.get("vad_series")):
        grouped[point.get("participant_id")].append(point)
    if not grouped:
        lines.append("无可展示的 VAD 数据。")
    for participant_id, points in grouped.items():
        lines.extend([f"### {person(participant_id, names)}", "", "```text", "-1.0       0.0       +1.0"])
        for point in points:
            lines.extend([
                text(point.get("segment_id"), "segment"),
                f"  V {ascii_axis(point.get('v'))}", f"  A {ascii_axis(point.get('a'))}",
                f"  D {ascii_axis(point.get('d'))}", f"  C {ascii_confidence(point.get('confidence'))}",
            ])
        lines.extend(["```", ""])

    self_echo = result.get("self_echo") if isinstance(result.get("self_echo"), dict) else {}
    lines.extend(["## 自我回声", ""])
    if self_echo.get("participant_id"):
        lines.extend([
            f"视角：**{person(self_echo.get('participant_id'), names)}**（{text(self_echo.get('identity_basis'))}）", "",
            "### 观察到的后续反应", "", bullets(self_echo.get("effects")), "",
            "### 低压力替代表达", "", bullets(self_echo.get("alternatives")),
        ])
    else:
        lines.append("本次未解析“我”的身份，因此不输出自我回声。")

    lines.extend(["", "## 关键洞察与证据", ""])
    insights = items(result.get("insights"))
    if not insights:
        lines.append("无。")
    for insight in insights:
        lines.extend([
            f"### {text(insight.get('claim'))}", "",
            f"- 结论层级：`{text(insight.get('claim_level'))}`",
            f"- 置信度：`{ascii_confidence(insight.get('confidence'))}`",
            f"- 证据：{', '.join(insight.get('evidence_refs', [])) or '未标记'}",
            f"- 替代解释：{'；'.join(map(str, items(insight.get('alternatives')))) or '未提供'}", "",
        ])
    evidence = items(result.get("evidence"))
    if evidence:
        lines.extend(["### 证据索引", ""])
        lines.extend(
            f"- `{text(item.get('id'))}` {evidence_label(item)} · {person(item.get('speaker_id'), names)}：{text(item.get('excerpt'))}"
            for item in evidence
        )
    lines.extend([
        "", "## 不确定性", "", bullets(result.get("uncertainties")), "", "## 继续问 memEcho", "",
        "- 哪个结论最需要回到原文核对？", "- 请只展开我的 VAD 转折与对应证据。",
        "- 把一个高压力表达改写成三种低压力版本。", "- 从未解决分歧中选择一个场景开始陪练。", "",
    ])
    return "\n".join(lines)


def html_list(values, empty="无"):
    values = items(values)
    return "<ul>" + "".join(f"<li>{escape(text(value))}</li>" for value in values) + "</ul>" if values else f'<p class="empty">{escape(empty)}</p>'


def vad_meter(label, value):
    try:
        value = max(-1.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        value = 0.0
    return f'<div class="meter"><b>{label}</b><div class="track"><i style="left:{(value + 1) * 50:.1f}%"></i><span></span></div><em>{value:+.2f}</em></div>'


def render_html(result, title=None):
    """Return a self-contained offline HTML report without external assets."""
    title = title or result.get("title") or "memEcho 对话分析报告"
    names = participant_names(result)
    scope = result.get("scope") if isinstance(result.get("scope"), dict) else {}
    minutes = result.get("minutes") if isinstance(result.get("minutes"), dict) else {}
    quality = bounded(scope.get("quality"))
    action_html = "".join(f'<li><span class="status confirmed">已确认</span><strong>{escape(text(a.get("text")))}</strong><small>负责人：{escape(person(a.get("owner"), names))} · 证据：{escape(", ".join(a.get("evidence_refs", [])) or "未标记")}</small></li>' for a in items(minutes.get("explicit_actions"))) or '<li class="empty">无明确承诺动作</li>'
    suggestion_html = "".join(f'<li><span class="status proposed">建议</span><strong>{escape(text(a.get("text")))}</strong><small>尚未确认 · 证据：{escape(", ".join(a.get("evidence_refs", [])) or "未标记")}</small></li>' for a in items(minutes.get("recommendations"))) or '<li class="empty">无建议</li>'
    content_html = ""
    for item in items(result.get("content_analysis")):
        content_html += f'<article class="card person-card"><p class="eyebrow">参与者</p><h3>{escape(person(item.get("participant_id"), names))}</h3><div class="triple"><section><h4>事实主张</h4>{html_list(item.get("fact_claims"))}</section><section><h4>观点</h4>{html_list(item.get("opinions"))}</section><section><h4>态度</h4>{html_list(item.get("attitudes"))}</section></div><div class="influence"><h4>相互影响小结</h4>{html_list(item.get("influence_summary"))}</div></article>'
    content_html = content_html or '<article class="card empty">无可展示的参与者内容解析。</article>'
    grouped = defaultdict(list)
    for point in items(result.get("vad_series")):
        grouped[point.get("participant_id")].append(point)
    vad_html = ""
    for participant_id, points in grouped.items():
        segments = ""
        for point in points:
            confidence = bounded(point.get("confidence"))
            segments += f'<div class="segment"><header><strong>{escape(text(point.get("segment_id"), "segment"))}</strong><small>置信度 {confidence:.0%}</small></header>{vad_meter("V", point.get("v"))}{vad_meter("A", point.get("a"))}{vad_meter("D", point.get("d"))}<p class="signal">语言权重 {escape(text(point.get("linguistic_weight"), "0"))} · 声学权重 {escape(text(point.get("acoustic_weight"), "0"))}</p></div>'
        vad_html += f'<article class="card"><p class="eyebrow">VAD TRAJECTORY</p><h3>{escape(person(participant_id, names))}</h3>{segments}</article>'
    vad_html = vad_html or '<article class="card empty">无可展示的 VAD 数据。</article>'
    insight_html = ""
    for item in items(result.get("insights")):
        confidence = bounded(item.get("confidence"))
        insight_html += f'<article class="card insight"><div class="confidence-ring" style="--score:{confidence*360:.0f}deg"><span>{confidence:.0%}</span></div><div><p class="eyebrow">{escape(text(item.get("claim_level")))}</p><h3>{escape(text(item.get("claim")))}</h3><p>证据：{escape(", ".join(item.get("evidence_refs", [])) or "未标记")}</p><p class="muted">替代解释：{escape("；".join(map(str, items(item.get("alternatives")))) or "未提供")}</p></div></article>'
    insight_html = insight_html or '<article class="card empty">无关键洞察。</article>'
    evidence_html = "".join(f'<tr><td><code>{escape(text(e.get("id")))}</code></td><td>{escape(evidence_label(e))}</td><td>{escape(person(e.get("speaker_id"), names))}</td><td>{escape(text(e.get("excerpt")))}</td></tr>' for e in items(result.get("evidence"))) or '<tr><td colspan="4" class="empty">无证据索引</td></tr>'
    self_echo = result.get("self_echo") if isinstance(result.get("self_echo"), dict) else {}
    echo_html = f'<p>视角：<strong>{escape(person(self_echo.get("participant_id"), names))}</strong> · {escape(text(self_echo.get("identity_basis")))}</p><div class="split"><section><h4>观察到的后续反应</h4>{html_list(self_echo.get("effects"))}</section><section><h4>低压力替代表达</h4>{html_list(self_echo.get("alternatives"))}</section></div>' if self_echo.get("participant_id") else '<p class="empty">本次未解析“我”的身份，因此不输出自我回声。</p>'
    css = """:root{--paper:#f5f3ef;--ink:#25243a;--muted:#777382;--violet:#6d5ed8;--mint:#82cbbb;--peach:#eaa48d;--line:rgba(37,36,58,.12)}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.7 Inter,"PingFang SC","Microsoft YaHei",sans-serif}main{width:min(1160px,calc(100% - 32px));margin:auto;padding:48px 0 80px}.hero{padding:44px;border-radius:32px;background:linear-gradient(135deg,#25243a,#403b68);color:white;display:grid;grid-template-columns:1fr auto;gap:32px;align-items:end}.hero h1{font:500 clamp(38px,6vw,70px)/1.05 Georgia,"Songti SC",serif;margin:8px 0 18px}.eyebrow{margin:0;color:var(--violet);font-size:11px;font-weight:800;letter-spacing:.16em}.hero .eyebrow{color:#b9adff}.score{width:150px;height:150px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#a596ef calc(var(--quality)*1turn),rgba(255,255,255,.12) 0);position:relative}.score:before{content:"";position:absolute;width:116px;height:116px;border-radius:50%;background:#302d50}.score span{z-index:1;text-align:center}.score b{display:block;font-size:30px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.card{background:rgba(255,255,255,.78);border:1px solid var(--line);border-radius:24px;padding:26px;box-shadow:0 22px 60px rgba(49,42,91,.08)}h2{font:500 34px Georgia,"Songti SC",serif;margin:56px 0 18px}h3{font-size:22px;margin:5px 0 18px}h4{margin:12px 0 7px}ul{padding-left:20px}.summary{grid-column:1/-1}.triple{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.triple section,.split section{padding:12px 16px;border-radius:16px;background:#f2f0f7}.influence{border-top:1px solid var(--line);margin-top:18px;padding-top:10px}.action-list{list-style:none;padding:0}.action-list li{display:grid;grid-template-columns:auto 1fr;gap:8px 12px;padding:14px 0;border-top:1px solid var(--line)}.action-list small{grid-column:2;color:var(--muted)}.status{border-radius:99px;padding:3px 9px;font-size:10px}.confirmed{background:rgba(130,203,187,.22);color:#326f64}.proposed{background:rgba(234,164,141,.22);color:#945c49}.segment{border-top:1px solid var(--line);padding:16px 0}.segment header{display:flex;justify-content:space-between}.segment small,.signal,.muted,.empty{color:var(--muted)}.meter{display:grid;grid-template-columns:20px 1fr 55px;gap:10px;align-items:center;margin:9px 0}.meter em{text-align:right;font-style:normal}.track{height:8px;border-radius:99px;background:linear-gradient(90deg,#eaa48d,#ece9e2 50%,#82cbbb);position:relative}.track span{position:absolute;left:50%;top:-3px;width:1px;height:14px;background:white}.track i{position:absolute;top:50%;width:15px;height:15px;border:3px solid white;border-radius:50%;background:var(--violet);transform:translate(-50%,-50%)}.insight{display:grid;grid-template-columns:auto 1fr;gap:20px}.confidence-ring{width:82px;height:82px;border-radius:50%;background:conic-gradient(var(--violet) var(--score),#e7e3ef 0);display:grid;place-items:center;position:relative}.confidence-ring:before{content:"";position:absolute;width:62px;height:62px;background:white;border-radius:50%}.confidence-ring span{z-index:1;font-weight:800}.split{display:grid;grid-template-columns:1fr 1fr;gap:14px}table{width:100%;border-collapse:collapse;background:white;border-radius:20px;overflow:hidden}th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:11px;color:var(--muted)}code{color:var(--violet)}footer{margin-top:50px;padding:24px;border-top:1px solid var(--line);color:var(--muted)}@media(max-width:760px){.hero,.grid{grid-template-columns:1fr}.score{width:110px;height:110px}.score:before{width:82px;height:82px}.triple,.split{grid-template-columns:1fr}.summary{grid-column:auto}.hero{padding:28px}.card{padding:20px}table{display:block;overflow:auto}}"""
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><link rel="icon" href="data:,"> <title>{escape(title)}</title><style>{css}</style></head><body><main><header class="hero"><div><p class="eyebrow">MEMECHO · SINGLE SESSION REPORT</p><h1>{escape(title)}</h1><p>{escape(text(minutes.get("summary")))}</p><p>模式：{escape(text(result.get("analysis_mode")))} · 已使用：{escape(", ".join(map(str, items(scope.get("signals_used")))) or "未标记")} · 缺失：{escape(", ".join(map(str, items(scope.get("signals_missing")))) or "无")}</p></div><div class="score" style="--quality:{quality:.2f}"><span><b>{quality:.0%}</b>报告可信度</span></div></header><h2>内容纪要</h2><section class="grid"><article class="card summary"><p class="eyebrow">SUMMARY</p><h3>本次对话发生了什么</h3><p>{escape(text(minutes.get("summary")))}</p></article><article class="card"><h3>关注重点</h3>{html_list(minutes.get("focus"))}<h3>共识</h3>{html_list(minutes.get("consensus"))}</article><article class="card"><h3>未解决分歧</h3>{html_list(minutes.get("disagreements"))}</article><article class="card"><h3>明确动作</h3><ul class="action-list">{action_html}</ul></article><article class="card"><h3>建议</h3><ul class="action-list">{suggestion_html}</ul></article></section><h2>事实、观点与态度</h2><section class="grid">{content_html}</section><h2>VAD 走向</h2><section class="grid">{vad_html}</section><h2>自我回声</h2><section class="card">{echo_html}</section><h2>关键洞察</h2><section class="grid">{insight_html}</section><h2>证据索引</h2><table><thead><tr><th>ID</th><th>片段</th><th>说话人</th><th>原文</th></tr></thead><tbody>{evidence_html}</tbody></table><h2>不确定性</h2><section class="card">{html_list(result.get("uncertainties"))}</section><footer>VAD 是对表达层面的概率性推断，不代表真实内心、人格判断或心理诊断。报告未自动写入长期记忆。</footer></main></body></html>'''
