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
            padding: 0.85rem 1rem;
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
            font-size: 1.55rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .odf-section-caption {
            color: #475569;
            font-size: 0.96rem;
            line-height: 1.6;
        }
        .odf-hero-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.35rem;
        }
        .odf-hero-caption {
            color: #334155;
            font-size: 1rem;
            line-height: 1.7;
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
        .odf-step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.75rem;
        }
        .odf-step-item {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            background: #f8fafc;
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
            padding: 0.75rem;
        }
        .odf-paper {
            max-width: 760px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 1.4rem 1.25rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
        }
        .odf-paper-note {
            color: #64748b;
            font-size: 0.74rem;
            margin-top: 0.9rem;
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
    note_html = (
        f"<div class='odf-paper-note'>{escape(note)}</div>"
        if note
        else ""
    )
    return (
        "<div class='odf-paper-shell'>"
        f"<div class='odf-paper'>{inner_html}{note_html}</div>"
        "</div>"
    )
