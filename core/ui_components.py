from __future__ import annotations

from html import escape

import streamlit as st


DEFAULT_EMPTY_HINT = "如果你是第一次使用 ODFlow，建議先到「社團設定」建立示範資料。"

CATEGORY_DOT_COLORS = {
    "日常行政型": "#c2410c",
    "專案活動型": "#15803d",
    "社團運作型": "#1d4ed8",
    "財務與清冊型": "#ca8a04",
}

BADGE_TONES = {
    "primary": {"border": "#bfdbfe", "background": "#eff6ff", "text": "#1d4ed8"},
    "neutral": {"border": "#e5e7eb", "background": "#ffffff", "text": "#374151"},
    "success": {"border": "#bbf7d0", "background": "#f0fdf4", "text": "#15803d"},
    "warning": {"border": "#fde68a", "background": "#fffbeb", "text": "#b45309"},
}


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(219, 234, 254, 0.55), transparent 28%),
                linear-gradient(180deg, #f8fafc 0%, #f4f7fb 100%);
        }
        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(247,250,255,0.98) 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
            top: 1rem;
        }
        section[data-testid="stSidebar"] .odf-sidebar-brand,
        section[data-testid="stSidebar"] .odf-sidebar-card {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #dbe4ef;
            border-radius: 18px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        }
        section[data-testid="stSidebar"] .odf-sidebar-brand {
            padding: 1rem 1rem 0.9rem 1rem;
            margin: 0.2rem 0 0.85rem 0;
        }
        section[data-testid="stSidebar"] .odf-sidebar-card {
            padding: 0.85rem 0.95rem;
            margin-top: 1rem;
        }
        .odf-sidebar-kicker {
            color: #2563eb;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.18rem;
        }
        .odf-sidebar-brand-title {
            color: #0f172a;
            font-size: 1.48rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.18rem;
        }
        .odf-sidebar-brand-caption,
        .odf-sidebar-card-text {
            color: #475569;
            font-size: 0.88rem;
            line-height: 1.55;
        }
        .odf-sidebar-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.65rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 20px;
            border: 1px solid #dbe4ef;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background: transparent;
        }
        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] .odf-card {
            margin-bottom: 0.9rem;
        }
        .odf-hero,
        .odf-card,
        .odf-empty-state,
        .odf-paper-shell,
        .odf-step-shell {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #dbe4ef;
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
        }
        .odf-hero {
            padding: 1.5rem 1.6rem;
        }
        .odf-card {
            padding: 1rem 1.05rem;
        }
        .odf-empty-state {
            padding: 1rem 1.1rem;
        }
        .odf-step-shell {
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .odf-section-kicker {
            color: #1d4ed8;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.18rem;
        }
        .odf-section-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.28rem;
        }
        .odf-section-caption {
            color: #475569;
            font-size: 0.98rem;
            line-height: 1.6;
        }
        .odf-hero-title {
            color: #0f172a;
            font-size: 2.35rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 0.42rem;
        }
        .odf-hero-caption {
            color: #334155;
            font-size: 1.02rem;
            line-height: 1.78;
        }
        .odf-card-title {
            color: #0f172a;
            font-size: 1.04rem;
            font-weight: 700;
            margin-bottom: 0.28rem;
        }
        .odf-card-text {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.6;
        }
        .odf-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.55rem;
        }
        .odf-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            padding: 0.16rem 0.62rem;
            border-radius: 999px;
            border: 1px solid #e5e7eb;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .odf-badge-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            display: inline-block;
            flex: none;
        }
        .odf-panel-kicker {
            color: #64748b;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }
        .odf-panel-title {
            color: #0f172a;
            font-size: 1.14rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 0.36rem;
        }
        .odf-panel-text {
            color: #475569;
            font-size: 0.94rem;
            line-height: 1.65;
        }
        .odf-status-card {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #dbe4ef;
            border-radius: 20px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
            padding: 1rem 1.05rem;
        }
        .odf-status-grid {
            display: grid;
            grid-template-columns: 108px 1fr;
            gap: 0.9rem;
            align-items: center;
        }
        .odf-status-ring {
            width: 108px;
            height: 108px;
            border-radius: 999px;
            background: conic-gradient(#2563eb calc(var(--odf-progress) * 1%), #dbeafe 0);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .odf-status-ring-inner {
            width: 78px;
            height: 78px;
            border-radius: 999px;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 0 1px #dbe4ef;
            color: #0f172a;
        }
        .odf-status-ring-value {
            font-size: 1.12rem;
            font-weight: 800;
            line-height: 1;
        }
        .odf-status-ring-label {
            font-size: 0.72rem;
            color: #64748b;
            margin-top: 0.18rem;
        }
        .odf-status-title {
            color: #0f172a;
            font-size: 1.1rem;
            font-weight: 800;
            margin-bottom: 0.22rem;
        }
        .odf-status-meta {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 0.55rem;
        }
        .odf-status-note {
            color: #64748b;
            font-size: 0.82rem;
            margin-top: 0.55rem;
            line-height: 1.5;
        }
        .odf-workflow {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            align-items: stretch;
        }
        .odf-workflow-step {
            position: relative;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid #dbe4ef;
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem 1rem;
            min-height: 178px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
        }
        .odf-workflow-step:not(:last-child)::after {
            content: "→";
            position: absolute;
            right: -0.72rem;
            top: 50%;
            transform: translateY(-50%);
            color: #2563eb;
            font-size: 1.5rem;
            font-weight: 800;
            background: #f8fafc;
            width: 1.6rem;
            text-align: center;
        }
        .odf-workflow-index {
            color: #2563eb;
            font-size: 0.84rem;
            font-weight: 800;
            margin-bottom: 0.38rem;
        }
        .odf-workflow-title {
            color: #0f172a;
            font-size: 1.04rem;
            font-weight: 800;
            margin-bottom: 0.38rem;
        }
        .odf-workflow-text {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.62;
        }
        .odf-step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.85rem;
        }
        .odf-step-item {
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 0.95rem 1rem;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            min-height: 132px;
        }
        .odf-step-item.is-active {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-color: #93c5fd;
        }
        .odf-step-index {
            color: #1d4ed8;
            font-weight: 800;
            font-size: 0.82rem;
            margin-bottom: 0.28rem;
        }
        .odf-step-title {
            color: #0f172a;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .odf-step-note {
            color: #64748b;
            font-size: 0.83rem;
            margin-top: 0.28rem;
            line-height: 1.5;
        }
        .odf-paper-shell {
            padding: 1rem;
        }
        .odf-paper {
            max-width: 780px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 1.55rem 1.35rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            min-height: 780px;
        }
        .odf-paper-note {
            color: #64748b;
            font-size: 0.74rem;
            margin-top: 0.9rem;
        }
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            border-radius: 12px;
            min-height: 2.8rem;
            font-weight: 700;
            border: 1px solid #d7dfeb;
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
        }
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
        }
        .stButton > button[kind="tertiary"],
        .stDownloadButton > button[kind="tertiary"],
        .stFormSubmitButton > button[kind="tertiary"] {
            border-color: transparent;
            background: transparent;
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            border-radius: 14px;
            border-color: #d7dfeb;
            background: rgba(255, 255, 255, 0.96);
        }
        @media (max-width: 900px) {
            .odf-workflow {
                grid-template-columns: 1fr;
            }
            .odf-workflow-step:not(:last-child)::after {
                display: none;
            }
            .odf-status-grid {
                grid-template-columns: 1fr;
                justify-items: center;
                text-align: center;
            }
            .odf-paper {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_intro(title: str, caption: str, eyebrow: str | None = None) -> None:
    eyebrow_html = (
        f"<div class='odf-section-kicker'>{escape(eyebrow)}</div>" if eyebrow else ""
    )
    st.markdown(
        f"""
        <div>
            {eyebrow_html}
            <div class="odf-section-title">{escape(title)}</div>
            <div class="odf-section-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_panel(title: str, caption: str, eyebrow: str | None = None) -> None:
    eyebrow_html = (
        f"<div class='odf-section-kicker'>{escape(eyebrow)}</div>" if eyebrow else ""
    )
    st.markdown(
        f"""
        <div class="odf-hero">
            {eyebrow_html}
            <div class="odf-hero-title">{escape(title)}</div>
            <div class="odf-hero-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_html(
    text: str,
    tone: str = "neutral",
    dot_color: str | None = None,
) -> str:
    tone_spec = BADGE_TONES.get(tone, BADGE_TONES["neutral"])
    dot_html = (
        f"<span class='odf-badge-dot' style='background:{escape(dot_color)};'></span>"
        if dot_color
        else ""
    )
    return (
        f"<span class='odf-badge' style='border-color:{tone_spec['border']};"
        f"background:{tone_spec['background']};color:{tone_spec['text']};'>"
        f"{dot_html}{escape(text)}</span>"
    )


def category_badge_html(category_name: str) -> str:
    return badge_html(
        category_name,
        tone="neutral",
        dot_color=CATEGORY_DOT_COLORS.get(category_name, "#64748b"),
    )


def card_html(title: str, description: str, badges: list[str] | None = None) -> str:
    badges_html = ""
    if badges:
        badges_html = f"<div class='odf-badge-row'>{''.join(badges)}</div>"
    return (
        "<div class='odf-card'>"
        f"<div class='odf-card-title'>{escape(title)}</div>"
        f"<div class='odf-card-text'>{escape(description)}</div>"
        f"{badges_html}"
        "</div>"
    )


def panel_body_html(
    title: str,
    description: str,
    badges: list[str] | None = None,
    eyebrow: str | None = None,
) -> str:
    eyebrow_html = (
        f"<div class='odf-panel-kicker'>{escape(eyebrow)}</div>" if eyebrow else ""
    )
    badges_html = ""
    if badges:
        badges_html = f"<div class='odf-badge-row'>{''.join(badges)}</div>"
    return (
        f"{eyebrow_html}"
        f"<div class='odf-panel-title'>{escape(title)}</div>"
        f"<div class='odf-panel-text'>{escape(description)}</div>"
        f"{badges_html}"
    )


def status_card_html(
    title: str,
    completion_percentage: int | float,
    subtitle: str,
    badges: list[str] | None = None,
    note: str | None = None,
) -> str:
    safe_progress = max(0, min(100, int(round(float(completion_percentage)))))
    badges_html = (
        f"<div class='odf-badge-row'>{''.join(badges)}</div>"
        if badges
        else ""
    )
    note_html = f"<div class='odf-status-note'>{escape(note)}</div>" if note else ""
    return f"""
        <div class="odf-status-card">
            <div class="odf-status-grid">
                <div class="odf-status-ring" style="--odf-progress:{safe_progress};">
                    <div class="odf-status-ring-inner">
                        <div class="odf-status-ring-value">{safe_progress}%</div>
                        <div class="odf-status-ring-label">完整度</div>
                    </div>
                </div>
                <div>
                    <div class="odf-status-title">{escape(title)}</div>
                    <div class="odf-status-meta">{escape(subtitle)}</div>
                    {badges_html}
                    {note_html}
                </div>
            </div>
        </div>
    """


def render_sidebar_brand(
    project_name: str,
    tagline: str,
    club_name: str,
    academic_year: str,
    campus: str,
) -> None:
    st.sidebar.markdown(
        f"""
        <div class="odf-sidebar-brand">
            <div class="odf-sidebar-kicker">ODFlow</div>
            <div class="odf-sidebar-brand-title">{escape(project_name)}</div>
            <div class="odf-sidebar-brand-caption">{escape(tagline)}</div>
            <div class="odf-sidebar-meta">
                {badge_html(academic_year, tone="primary")}
                {badge_html(campus, tone="neutral")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""
        <div class="odf-sidebar-card">
            <div class="odf-panel-kicker">目前社團</div>
            <div class="odf-panel-title" style="font-size:1rem;margin-bottom:0.2rem;">{escape(club_name)}</div>
            <div class="odf-sidebar-card-text">可先從空白範本、生成文件、檔案庫與社團評鑑完成主要流程。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_steps(steps: list[dict[str, str]]) -> None:
    parts = []
    for index, step in enumerate(steps, start=1):
        parts.append(
            f"""
            <div class="odf-workflow-step">
                <div class="odf-workflow-index">STEP {index}</div>
                <div class="odf-workflow-title">{escape(step['title'])}</div>
                <div class="odf-workflow-text">{escape(step['description'])}</div>
            </div>
            """
        )
    st.markdown(
        f"<div class='odf-workflow'>{''.join(parts)}</div>",
        unsafe_allow_html=True,
    )


def render_stepper(steps: list[dict], active_index: int) -> None:
    items = []
    for index, step in enumerate(steps):
        active_class = " is-active" if index == active_index else ""
        note_html = (
            f"<div class='odf-step-note'>{escape(step['note'])}</div>"
            if step.get("note")
            else ""
        )
        items.append(
            f"""
            <div class="odf-step-item{active_class}">
                <div class="odf-step-index">STEP {index + 1}</div>
                <div class="odf-step-title">{escape(step['title'])}</div>
                {note_html}
            </div>
            """
        )
    st.markdown(
        f"<div class='odf-step-shell'><div class='odf-step-grid'>{''.join(items)}</div></div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, description: str, hint: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="odf-empty-state">
            <div class="odf-card-title">{escape(title)}</div>
            <div class="odf-card-text">{escape(description)}</div>
            <div class="odf-card-text" style="margin-top:0.45rem;color:#64748b;">
                {escape(hint or DEFAULT_EMPTY_HINT)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def paper_preview_shell(inner_html: str, note: str | None = None) -> str:
    note_html = f"<div class='odf-paper-note'>{escape(note)}</div>" if note else ""
    return (
        "<div class='odf-paper-shell'>"
        f"<div class='odf-paper'>{inner_html}{note_html}</div>"
        "</div>"
    )
