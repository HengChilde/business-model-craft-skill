#!/usr/bin/env python3
"""
business-model-craft-skill 本地案例详情页生成器
基于 businessmodelcraft.com 案例详情页的结构、样式变量与九宫格布局，
将四件套中的 JSON + 中英文 Markdown 生成一个可双击打开的本地 HTML 文件。

约束：
- 只生成案例详情页，不生成本地列表页 / 博客页
- 页面中的其他可点击入口统一跳转到 businessmodelcraft.com 真站
- 页面内置中英文切换按钮，无需本地服务
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

BASE_URL = "https://businessmodelcraft.com"
TOKEN_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*')
OUTPUT_DIR_ENV_KEYS = ("BUSINESSMODELCRAFT_OUTPUT_BASE", "BUSINESSMODELCRAFT_OUTPUT_DIR")
OUTPUT_FOLDER_NAME = "BusinessModelCraft"

SITE_TEXT = {
    "en": {
        "home": "Home",
        "examples": "Examples",
        "blog": "Blog",
        "guide": "Guide",
        "editor_take": "Editor's Take",
        "craft_cta": "Build your own business model",
        "footer_note": "This local page is generated for easier reading. All navigation links open the live site.",
        "open_live": "Open live page",
        "visit_site": "Visit BusinessModelCraft",
    },
    "zh": {
        "home": "首页",
        "examples": "案例",
        "blog": "博客",
        "guide": "入门指南",
        "editor_take": "深度解析",
        "craft_cta": "构建你自己的商业模式",
        "footer_note": "这个本地页面仅用于便于阅读，所有导航入口都会跳转到网站真实页面。",
        "open_live": "打开官网页面",
        "visit_site": "访问 BusinessModelCraft",
    },
}

CANVAS_LABELS = {
    "en": {
        "keyPartners": "Key Partners",
        "keyActivities": "Key Activities",
        "keyResources": "Key Resources",
        "valuePropositions": "Value Propositions",
        "customerRelationships": "Customer Relationships",
        "channels": "Channels",
        "customerSegments": "Customer Segments",
        "costStructure": "Cost Structure",
        "revenueStreams": "Revenue Streams",
    },
    "zh": {
        "keyPartners": "重要合作伙伴",
        "keyActivities": "关键业务",
        "keyResources": "核心资源",
        "valuePropositions": "价值主张",
        "customerRelationships": "客户关系",
        "channels": "渠道通路",
        "customerSegments": "客户细分",
        "costStructure": "成本结构",
        "revenueStreams": "收入来源",
    },
}

# 近似复用 app/globals.css 的设计令牌
GLOBAL_STYLE_VARS = """
:root {
  --bg-primary: #F2F2F0;
  --bg-secondary: #FFFFFF;
  --bg-accent: #E5E5E5;
  --text-primary: #1A1A1A;
  --text-secondary: #4A4A4A;
  --accent-primary: #1A1A1A;
  --accent-secondary: #E8F5E9;
  --font-serif: 'Playfair Display', 'Times New Roman', Times, serif;
  --font-sans: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-serif-sc: 'Noto Serif SC', 'Songti SC', 'SimSun', serif;
}
html[lang='zh'] .font-serif,
.font-serif:lang(zh),
.font-serif:lang(zh-CN) {
  font-family: var(--font-serif-sc) !important;
}
"""

SVG_ICONS = {
    "layers": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2" ry="2" fill="none" stroke="currentColor" stroke-width="2"></rect><path d="M9 5v14" stroke="currentColor" stroke-width="2"></path><path d="M15 5v14" stroke="currentColor" stroke-width="2"></path></svg>',
    "users": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" fill="none" stroke="currentColor" stroke-width="2"></path><circle cx="9.5" cy="7" r="3" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="M20 21v-2a4 4 0 0 0-3-3.87" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M16 4.13a3 3 0 0 1 0 5.74" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "activity": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 12h-4l-3 9-6-18-3 9H2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
    "package": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" fill="none" stroke="currentColor" stroke-width="2"></path><path d="m3.3 7 8.7 5 8.7-5" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M12 22V12" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "gift": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="8" width="18" height="4" rx="1" fill="none" stroke="currentColor" stroke-width="2"></rect><path d="M12 8v13" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M7.5 8a2.5 2.5 0 1 1 0-5C10 3 12 8 12 8" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M16.5 8a2.5 2.5 0 1 0 0-5C14 3 12 8 12 8" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "heart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 21-1.45-1.32C5.4 15.36 2 12.28 2 8.5A4.5 4.5 0 0 1 6.5 4 5 5 0 0 1 12 7a5 5 0 0 1 5.5-3A4.5 4.5 0 0 1 22 8.5c0 3.78-3.4 6.86-8.55 11.18Z" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "truck": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17h4V5H2v12h3" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M14 9h4l4 4v4h-2" fill="none" stroke="currentColor" stroke-width="2"></path><circle cx="7" cy="17" r="2" fill="none" stroke="currentColor" stroke-width="2"></circle><circle cx="17" cy="17" r="2" fill="none" stroke="currentColor" stroke-width="2"></circle></svg>',
    "wallet": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M2 7h20v10H2z" fill="none" stroke="currentColor" stroke-width="2"></path><circle cx="16" cy="12" r="1" fill="currentColor"></circle></svg>',
    "trending": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m22 7-8.5 8.5-5-5L2 17" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M16 7h6v6" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "file": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M14 2v6h6" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "book": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "compass": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36z" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "globe": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="M2 12h20" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"></rect><path d="m3 7 9 6 9-6" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "home": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 10 9-7 9 7" fill="none" stroke="currentColor" stroke-width="2"></path><path d="M5 10v10h14V10" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
    "arrow_right": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14" fill="none" stroke="currentColor" stroke-width="2"></path><path d="m12 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2"></path></svg>',
}

CANVAS_ICON_BY_KEY = {
    "keyPartners": "users",
    "keyActivities": "activity",
    "keyResources": "package",
    "valuePropositions": "gift",
    "customerRelationships": "heart",
    "channels": "truck",
    "customerSegments": "users",
    "costStructure": "wallet",
    "revenueStreams": "trending",
}

CANVAS_POSITIONS = {
    "keyPartners": (1, 1, 2),
    "keyActivities": (2, 1, 1),
    "keyResources": (2, 2, 1),
    "valuePropositions": (3, 1, 2),
    "customerRelationships": (4, 1, 1),
    "channels": (4, 2, 1),
    "customerSegments": (5, 1, 2),
}


def normalize_href(href: str) -> str:
    href = href.strip()
    if not href:
        return href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return f"{BASE_URL}{href}"
    return href



def render_inline(text: str) -> str:
    result: list[str] = []
    last = 0
    for match in TOKEN_RE.finditer(text):
        result.append(html.escape(text[last:match.start()]))
        label, href, code, strong, em = match.groups()
        if label is not None and href is not None:
            safe_href = html.escape(normalize_href(href), quote=True)
            safe_label = html.escape(label)
            result.append(f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer">{safe_label}</a>')
        elif code is not None:
            result.append(f"<code>{html.escape(code)}</code>")
        elif strong is not None:
            result.append(f"<strong>{html.escape(strong)}</strong>")
        elif em is not None:
            result.append(f"<em>{html.escape(em)}</em>")
        last = match.end()
    result.append(html.escape(text[last:]))
    return "".join(result)



def markdown_table_to_html(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\|[\s\-:|]+\|$", stripped):
            continue
        rows.append([render_inline(cell.strip()) for cell in stripped.strip("|").split("|")])
    if not rows:
        return ""
    output = ["<table>"]
    for index, row in enumerate(rows):
        tag = "th" if index == 0 else "td"
        output.append("<tr>")
        for cell in row:
            output.append(f"<{tag}>{cell}</{tag}>")
        output.append("</tr>")
    output.append("</table>")
    return "\n".join(output)



def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    output: list[str] = []
    i = 0
    in_list = False
    in_blockquote = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    def close_blockquote() -> None:
        nonlocal in_blockquote
        if in_blockquote:
            output.append("</blockquote>")
            in_blockquote = False

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            close_list()
            close_blockquote()
            i += 1
            continue

        if stripped.startswith(">"):
            close_list()
            if not in_blockquote:
                output.append("<blockquote>")
                in_blockquote = True
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]).rstrip())
                i += 1
            j = 0
            while j < len(quote_lines):
                line = quote_lines[j]
                if not line.strip():
                    j += 1
                    continue
                if line.startswith("|"):
                    table_lines: list[str] = []
                    while j < len(quote_lines) and quote_lines[j].startswith("|"):
                        table_lines.append(quote_lines[j])
                        j += 1
                    output.append(markdown_table_to_html(table_lines))
                    continue
                if line.startswith("- ") or line.startswith("* "):
                    items: list[str] = []
                    while j < len(quote_lines) and (quote_lines[j].startswith("- ") or quote_lines[j].startswith("* ")):
                        items.append(f"<li>{render_inline(quote_lines[j][2:].strip())}</li>")
                        j += 1
                    output.append("<ul>" + "".join(items) + "</ul>")
                    continue
                output.append(f"<p>{render_inline(line)}</p>")
                j += 1
            close_blockquote()
            continue

        close_blockquote()

        if stripped.startswith("## "):
            close_list()
            output.append(f"<h2>{render_inline(stripped[3:].strip())}</h2>")
            i += 1
            continue
        if stripped.startswith("### "):
            close_list()
            output.append(f"<h3>{render_inline(stripped[4:].strip())}</h3>")
            i += 1
            continue
        if stripped.startswith("|"):
            close_list()
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            output.append(markdown_table_to_html(table_lines))
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{render_inline(stripped[2:].strip())}</li>")
            i += 1
            continue

        close_list()
        output.append(f"<p>{render_inline(stripped)}</p>")
        i += 1

    close_list()
    close_blockquote()
    return "\n".join(output)



def split_canvas_lines(content: str) -> list[str]:
    lines = []
    for raw in (content or "").splitlines():
        text = raw.strip()
        if not text:
            continue
        if text.startswith("•"):
            text = text[1:].strip()
        lines.append(text)
    return lines or ["—"]



def render_canvas_card(title: str, content: str, icon_name: str) -> str:
    items = "".join(f"<li>{render_inline(item)}</li>" for item in split_canvas_lines(content))
    return f'''<section class="canvas-card">
  <div class="canvas-card-header">
    <div class="canvas-icon-wrap">
      <span class="canvas-icon-bg"></span>
      <span class="canvas-icon">{SVG_ICONS[icon_name]}</span>
    </div>
    <h2>{html.escape(title)}</h2>
  </div>
  <div class="canvas-card-content">
    <ul>{items}</ul>
  </div>
</section>'''



def render_canvas_grid(canvas: dict, lang: str) -> str:
    labels = CANVAS_LABELS[lang]
    top_slots = []
    for key in [
        "keyPartners",
        "keyActivities",
        "keyResources",
        "valuePropositions",
        "customerRelationships",
        "channels",
        "customerSegments",
    ]:
        col, row, row_span = CANVAS_POSITIONS[key]
        style = f"grid-column: {col}; grid-row: {row} / span {row_span};"
        top_slots.append(
            f'<div class="canvas-slot" style="{style}">{render_canvas_card(labels[key], canvas.get(key, ""), CANVAS_ICON_BY_KEY[key])}</div>'
        )
    bottom_slots = []
    for key in ["costStructure", "revenueStreams"]:
        bottom_slots.append(
            f'<div class="canvas-slot">{render_canvas_card(labels[key], canvas.get(key, ""), CANVAS_ICON_BY_KEY[key])}</div>'
        )
    return (
        '<div class="canvas-grid-top">' + ''.join(top_slots) + '</div>'
        + '<div class="canvas-grid-bottom">' + ''.join(bottom_slots) + '</div>'
    )


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_en}</title>
  <style>
    {global_style_vars}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-family: var(--font-sans);
      line-height: 1.6;
    }}
    a {{ color: inherit; text-decoration: none; }}
    svg {{ width: 100%; height: 100%; display: block; }}
    .font-serif {{ font-family: var(--font-serif); }}
    .page {{ min-height: 100vh; background: var(--bg-primary); }}
    .shell {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; }}
    .article-shell {{ max-width: 768px; margin: 0 auto; padding: 0 24px; }}
    .lang-en [data-locale="zh"], .lang-zh [data-locale="en"] {{ display: none !important; }}

    .site-header {{ width: 100%; padding: 32px 0; background: transparent; position: relative; z-index: 50; }}
    .site-header-inner {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; display: flex; justify-content: space-between; align-items: center; gap: 24px; }}
    .brand {{ display: flex; align-items: center; gap: 8px; }}
    .brand-mark {{ width: 40px; height: 40px; padding: 6px; background: #000; color: #fff; border-radius: 12px; flex: none; }}
    .brand-title {{ font-family: var(--font-sans); font-weight: 700; font-size: 20px; line-height: 1; letter-spacing: -0.02em; color: var(--text-primary); }}
    .nav-center {{ display: none; }}
    .nav-right {{ display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; color: var(--text-secondary); }}
    .nav-right svg {{ width: 16px; height: 16px; }}
    .lang-link {{ background: none; border: 0; padding: 0; color: inherit; cursor: pointer; font: inherit; }}
    .lang-link.active {{ color: #000; font-weight: 700; }}

    @media (min-width: 768px) {{
      .nav-center {{ display: flex; align-items: center; gap: 8px; position: absolute; left: 50%; transform: translateX(-50%); }}
      .nav-pill {{ display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 999px; font-size: 14px; font-weight: 500; color: var(--text-secondary); transition: all .2s ease; }}
      .nav-pill:hover {{ color: #000; background: rgba(0, 0, 0, 0.05); }}
      .nav-pill-icon {{ width: 16px; height: 16px; }}
    }}

    .breadcrumb {{ width: 100%; max-width: 1280px; padding: 16px 24px 32px; margin: 0 auto; }}
    .breadcrumb ol {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; list-style: none; margin: 0; padding: 0; font-size: 14px; color: #6b7280; }}
    .breadcrumb a:hover {{ color: #000; }}
    .breadcrumb .separator {{ color: #9ca3af; }}
    .breadcrumb .current {{ color: #111827; font-weight: 500; }}

    .hero {{ padding: 32px 24px 48px; max-width: 1024px; margin: 0 auto; }}
    .industry-tag {{ display: inline-block; padding: 4px 12px; margin-bottom: 24px; border-radius: 999px; background: #eef2ff; color: #4f46e5; font-size: 14px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
    .hero h1 {{ margin: 0 0 24px; font-size: clamp(36px, 5vw, 48px); line-height: 1.1; font-weight: 800; color: #111827; text-align: center; }}
    .hero p {{ margin: 0; font-size: clamp(18px, 2vw, 20px); line-height: 1.7; color: #6b7280; text-align: left; }}

    .canvas-section {{ width: 100%; max-width: 1280px; margin: 0 auto; padding: 0 24px 80px; }}
    .canvas-grid-top {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(200px, auto)); gap: 12px; }}
    .canvas-grid-bottom {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 12px; }}
    .canvas-card {{ height: 100%; min-height: 100%; background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04); display: flex; flex-direction: column; overflow: hidden; }}
    .canvas-card-header {{ display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-bottom: 1px solid #f3f4f6; }}
    .canvas-card-header h2 {{ margin: 0; font-family: var(--font-sans); font-weight: 700; font-size: 14px; line-height: 1.2; color: #1A1A1A; }}
    .canvas-icon-wrap {{ position: relative; width: 24px; height: 24px; flex: none; }}
    .canvas-icon-bg {{ position: absolute; inset: 0; background: rgb(238 242 255); border-radius: 999px; }}
    .canvas-icon {{ position: absolute; inset: 5px; color: rgb(79 70 229); }}
    .canvas-card-content {{ flex: 1; padding: 16px; }}
    .canvas-card-content ul {{ margin: 0; padding-left: 18px; color: #6b7280; font-size: 14px; line-height: 1.8; }}
    .canvas-card-content li {{ margin-bottom: 4px; }}

    .insight-section {{ width: 100%; background: #fff; border-top: 1px solid #e5e7eb; padding: 80px 0 0; display: flex; justify-content: center; }}
    .insight-inner {{ width: 100%; max-width: 768px; padding: 0 24px 0; }}
    .insight-title {{ margin: 0 0 48px; text-align: center; font-size: 36px; font-weight: 800; color: #111827; }}
    .article-body {{ font-family: var(--font-sans); }}
    .article-body blockquote {{ margin: 0 0 32px; padding: 0 0 0 18px; border-left: 4px solid #d1d5db; color: #4b5563; }}
    .article-body blockquote p {{ margin: 0 0 12px; }}
    .article-body h2 {{ margin: 48px 0 18px; padding-left: 16px; border-left: 8px solid #4f46e5; font-family: var(--font-serif); font-size: 30px; font-weight: 700; color: #111827; }}
    .article-body h3 {{ margin: 30px 0 12px; padding-left: 16px; border-left: 8px solid #000; font-family: var(--font-serif); font-size: 22px; font-weight: 700; color: #111827; }}
    .article-body p {{ margin: 0 0 18px; color: #4A5563; font-size: 18px; line-height: 1.9; letter-spacing: 0.01em; }}
    .article-body ul {{ margin: 0 0 18px; padding-left: 24px; color: #4A5563; }}
    .article-body li {{ margin-bottom: 8px; line-height: 1.9; }}
    .article-body table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 15px; }}
    .article-body th, .article-body td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
    .article-body th {{ background: #f8fafc; color: #374151; }}
    .article-body a {{ color: #4f46e5; }}
    .article-body code {{ background: #f3f4f6; border-radius: 6px; padding: 1px 6px; font-size: 0.92em; }}

    .live-link-wrap {{ padding: 36px 0 20px; text-align: center; }}
    .live-link {{ display: inline-flex; align-items: center; gap: 8px; color: #6b7280; font-size: 14px; font-weight: 500; border-bottom: 1px solid #d1d5db; padding-bottom: 2px; }}
    .live-link svg {{ width: 16px; height: 16px; }}
    .live-link:hover {{ color: #000; border-bottom-color: #000; }}

    .site-footer {{ width: 100%; background: #111111; padding: 96px 0 48px; border-top: 1px solid #111111; overflow: hidden; position: relative; margin-top: 0; }}
    .site-footer::before {{ content: 'BusinessModelCraft'; position: absolute; left: 24px; top: 24px; font-family: var(--font-serif); font-size: min(12vw, 128px); line-height: 0.8; color: #fff; opacity: 0.06; letter-spacing: -0.04em; white-space: nowrap; }}
    .site-footer-inner {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }}
    .footer-links {{ display: flex; flex-direction: column; align-items: flex-start; gap: 24px; margin-left: auto; width: fit-content; }}
    .footer-link {{ display: flex; align-items: center; gap: 12px; color: #6b7280; font-size: 14px; font-weight: 500; }}
    .footer-link:hover {{ color: #fff; }}
    .footer-link-icon-wrap {{ width: 32px; height: 32px; border-radius: 999px; background: rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; }}
    .footer-link:hover .footer-link-icon-wrap {{ background: #fff; color: #000; }}
    .footer-link-icon-wrap svg {{ width: 16px; height: 16px; }}
    .footer-bottom {{ border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; padding-top: 20px; display: flex; justify-content: center; color: #6b7280; font-size: 13px; }}

    @media (min-width: 768px) {{
      .footer-links {{ align-items: flex-end; }}
      .footer-bottom {{ justify-content: flex-end; }}
    }}

    @media (max-width: 1023px) {{
      .canvas-grid-top {{ grid-template-columns: repeat(2, minmax(0, 1fr)); grid-template-rows: none; }}
      .canvas-slot[style] {{ grid-column: auto !important; grid-row: auto !important; }}
      .canvas-grid-bottom {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 767px) {{
      .site-header-inner {{ align-items: flex-start; }}
      .brand-title {{ font-size: 18px; }}
      .hero {{ padding-left: 18px; padding-right: 18px; }}
      .breadcrumb, .canvas-section, .insight-inner, .site-header-inner, .site-footer-inner {{ padding-left: 18px; padding-right: 18px; }}
      .nav-right {{ margin-left: auto; }}
      .hero h1 {{ font-size: 36px; }}
      .insight-title {{ font-size: 30px; }}
      .article-body p {{ font-size: 17px; }}
      .canvas-grid-top {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body class="page lang-en" id="page-body">
  <header class="site-header">
    <div class="site-header-inner">
      <a class="brand external-link" data-href-en="{home_en}" data-href-zh="{home_zh}" href="{home_en}" target="_blank" rel="noopener noreferrer">
        <span class="brand-mark">{layers_svg}</span>
        <span class="brand-title">BusinessModelCraft</span>
      </a>
      <nav class="nav-center">
        <a class="nav-pill external-link" data-href-en="{examples_en}" data-href-zh="{examples_zh}" href="{examples_en}" target="_blank" rel="noopener noreferrer">
          <span class="nav-pill-icon">{file_svg}</span><span data-locale="en">Examples</span><span data-locale="zh">案例</span>
        </a>
        <a class="nav-pill external-link" data-href-en="{blog_en}" data-href-zh="{blog_zh}" href="{blog_en}" target="_blank" rel="noopener noreferrer">
          <span class="nav-pill-icon">{book_svg}</span><span data-locale="en">Blog</span><span data-locale="zh">博客</span>
        </a>
        <a class="nav-pill external-link" data-href-en="{guide_en}" data-href-zh="{guide_zh}" href="{guide_en}" target="_blank" rel="noopener noreferrer">
          <span class="nav-pill-icon">{compass_svg}</span><span data-locale="en">Guide</span><span data-locale="zh">入门指南</span>
        </a>
      </nav>
      <div class="nav-right">
        <span style="width:16px;height:16px;">{globe_svg}</span>
        <button class="lang-link active" id="btn-en" onclick="switchLang('en')">EN</button>
        <span>/</span>
        <button class="lang-link" id="btn-zh" onclick="switchLang('zh')">中文</button>
      </div>
    </div>
  </header>

  <main>
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a class="external-link" data-href-en="{home_en}" data-href-zh="{home_zh}" href="{home_en}" target="_blank" rel="noopener noreferrer"><span data-locale="en">{home_text_en}</span><span data-locale="zh">{home_text_zh}</span></a></li>
        <li class="separator">›</li>
        <li><a class="external-link" data-href-en="{examples_en}" data-href-zh="{examples_zh}" href="{examples_en}" target="_blank" rel="noopener noreferrer"><span data-locale="en">{examples_text_en}</span><span data-locale="zh">{examples_text_zh}</span></a></li>
        <li class="separator">›</li>
        <li class="current"><span data-locale="en">{name_en}</span><span data-locale="zh">{name_zh}</span></li>
      </ol>
    </nav>

    <section class="hero">
      <div data-locale="en">
        <span class="industry-tag">{industry_en}</span>
        <h1 class="font-serif">{title_en}</h1>
        <p>{intro_en}</p>
      </div>
      <div data-locale="zh">
        <span class="industry-tag">{industry_zh}</span>
        <h1 class="font-serif">{title_zh}</h1>
        <p>{intro_zh}</p>
      </div>
    </section>

    <section class="canvas-section">
      <div data-locale="en">{canvas_en}</div>
      <div data-locale="zh">{canvas_zh}</div>
    </section>

    <section class="insight-section">
      <div class="insight-inner">
        <h2 class="insight-title font-serif"><span data-locale="en">{editor_take_en}</span><span data-locale="zh">{editor_take_zh}</span></h2>
        <article class="article-body" data-locale="en">{article_en}</article>
        <article class="article-body" data-locale="zh">{article_zh}</article>
{live_link_block}
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="site-footer-inner">
      <div class="footer-links">
        <a class="footer-link" href="mailto:hh@1000idea.com" target="_blank" rel="noopener noreferrer"><span>hh@1000idea.com</span><span class="footer-link-icon-wrap">{mail_svg}</span></a>
        <a class="footer-link external-link" data-href-en="{home_en}" data-href-zh="{home_zh}" href="{home_en}" target="_blank" rel="noopener noreferrer"><span data-locale="en">{home_text_en}</span><span data-locale="zh">{home_text_zh}</span><span class="footer-link-icon-wrap">{home_svg}</span></a>
        <a class="footer-link external-link" data-href-en="{examples_en}" data-href-zh="{examples_zh}" href="{examples_en}" target="_blank" rel="noopener noreferrer"><span data-locale="en">{examples_text_en}</span><span data-locale="zh">{examples_text_zh}</span><span class="footer-link-icon-wrap">{file_svg}</span></a>
        <a class="footer-link external-link" data-href-en="{blog_en}" data-href-zh="{blog_zh}" href="{blog_en}" target="_blank" rel="noopener noreferrer"><span data-locale="en">Blog</span><span data-locale="zh">博客</span><span class="footer-link-icon-wrap">{book_svg}</span></a>
      </div>
      <div class="footer-bottom">
        <span data-locale="en">{footer_note_en}</span>
        <span data-locale="zh">{footer_note_zh}</span>
      </div>
    </div>
  </footer>

  <script>
    function switchLang(lang) {{
      const body = document.getElementById('page-body');
      const btnEn = document.getElementById('btn-en');
      const btnZh = document.getElementById('btn-zh');
      body.classList.remove('lang-en', 'lang-zh');
      body.classList.add(lang === 'zh' ? 'lang-zh' : 'lang-en');
      document.documentElement.lang = lang;
      btnEn.classList.toggle('active', lang === 'en');
      btnZh.classList.toggle('active', lang === 'zh');
      document.title = lang === 'zh' ? {title_zh_js} : {title_en_js};
      document.querySelectorAll('.external-link').forEach((node) => {{
        const href = lang === 'zh' ? node.dataset.hrefZh : node.dataset.hrefEn;
        if (href) node.setAttribute('href', href);
      }});
    }}
  </script>
</body>
</html>'''



def build_html(data: dict, zh_markdown: str, en_markdown: str) -> str:
    slug = data.get("slug", "")
    title_en = data.get("displayTitle_en") or data.get("name_en") or slug or "Case Study"
    title_zh = data.get("displayTitle_zh") or data.get("name_zh") or slug or "案例页"
    content = data.get("content", {})

    is_published = data.get("isPublished", False)
    if is_published:
        _href_en = f"{BASE_URL}/en/examples/{slug}"
        _href_zh = f"{BASE_URL}/zh/examples/{slug}"
        _label_en = html.escape(SITE_TEXT["en"]["open_live"])
        _label_zh = html.escape(SITE_TEXT["zh"]["open_live"])
    else:
        _href_en = f"{BASE_URL}/en"
        _href_zh = f"{BASE_URL}/zh"
        _label_en = html.escape(SITE_TEXT["en"]["visit_site"])
        _label_zh = html.escape(SITE_TEXT["zh"]["visit_site"])
    _arrow = SVG_ICONS["arrow_right"]
    live_link_block = (
        f'        <div class="live-link-wrap">'
        f'<a class="live-link external-link"'
        f' data-href-en="{_href_en}" data-href-zh="{_href_zh}"'
        f' href="{_href_en}" target="_blank" rel="noopener noreferrer">'
        f'<span data-locale="en">{_label_en}</span>'
        f'<span data-locale="zh">{_label_zh}</span>'
        f'<span style="width:16px;height:16px;">{_arrow}</span>'
        f'</a></div>'
    )

    return HTML_TEMPLATE.format(
        global_style_vars=GLOBAL_STYLE_VARS,
        layers_svg=SVG_ICONS["layers"],
        file_svg=SVG_ICONS["file"],
        book_svg=SVG_ICONS["book"],
        compass_svg=SVG_ICONS["compass"],
        globe_svg=SVG_ICONS["globe"],
        mail_svg=SVG_ICONS["mail"],
        home_svg=SVG_ICONS["home"],
        arrow_svg=SVG_ICONS["arrow_right"],
        home_en=f"{BASE_URL}/en",
        home_zh=f"{BASE_URL}/zh",
        examples_en=f"{BASE_URL}/en/examples",
        examples_zh=f"{BASE_URL}/zh/examples",
        blog_en=f"{BASE_URL}/en/blog",
        blog_zh=f"{BASE_URL}/zh/blog",
        guide_en=f"{BASE_URL}/en/blog/business-model-guide",
        guide_zh=f"{BASE_URL}/zh/blog/business-model-guide",
        title_en=html.escape(title_en),
        title_zh=html.escape(title_zh),
        title_en_js=json.dumps(title_en, ensure_ascii=False),
        title_zh_js=json.dumps(title_zh, ensure_ascii=False),
        name_en=html.escape(data.get("name_en", slug)),
        name_zh=html.escape(data.get("name_zh", slug)),
        industry_en=html.escape(data.get("industry_en", "")),
        industry_zh=html.escape(data.get("industry_zh", "")),
        intro_en=html.escape(content.get("intro_en", "")),
        intro_zh=html.escape(content.get("intro_zh", "")),
        canvas_en=render_canvas_grid(content.get("canvas_en", {}), "en"),
        canvas_zh=render_canvas_grid(content.get("canvas_zh", {}), "zh"),
        article_en=markdown_to_html(en_markdown),
        article_zh=markdown_to_html(zh_markdown),
        editor_take_en=SITE_TEXT["en"]["editor_take"],
        editor_take_zh=SITE_TEXT["zh"]["editor_take"],
        craft_cta_en=SITE_TEXT["en"]["craft_cta"],
        craft_cta_zh=SITE_TEXT["zh"]["craft_cta"],
        footer_note_en=SITE_TEXT["en"]["footer_note"],
        footer_note_zh=SITE_TEXT["zh"]["footer_note"],
        home_text_en=SITE_TEXT["en"]["home"],
        home_text_zh=SITE_TEXT["zh"]["home"],
        examples_text_en=SITE_TEXT["en"]["examples"],
        examples_text_zh=SITE_TEXT["zh"]["examples"],
        live_link_block=live_link_block,
    )



def normalize_output_root(output_dir) -> Path:
    if output_dir and output_dir.strip():
        candidate = Path(output_dir).expanduser()
    else:
        candidate = None
        for env_key in OUTPUT_DIR_ENV_KEYS:
            raw_value = os.getenv(env_key, "").strip()
            if raw_value:
                candidate = Path(raw_value).expanduser()
                break
        if candidate is None:
            candidate = Path.home() / "Documents" / OUTPUT_FOLDER_NAME
    if candidate.name == OUTPUT_FOLDER_NAME:
        return candidate
    return candidate / OUTPUT_FOLDER_NAME



def _validate_zh_quotes(raw_json: str, json_path) -> None:
    """检查 JSON 文本中 _zh 字段值里是否混入了 ASCII 直引号（U+0022）。

    由于 Python 的 json.loads 遇到未转义的直引号会直接抛出 JSONDecodeError，
    本函数在 json.loads 之前运行，仅对能通过语法校验的内容做额外警告检查。
    若 json.loads 本身失败，则先尝试诊断是否由 _zh 字段中的直引号引起。
    """
    import re as _re
    # 找出所有 *_zh 键对应的字符串值，检查值内是否包含 ASCII 直引号
    # 简单启发式：匹配 "xxx_zh": "..." 中的值段，看值内是否有未转义的 "
    pattern = _re.compile(r'"[^"]*_zh"\s*:\s*"((?:[^\\"]|\\.)*)"', _re.DOTALL)
    for m in pattern.finditer(raw_json):
        value = m.group(1)
        # 还原转义后检查是否有裸的 ASCII 直引号夹在中文字符之间
        # （排除转义序列 \" 本身，它在 JSON 中是合法的）
        unescaped = value.replace('\\"', '\x00')  # 暂替合法转义引号
        if '"' in unescaped:
            # 找出第一处位置用于提示
            pos = unescaped.index('"')
            ctx = value[max(0, pos - 10):pos + 11]
            print(
                f"⚠️  JSON 质检警告：{json_path.name} 的 _zh 字段中检测到 ASCII 直引号 (U+0022)。\n"
                f"   出现位置附近：...{ctx}...\n"
                f"   请将中文语境中的引号改为弯引号 \u201c...\u201d（U+201C/U+201D）。",
                file=sys.stderr
            )
            break  # 只报第一处，避免刷屏


def generate_case_page(slug: str, output_dir) -> str:
    slug_dir = normalize_output_root(output_dir) / slug
    json_path = slug_dir / f"{slug}.json"
    zh_path = slug_dir / f"{slug}.zh.md"
    en_path = slug_dir / f"{slug}.en.md"

    if not json_path.exists():
        raise FileNotFoundError(f"JSON 文件不存在：{json_path}")
    if not zh_path.exists():
        raise FileNotFoundError(f"中文 Markdown 文件不存在：{zh_path}")
    if not en_path.exists():
        raise FileNotFoundError(f"英文 Markdown 文件不存在：{en_path}")

    raw_json = json_path.read_text(encoding="utf-8")
    _validate_zh_quotes(raw_json, json_path)
    data = json.loads(raw_json)
    zh_markdown = zh_path.read_text(encoding="utf-8")
    en_markdown = en_path.read_text(encoding="utf-8")

    html_path = slug_dir / f"{slug}.html"
    html_path.write_text(build_html(data, zh_markdown, en_markdown), encoding="utf-8")
    return str(html_path.resolve())



def main() -> None:
    if len(sys.argv) < 2:
        print("用法：python3 scripts/start_preview.py <slug> [output_dir]")
        sys.exit(1)

    slug = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        html_path = generate_case_page(slug, output_dir)
        print(f"✅ 本地案例页已生成：{html_path}")
        print(f"🌐 本地预览链接：file://{html_path}")
        print("🖱️ 也可以直接双击该 .html 文件打开")
    except Exception as exc:
        print(f"❌ 生成失败：{exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
