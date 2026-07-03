from __future__ import annotations

from html import escape
import re
from urllib.parse import urlencode
import streamlit as st

PRIMARY = "#1D6BFF"
GREEN = "#16A34A"
PURPLE = "#6D4CFF"
CORAL = "#FF5A7A"
CORAL_DARK = "#EF476F"
BORDER = "#E5EDF7"
TEXT = "#0F172A"
MUTED = "#64748B"


def _safe(value: object) -> str:
    return escape(str(value))


def _first_query(name: str, default: str = "") -> str:
    try:
        value = st.query_params.get(name)
    except Exception:
        return default
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


def nav_href(page: str = "home", **params: object) -> str:
    query = {"page": page}
    for key, value in params.items():
        if value is not None and value != "":
            query[key] = value
    return "/?" + urlencode(query, doseq=True)


def _panel_href(active: str, panel: str | None) -> str:
    query = {}
    try:
        query.update(dict(st.query_params))
    except Exception:
        pass
    query.setdefault("page", active or "home")
    if panel:
        query["panel"] = panel
    else:
        query.pop("panel", None)
    return "/?" + urlencode(query, doseq=True)


def _runtime_state() -> dict:
    fallback_settings = {
        "club_name": "ODFlow示範社團",
        "academic_year": "114",
        "campus": "天母校區",
        "club_type": "",
        "president_name": "",
        "advisor_name": "",
    }
    try:
        from core.database import initialize_database
        initialize_database()
    except Exception:
        pass
    try:
        from core.settings_service import get_club_settings
        settings = get_club_settings()
    except Exception:
        settings = fallback_settings
    try:
        from core.document_service import list_documents
        documents = list_documents()
    except Exception:
        documents = []
    try:
        from core.evaluation_service import get_evaluation_summary
        summary = get_evaluation_summary()
    except Exception:
        summary = {
            "overall_completion_percentage": 0,
            "missing_requirements": [],
            "draft_or_pending_documents": 0,
        }
    try:
        from core.template_service import list_template_definitions
        templates = list_template_definitions()
    except Exception:
        templates = []
    return {
        "settings": {**fallback_settings, **(settings or {})},
        "documents": documents or [],
        "summary": summary or {},
        "templates": templates or [],
    }


def _status_counts(documents: list[dict]) -> dict:
    counts = {"draft": 0, "pending": 0, "done": 0, "unfiled": 0}
    for doc in documents:
        status = str(doc.get("status", "")).strip()
        if status == "草稿":
            counts["draft"] += 1
        if status in {"待審", "待確認"}:
            counts["pending"] += 1
        if status in {"正式版", "已歸檔", "已完成"}:
            counts["done"] += 1
        if status not in {"已歸檔", "正式版", "已完成"}:
            counts["unfiled"] += 1
    return counts


def _doc_title(doc: dict, fallback: str = "未命名文件") -> str:
    return _safe(doc.get("title") or doc.get("document_title") or fallback)


def _doc_type(doc: dict) -> str:
    return _safe(doc.get("document_type") or doc.get("template_type") or "文件")


def _doc_status(doc: dict) -> str:
    return _safe(doc.get("status") or "草稿")


def _doc_updated(doc: dict) -> str:
    return _safe(doc.get("updated_at") or doc.get("created_at") or "-")


def _empty_block(title: str, desc: str, action_label: str = "", href: str = "#") -> str:
    action = f'<a class="odf-btn soft" style="margin-top:16px;" href="{href}">{action_label} →</a>' if action_label else ""
    return f'<div class="odf-card" style="padding:28px;text-align:center;background:#f8fbff;border-style:dashed;"><div style="font-size:42px;margin-bottom:10px;">📭</div><h3 style="font-size:18px;margin:0 0 8px 0;">{title}</h3><p class="odf-muted" style="margin:0;">{desc}</p>{action}</div>'


def inject_exact_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --sidebar-w: clamp(272px, 18.2vw, 304px);
            --topbar-h: 68px;
            --page-max: 1304px;
            --bg: #f7faff;
            --card: #ffffff;
            --border: #e5edf7;
            --text: #0f172a;
            --muted: #64748b;
            --primary: #1d6bff;
            --green: #16a34a;
            --purple: #6d4cff;
            --coral: #ff5a7a;
            --coral-dark: #ef476f;
            --shadow: 0 12px 28px rgba(15, 23, 42, 0.055);
            --shadow-soft: 0 8px 18px rgba(15, 23, 42, 0.045);
            --radius: 16px;
        }

        html, body, .stApp {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            min-height: 100vh !important;
            background: var(--bg) !important;
            color: var(--text) !important;
            font-family: "Noto Sans TC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            overflow-x: hidden !important;
        }

        header[data-testid="stHeader"],
        section[data-testid="stSidebar"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .stApp > div,
        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewContainer"] > .main,
        section.main {
            background: var(--bg) !important;
        }

        .odf-shell {
            min-height: 100vh;
            width: 100%;
            display: flex;
            background:
                radial-gradient(circle at 35% 10%, rgba(219, 234, 254, 0.72), transparent 32%),
                linear-gradient(180deg, #fbfdff 0%, #f7faff 46%, #f4f8fe 100%);
        }

        .odf-sidebar {
            width: var(--sidebar-w);
            min-width: var(--sidebar-w);
            height: 100vh;
            position: sticky;
            top: 0;
            box-sizing: border-box;
            padding: 26px 22px 20px 22px;
            background: rgba(255,255,255,0.98);
            border-right: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .odf-brand {
            height: 58px;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 28px;
            flex: none;
        }

        .odf-logo {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: radial-gradient(circle, #e0f2fe 0%, #38bdf8 42%, #1d4ed8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 23px;
            box-shadow: inset 0 0 0 3px rgba(255,255,255,.88), 0 7px 16px rgba(29,78,216,.18);
            flex: none;
        }

        .odf-brand-title {
            font-size: 24px;
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: -0.035em;
            margin: 0;
            color: #0f172a;
        }

        .odf-brand-subtitle {
            margin-top: 5px;
            color: #475569;
            font-size: 12.5px;
            line-height: 1.25;
            font-weight: 650;
            white-space: nowrap;
        }

        .odf-nav { flex: none; }
        .odf-nav-group { margin: 0 0 26px 0; }
        .odf-nav-heading {
            color: #334155;
            font-weight: 850;
            font-size: 14px;
            line-height: 18px;
            margin: 0 0 10px 4px;
        }

        .odf-nav-item {
            height: 42px;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 14px;
            border-radius: 11px;
            color: #405168 !important;
            text-decoration: none !important;
            font-weight: 760;
            font-size: 16px;
            line-height: 42px;
            margin: 0 0 6px 0;
            box-sizing: border-box;
            white-space: nowrap;
        }

        .odf-nav-item:hover { background: #f1f5fb; color: #1d4ed8 !important; }
        .odf-nav-item.active { background: #eaf2ff; color: #1457d9 !important; }
        .odf-nav-icon { width: 22px; min-width: 22px; text-align: center; font-size: 17px; }

        .odf-sidebar-divider {
            height: 1px;
            background: #e7edf4;
            margin: 2px 0 22px 0;
            flex: none;
        }

        .odf-sidebar-spacer { flex: 1; min-height: 12px; }

        .odf-club-card {
            flex: none;
            width: 100%;
            min-height: 136px;
            box-sizing: border-box;
            border: 1px solid var(--border);
            background: #fff;
            border-radius: 16px;
            padding: 18px 18px 16px 18px;
            box-shadow: var(--shadow-soft);
        }

        .odf-kicker,
        .odf-page-eyebrow {
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: .12em;
            font-weight: 900;
            font-size: 11px;
            line-height: 16px;
        }

        .odf-club-name { font-size: 18px; font-weight: 880; margin-top: 8px; line-height: 1.2; }
        .odf-chip-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 11px; }
        .odf-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 24px;
            border-radius: 999px;
            padding: 0 10px;
            font-size: 12px;
            font-weight: 820;
            border: 1px solid #dbe7f8;
            background: #f8fbff;
            color: #33506e;
            white-space: nowrap;
        }
        .odf-chip.blue { background: #eaf2ff; color: #1d6bff; border-color: #bfd8ff; }
        .odf-switch-link {
            height: 34px;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid #e7edf4;
            color: #475569;
            font-size: 13px;
            text-decoration: none !important;
            font-weight: 700;
        }

        .odf-main {
            width: calc(100% - var(--sidebar-w));
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .odf-topbar {
            height: var(--topbar-h);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 16px;
            padding: 0 44px;
            box-sizing: border-box;
            background: rgba(255,255,255,.78);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(231, 237, 244, .78);
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .odf-icon-btn,
        .odf-user-pill {
            height: 42px;
            border-radius: 999px;
            background: #fff;
            border: 1px solid var(--border);
            box-shadow: 0 6px 14px rgba(15,23,42,.045);
            color: #0f172a !important;
            text-decoration: none !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .odf-icon-btn { width: 42px; font-weight: 900; }
        .odf-user-pill { gap: 10px; padding: 0 14px 0 8px; font-size: 15px; font-weight: 820; }
        .odf-avatar {
            width: 32px;
            height: 32px;
            border-radius: 999px;
            background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 900;
        }

        .odf-content {
            width: min(var(--page-max), calc(100vw - var(--sidebar-w) - 56px));
            max-width: var(--page-max);
            min-width: 0;
            margin: 0 auto;
            padding: 39px 0 44px 0;
            box-sizing: border-box;
        }

        .odf-page-header { margin-bottom: 28px; }
        .odf-page-title {
            font-size: 40px;
            line-height: 1.05;
            letter-spacing: -0.06em;
            font-weight: 920;
            margin: 4px 0 13px 0;
            color: #0f172a;
        }
        .odf-page-desc {
            color: #64748b;
            font-size: 16px;
            font-weight: 650;
            margin: 0;
            line-height: 1.45;
        }

        .odf-grid { display: grid; gap: 20px; }
        .odf-card, .odf-card * { box-sizing: border-box; }
        .odf-card {
            background: rgba(255,255,255,.97);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: var(--shadow-soft);
            overflow: visible;
        }
        .odf-card.pad { padding: 24px 26px; }

        .odf-section-title {
            font-size: 19px;
            font-weight: 900;
            line-height: 1.35;
            margin: 0 0 14px 0;
            color: #0f172a;
        }
        .odf-muted, .odf-mini {
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
            font-weight: 650;
        }

        .odf-btn {
            height: 44px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 0 18px;
            text-decoration: none !important;
            border: 1px solid transparent;
            font-weight: 850;
            font-size: 15px;
            line-height: 44px;
            box-sizing: border-box;
            white-space: nowrap;
        }
        .odf-btn.full { width: 100%; }
        .odf-btn.primary { background: var(--primary); color: #fff !important; box-shadow: 0 10px 20px rgba(29,107,255,.16); }
        .odf-btn.green { background: var(--green); color: #fff !important; box-shadow: 0 10px 20px rgba(22,163,74,.14); }
        .odf-btn.purple { background: var(--purple); color: #fff !important; box-shadow: 0 10px 20px rgba(109,76,255,.14); }
        .odf-btn.coral { background: var(--coral); color: #fff !important; box-shadow: 0 10px 20px rgba(255,90,122,.16); }
        .odf-btn.outline { background: #fff; border-color: #d8e4f2; color: var(--primary) !important; }
        .odf-btn.soft { background: #eef5ff; color: var(--primary) !important; border-color: #d8e8ff; }

        .odf-doc-icon {
            width: 64px;
            height: 64px;
            border-radius: 24px;
            background: #eaf2ff;
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            flex: none;
        }
        .odf-doc-icon.green { background: #eaf8ef; color: var(--green); }
        .odf-doc-icon.purple { background: #f0ebff; color: var(--purple); }
        .odf-doc-icon.orange { background: #fff4e8; color: #f97316; }
        .odf-doc-icon.red { background: #fff1ee; color: #ef4444; }

        .odf-tag {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            height: 26px;
            padding: 0 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 850;
            border: 1px solid #e5e7eb;
            background: #f8fafc;
            color: #334155;
            white-space: nowrap;
            line-height: 26px;
        }
        .odf-tag.odt, .odf-tag.blue { background: #eaf2ff; color: #1d6bff; border-color: #cfe1ff; }
        .odf-tag.ods, .odf-tag.green { background: #eaf8ef; color: #16a34a; border-color: #ccefd7; }
        .odf-tag.red { background: #fff1ee; color: #ef4444; border-color: #ffd7cf; }
        .odf-tag.orange { background: #fff4e8; color: #f97316; border-color: #fed7aa; }
        .odf-tag.gray { background: #f1f5f9; color: #64748b; border-color: #e2e8f0; }

        .odf-home-row-top {
            display: grid;
            grid-template-columns: minmax(0, 1.62fr) minmax(360px, 0.98fr);
            gap: 20px;
            margin-bottom: 24px;
            align-items: stretch;
        }
        .odf-hero-card {
            min-height: 262px;
            padding: 28px 32px;
            display: grid;
            grid-template-columns: minmax(145px, 176px) minmax(0, 1fr);
            gap: 28px;
            align-items: center;
            overflow: visible;
        }
        .odf-hero-illus {
            width: 150px;
            height: 150px;
            border-radius: 64px;
            background: linear-gradient(135deg, #eaf2ff, #f8fbff);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            margin-left: 2px;
        }
        .odf-hero-illus .folder { font-size: 72px; transform: translateY(3px); }
        .odf-hero-illus .odf-bubble {
            position: absolute;
            right: -8px;
            top: 36px;
            width: 54px;
            height: 54px;
            border-radius: 999px;
            background: #fff;
            border: 1px solid #dbe7f8;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-weight: 920;
            font-size: 16px;
        }
        .odf-hero-title {
            font-size: clamp(20px, 1.6vw, 22px);
            line-height: 1.35;
            letter-spacing: -0.02em;
            margin: 10px 0 10px 0;
            color: #0f172a;
            font-weight: 900;
        }
        .odf-hero-desc {
            margin: 0 0 20px 0;
            color: #475569;
            font-size: 14.5px;
            line-height: 1.65;
            font-weight: 650;
            max-width: 100%;
        }
        .odf-home-stat-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(86px, 1fr));
            gap: 10px;
            width: 100%;
        }
        .odf-stat-mini {
            min-height: 74px;
            border: 1px solid var(--border);
            border-radius: 13px;
            background: #fff;
            display: grid;
            grid-template-columns: 32px minmax(0, 1fr);
            align-items: center;
            gap: 8px;
            padding: 8px 9px;
            box-sizing: border-box;
            min-width: 0;
            overflow: hidden;
        }
        .odf-stat-mini .stat-icon {
            width: 30px;
            height: 30px;
            border-radius: 10px;
            background: #eaf2ff;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 18px;
            flex: none;
        }
        .odf-stat-mini.green .stat-icon { background: #eaf8ef; color: var(--green); }
        .odf-stat-mini strong {
            display: block;
            font-size: 18px;
            line-height: 1.05;
            font-weight: 920;
            white-space: nowrap;
        }
        .odf-stat-mini span {
            display: block;
            color: #475569;
            font-size: 10.5px;
            line-height: 1.25;
            font-weight: 700;
            margin-top: 3px;
            white-space: normal;
        }

        .odf-eval-card {
            min-height: 262px;
            padding: 22px 28px 24px 28px;
            border-color: #ffc4bc;
            background: linear-gradient(180deg,#fff,#fffaf9);
            overflow: visible;
        }
        .odf-eval-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 18px;
        }
        .odf-eval-title { font-size: 19px; font-weight: 900; line-height: 1.3; margin: 0; }
        .odf-eval-layout {
            display: grid;
            grid-template-columns: 142px minmax(0, 1fr);
            gap: 22px;
            align-items: center;
            margin-bottom: 16px;
        }
        .odf-ring {
            --pct: 0;
            --size: 132px;
            --accent: var(--coral);
            width: var(--size);
            height: var(--size);
            border-radius: 999px;
            background: conic-gradient(var(--accent) calc(var(--pct) * 1%), #edf2f7 0);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .odf-ring-inner {
            width: calc(var(--size) - 38px);
            height: calc(var(--size) - 38px);
            border-radius: 999px;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            box-shadow: inset 0 0 0 1px #e7edf4;
        }
        .odf-ring-value { font-size: 28px; font-weight: 920; line-height: 1; }
        .odf-ring-label { color: #475569; font-size: 12px; line-height: 1.2; font-weight: 800; margin-top: 7px; }
        .odf-eval-status-list { display: flex; flex-direction: column; gap: 13px; min-width: 0; }
        .odf-eval-status {
            height: 40px;
            border-radius: 12px;
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 10px;
            align-items: center;
            padding: 0 14px;
            font-size: 14px;
            font-weight: 880;
            white-space: nowrap;
        }
        .odf-eval-note {
            color: #64748b;
            font-size: 13px;
            font-weight: 700;
            line-height: 1.4;
            margin: 0 0 12px 0;
        }
        .odf-eval-card .odf-btn { height: 46px; }

        .odf-row-title { font-size: 23px; font-weight: 920; line-height: 1.2; margin: 0 0 16px 0; }
        .odf-home-row-action {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 20px;
            margin-bottom: 16px;
        }
        .odf-action-card {
            min-height: 208px;
            padding: 22px 24px 24px 24px;
            display: grid;
            grid-template-columns: 92px minmax(0, 1fr);
            grid-template-rows: minmax(108px, auto) 46px;
            gap: 14px 20px;
            align-items: center;
        }
        .odf-action-card .odf-doc-icon { width: 72px; height: 72px; border-radius: 28px; font-size: 32px; }
        .odf-action-title { font-size: 21px; font-weight: 900; line-height: 1.3; margin: 0 0 8px 0; }
        .odf-action-desc { color: #475569; font-size: 14px; line-height: 1.55; font-weight: 650; margin: 0; }
        .odf-action-card .odf-btn { grid-column: 1 / 3; height: 46px; margin-top: 2px; }

        .odf-home-row-bottom {
            display: grid;
            grid-template-columns: 1fr 1fr .82fr .82fr;
            gap: 14px;
            align-items: stretch;
        }
        .odf-bottom-card { min-height: 230px; padding: 18px 20px; }
        .odf-row-line {
            min-height: 40px;
            display: grid;
            grid-template-columns: 22px 1fr 54px 70px;
            gap: 8px;
            align-items: center;
            border-bottom: 1px solid #edf2f7;
            font-size: 13px;
            font-weight: 720;
        }
        .odf-file-quick-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
        .odf-file-quick-item {
            height: 86px;
            border: 1px solid var(--border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            background: #fff;
            text-align: center;
        }
        .odf-file-quick-item .icon { font-size: 25px; line-height: 1; }
        .odf-file-quick-item strong { font-size: 13px; line-height: 1.1; }
        .odf-file-quick-item .odf-mini { font-size: 11px; line-height: 1.2; }

        .odf-input {
            height: 48px;
            border: 1px solid #dbe7f4;
            background: #fff;
            color: #475569;
            border-radius: 12px;
            padding: 0 16px;
            display: flex;
            align-items: center;
            font-size: 14px;
            font-weight: 650;
            box-sizing: border-box;
        }
        .odf-field label { display:block; font-size: 13px; font-weight: 850; color:#334155; margin:0 0 8px 0; }
        .odf-textarea { min-height: 74px; align-items: flex-start; padding-top: 14px; line-height: 1.55; }

        .odf-progress { height: 8px; background:#e7edf4; border-radius:999px; overflow:hidden; }
        .odf-progress span { display:block; height:100%; background:var(--primary); border-radius:999px; }

        .odf-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .odf-table th {
            height: 46px;
            text-align: left;
            color:#64748b;
            font-size:12px;
            font-weight:850;
            border-bottom:1px solid #edf2f7;
        }
        .odf-table td {
            height: 58px;
            border-bottom:1px solid #edf2f7;
            color:#334155;
            font-weight:650;
            vertical-align: middle;
        }

        .odf-template-thumb {
            width: 100px;
            height: 132px;
            border: 1px solid #dbe4ef;
            border-radius: 8px;
            background:
                linear-gradient(#ffffff,#ffffff) padding-box,
                linear-gradient(180deg,#f8fafc,#e2e8f0) border-box;
            position: relative;
            box-shadow: 0 8px 18px rgba(15,23,42,.045);
        }
        .odf-template-thumb::before {
            content: "";
            position: absolute;
            left: 17px;
            right: 17px;
            top: 22px;
            height: 4px;
            background: #cbd5e1;
            box-shadow:
                0 14px 0 #e2e8f0,
                0 28px 0 #e2e8f0,
                0 42px 0 #e2e8f0,
                0 56px 0 #e2e8f0;
        }
        .odf-template-thumb.sheet::after {
            content: "";
            position: absolute;
            left: 12px;
            right: 12px;
            top: 42px;
            height: 54px;
            background:
                linear-gradient(#bbf7d0 0 0) top/100% 16px no-repeat,
                repeating-linear-gradient(to right, transparent 0 25%, #dbe4ef 25% calc(25% + 1px), transparent calc(25% + 1px) 50%),
                repeating-linear-gradient(to bottom, transparent 0 18px, #dbe4ef 18px 19px);
            border: 1px solid #bbf7d0;
        }

        .odf-stepper {
            height: 62px;
            display: grid;
            grid-template-columns: repeat(4,1fr);
            align-items: center;
            gap: 0;
            margin: 0 18px 24px 18px;
        }
        .odf-step { position: relative; display: flex; align-items: center; gap: 12px; color:#64748b; font-weight:850; }
        .odf-step::after {
            content: "";
            position: absolute;
            left: 58px;
            right: 20px;
            top: 50%;
            height: 2px;
            background:#dbe7f4;
            transform: translateY(-50%);
            z-index: 0;
        }
        .odf-step:last-child::after { display: none; }
        .odf-step-badge {
            width: 36px;
            height: 36px;
            border-radius: 999px;
            background:#eef2f7;
            border:1px solid #dbe7f4;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#334155;
            z-index: 1;
            font-weight:900;
        }
        .odf-step.active, .odf-step.done { color:#1d6bff; }
        .odf-step.active .odf-step-badge { background:#1d6bff; color:#fff; border-color:#1d6bff; }
        .odf-step.done .odf-step-badge { background:#fff; color:#1d6bff; border-color:#b7d2ff; }



        .odf-template-card {
            min-height: 226px;
            padding: 18px;
            display: grid;
            grid-template-columns: 104px minmax(0, 1fr);
            gap: 16px;
            align-items: center;
            overflow: visible;
        }
        .odf-template-card .odf-template-actions {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            gap: 8px;
            width: 100%;
        }
        .odf-template-card .odf-template-actions .odf-btn {
            min-width: 0;
            width: 100%;
            height: 34px;
            padding: 0 8px;
            font-size: 12px;
        }
        .odf-generate-template-card {
            min-height: 190px;
            padding: 16px;
            display: grid;
            grid-template-columns: 82px minmax(0, 1fr);
            gap: 14px;
            overflow: visible;
        }
        .odf-generate-template-card .odf-btn {
            height: 34px;
            font-size: 13px;
            width: 100%;
            margin-top: 4px;
        }
        .odf-generate-template-card p {
            min-height: 38px;
        }


        .odf-panel-overlay {
            position: fixed;
            inset: 0;
            z-index: 9999;
            background: rgba(15, 23, 42, .12);
            display: flex;
            justify-content: flex-end;
            align-items: stretch;
            animation: odfFadeIn .16s ease-out;
        }
        .odf-panel {
            width: 380px;
            max-width: calc(100vw - 32px);
            height: 100vh;
            background: #fff;
            border-left: 1px solid var(--border);
            box-shadow: -18px 0 36px rgba(15, 23, 42, .10);
            padding: 28px;
            box-sizing: border-box;
            overflow-y: auto;
        }
        .odf-panel-head {
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:20px;
        }
        .odf-panel-title {
            font-size:24px;
            font-weight:920;
            margin:0;
            letter-spacing:-.03em;
        }
        .odf-panel-close {
            width:38px;
            height:38px;
            border-radius:999px;
            background:#f8fafc;
            border:1px solid var(--border);
            display:flex;
            align-items:center;
            justify-content:center;
            text-decoration:none!important;
            color:#334155!important;
            font-weight:900;
        }
        .odf-panel-list {
            display:grid;
            gap:12px;
        }
        .odf-panel-item {
            border:1px solid var(--border);
            border-radius:14px;
            padding:14px 16px;
            background:#fbfdff;
        }
        @keyframes odfFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .stApp {
            transition: background-color .12s ease-out;
        }


        .odf-filter-form {
            display: grid;
            grid-template-columns: 1.7fr .78fr .68fr .78fr 112px;
            gap: 14px;
            margin-bottom: 16px;
            align-items: center;
        }
        .odf-filter-control {
            width: 100%;
            height: 48px;
            border: 1px solid #dbe7f4;
            background: #fff;
            color: #475569;
            border-radius: 12px;
            padding: 0 16px;
            font-size: 14px;
            font-weight: 650;
            box-sizing: border-box;
            outline: none;
            font-family: inherit;
        }
        .odf-filter-control:focus {
            border-color: #1d6bff;
            box-shadow: 0 0 0 3px rgba(29,107,255,.10);
        }
        .odf-filter-submit {
            height: 48px;
            border: 1px solid #d8e4f2;
            border-radius: 12px;
            background: #ffffff;
            color: #1d6bff;
            font-size: 14px;
            font-weight: 850;
            font-family: inherit;
            cursor: pointer;
        }
        .odf-template-empty {
            grid-column: 1 / -1;
        }
        .odf-stepper {
            height: 56px !important;
            display: grid !important;
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
            align-items: center !important;
            gap: 16px !important;
            margin: 0 0 24px 0 !important;
            overflow: hidden !important;
        }
        .odf-step {
            min-width: 0 !important;
            display: grid !important;
            grid-template-columns: 38px minmax(0, auto) 1fr !important;
            align-items: center !important;
            gap: 12px !important;
            color: #64748b;
            font-weight: 850;
            position: relative;
        }
        .odf-step::after {
            display: none !important;
        }
        .odf-step::before {
            content: "";
            display: block;
            height: 2px;
            background: #dbe7f4;
            grid-column: 3;
            grid-row: 1;
            width: 100%;
        }
        .odf-step:last-child::before {
            display: none !important;
        }
        .odf-step-badge {
            width: 36px !important;
            height: 36px !important;
            grid-column: 1;
            grid-row: 1;
        }
        .odf-step-label {
            grid-column: 2;
            grid-row: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 15px;
            line-height: 36px;
            position: relative;
            z-index: 2;
        }
        .odf-generate-shell {
            display: grid;
            grid-template-columns: minmax(220px, 260px) minmax(0, 1fr);
            gap: 22px;
            min-height: 640px;
        }
        .odf-generate-main-card {
            overflow: visible !important;
        }

        .odf-settings-layout {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 22px;
            align-items: start;
        }
        .odf-settings-nav {
            position: sticky;
            top: 92px;
            padding: 14px;
            min-height: 420px;
        }
        .odf-settings-nav-title {
            color: #64748b;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin: 4px 8px 12px 8px;
        }
        .odf-settings-nav-item {
            height: 44px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 0 12px;
            text-decoration: none !important;
            color: #475569 !important;
            font-size: 14px;
            font-weight: 820;
            margin-bottom: 6px;
        }
        .odf-settings-nav-item:hover {
            background: #f1f6ff;
            color: #1d6bff !important;
        }
        .odf-settings-nav-item.active {
            background: #eaf2ff;
            color: #1d6bff !important;
        }
        .odf-settings-content {
            display: grid;
            gap: 18px;
        }
        .odf-settings-section-head {
            margin-bottom: 12px;
        }
        .odf-settings-section-head h2 {
            font-size: 24px;
            line-height: 1.25;
            font-weight: 920;
            letter-spacing: -.035em;
            margin: 0 0 6px 0;
            color: #0f172a;
        }
        .odf-settings-section-head p {
            margin: 0;
            color: #64748b;
            font-size: 14px;
            line-height: 1.55;
            font-weight: 650;
        }
        .odf-settings-card {
            padding: 0;
            overflow: hidden !important;
        }
        .odf-setting-row {
            min-height: 76px;
            display: grid;
            grid-template-columns: minmax(260px, 1fr) minmax(170px, 260px) 96px;
            gap: 18px;
            align-items: center;
            padding: 18px 22px;
            border-bottom: 1px solid #e7edf4;
            box-sizing: border-box;
        }
        .odf-setting-row:last-child {
            border-bottom: none;
        }
        .odf-setting-main strong {
            display: block;
            color: #0f172a;
            font-size: 15px;
            line-height: 1.35;
            font-weight: 900;
            margin-bottom: 5px;
        }
        .odf-setting-main span {
            display: block;
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
            font-weight: 650;
        }
        .odf-setting-value {
            color: #334155;
            font-size: 14px;
            line-height: 1.45;
            font-weight: 760;
            text-align: left;
        }
        .odf-setting-action {
            justify-self: end;
            min-width: 78px;
            height: 34px;
            border-radius: 10px;
            border: 1px solid #d8e4f2;
            background: #ffffff;
            color: #1d6bff !important;
            text-decoration: none !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0 12px;
            box-sizing: border-box;
            font-size: 13px;
            font-weight: 850;
        }
        .odf-settings-note {
            border: 1px solid #cfe1ff;
            background: linear-gradient(90deg, #eff6ff, #fbfdff);
            border-radius: 16px;
            padding: 18px 20px;
            color: #475569;
            font-size: 14px;
            line-height: 1.65;
            font-weight: 650;
        }
        @media (max-width: 1280px) {
            .odf-settings-layout {
                grid-template-columns: 1fr;
            }
            .odf-settings-nav {
                position: static;
                min-height: auto;
            }
            .odf-setting-row {
                grid-template-columns: 1fr;
                gap: 8px;
            }
            .odf-setting-action {
                justify-self: start;
            }
        }

        @media (max-width: 1500px) {
            .odf-filter-form {
                grid-template-columns: 1.35fr .74fr .66fr .74fr 104px;
                gap: 12px;
            }
            .odf-stepper {
                gap: 12px !important;
            }
            .odf-step {
                grid-template-columns: 36px minmax(0, auto) 1fr !important;
                gap: 10px !important;
            }
            .odf-step-label {
                font-size: 14px;
            }
            .odf-generate-shell {
                grid-template-columns: 230px minmax(0, 1fr);
            }
        }
        @media (max-width: 1280px) {
            .odf-filter-form {
                grid-template-columns: 1fr 1fr;
            }
            .odf-filter-form .odf-filter-submit {
                grid-column: 1 / -1;
            }
            .odf-stepper {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
                height: auto !important;
                gap: 12px !important;
            }
            .odf-step::before {
                display: none !important;
            }
            .odf-generate-shell {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 1500px) {
            .odf-content {
                width: calc(100vw - var(--sidebar-w) - 44px);
            }
            .odf-home-row-top {
                grid-template-columns: minmax(0, 1.55fr) minmax(330px, .92fr);
                gap: 18px;
            }
            .odf-hero-card {
                padding: 24px 26px;
                grid-template-columns: minmax(128px, 150px) minmax(0, 1fr);
                gap: 22px;
            }
            .odf-hero-illus {
                width: 132px;
                height: 132px;
                border-radius: 52px;
            }
            .odf-hero-illus .folder { font-size: 62px; }
            .odf-hero-title { font-size: 20px; }
            .odf-hero-desc { font-size: 13.5px; line-height: 1.55; margin-bottom: 16px; }
            .odf-home-stat-grid { gap: 8px; }
            .odf-stat-mini { grid-template-columns: 28px minmax(0, 1fr); padding: 7px 8px; }
            .odf-stat-mini .stat-icon { width: 26px; height: 26px; font-size: 15px; }
            .odf-stat-mini strong { font-size: 16px; }
            .odf-stat-mini span { font-size: 10px; }
            .odf-eval-card { padding: 22px 24px; }
            .odf-eval-layout { grid-template-columns: 128px minmax(0, 1fr); gap: 18px; }
            .odf-ring { --size: 118px !important; }
            .odf-eval-status { font-size: 13px; padding: 0 12px; }
            .odf-home-row-bottom { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }

        @media (max-width: 1280px) {
            :root { --sidebar-w: 252px; }
            .odf-sidebar { padding-left: 18px; padding-right: 18px; }
            .odf-brand-title { font-size: 22px; }
            .odf-brand-subtitle { font-size: 11.5px; white-space: normal; }
            .odf-content { width: calc(100vw - var(--sidebar-w) - 32px); }
            .odf-home-row-top { grid-template-columns: 1fr; }
            .odf-home-row-action { grid-template-columns: 1fr; }
            .odf-home-row-bottom { grid-template-columns: 1fr; }
        }

        @media (max-height: 820px) {
            .odf-sidebar { padding-top: 18px; padding-bottom: 14px; }
            .odf-brand { margin-bottom: 18px; height: 50px; }
            .odf-logo { width: 44px; height: 44px; font-size: 20px; }
            .odf-brand-title { font-size: 22px; }
            .odf-brand-subtitle { font-size: 12px; }
            .odf-nav-group { margin-bottom: 18px; }
            .odf-nav-item { height: 38px; line-height: 38px; margin-bottom: 4px; }
            .odf-club-card { min-height: 118px; padding: 14px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



def _nav_item(active: str, page: str, icon: str, label: str) -> str:
    cls = " active" if active.lower() == page.lower() else ""
    return f'<a class="odf-nav-item{cls}" href="{nav_href(page)}"><span class="odf-nav-icon">{icon}</span><span>{label}</span></a>'


def _sidebar(active: str) -> str:
    groups = [
        ("工作台", [("home", "🏠", "首頁"), ("Dashboard", "📊", "儀表板")]),
        ("文件製作", [("Templates", "📚", "空白範本"), ("Generate", "📝", "生成文件"), ("Files", "🗂️", "檔案庫")]),
        ("評鑑管理", [("Evaluation", "📦", "社團評鑑")]),
        ("社團資料", [("Settings", "⚙️", "社團設定")]),
        ("系統支援", [("Projects", "🧭", "專案")]),
    ]
    html = '<aside class="odf-sidebar">'
    html += '<div class="odf-brand"><div class="odf-logo">🏫</div><div><h1 class="odf-brand-title">ODFlow</h1><div class="odf-brand-subtitle">台灣學生社團 ODF 文件工作台</div></div></div>'
    html += '<nav class="odf-nav">'
    for title, items in groups:
        html += f'<div class="odf-nav-group"><div class="odf-nav-heading">{title}</div>'
        for page, icon, label in items:
            html += _nav_item(active, page, icon, label)
        html += '</div>'
    html += '</nav><div class="odf-sidebar-spacer"></div><div class="odf-sidebar-divider"></div>'
    html += '<div class="odf-club-card"><div class="odf-kicker">ODFlow 社團</div><div class="odf-club-name">天母校區 <span class="odf-chip blue">114</span></div><a class="odf-switch-link" href="/?page=Settings"><span>切換社團</span><span>›</span></a></div>'
    html += '<a class="odf-btn outline full" style="height:44px;margin-top:12px;color:#475569!important;" href="/?page=Projects">前往服務中心 ↗</a>'
    html += '</aside>'
    return html


def _topbar(active: str) -> str:
    return (
        '<div class="odf-topbar">'
        f'<a class="odf-icon-btn" href="{_panel_href(active, "help")}">?</a>'
        f'<a class="odf-icon-btn" href="{_panel_href(active, "notifications")}">🔔</a>'
        f'<a class="odf-user-pill" href="{_panel_href(active, "profile")}"><span class="odf-avatar">OD</span><span>社團小幫手</span><span>⌄</span></a>'
        '</div>'
    )


def _panel(active: str) -> str:
    panel = _first_query("panel", "")
    if not panel:
        return ""
    close_href = _panel_href(active, None)
    if panel == "help":
        title = "使用說明"
        body = (
            '<div class="odf-panel-list">'
            '<div class="odf-panel-item"><strong>快速開始</strong><p class="odf-muted">先下載空白範本，或直接到生成文件建立正式文件。</p></div>'
            '<div class="odf-panel-item"><strong>文件流程</strong><p class="odf-muted">範本 → 填寫資料 → 預覽確認 → 下載 / 檔案庫。</p></div>'
            '<div class="odf-panel-item"><strong>評鑑整理</strong><p class="odf-muted">社團評鑑頁會整理缺件、待補與待審核資料。</p></div>'
            f'<a class="odf-btn soft full" href="{nav_href("Projects")}">前往服務中心 →</a>'
            '</div>'
        )
    elif panel == "notifications":
        title = "通知中心"
        body = (
            '<div class="odf-panel-list">'
            '<div class="odf-panel-item"><strong>尚有缺件待補</strong><p class="odf-muted">建議先補齊社團評鑑核心文件。</p></div>'
            '<div class="odf-panel-item"><strong>檔案庫提醒</strong><p class="odf-muted">尚未歸檔的文件會集中顯示於檔案庫。</p></div>'
            '<div class="odf-panel-item"><strong>系統狀態</strong><p class="odf-muted">目前為本機 Streamlit 展示版，資料依本機資料庫顯示。</p></div>'
            '</div>'
        )
    else:
        title = "社團小幫手"
        state = _runtime_state()
        settings = state["settings"]
        body = (
            '<div class="odf-panel-list">'
            f'<div class="odf-panel-item"><strong>{_safe(settings.get("club_name", "ODFlow示範社團"))}</strong><p class="odf-muted">{_safe(settings.get("campus", "天母校區"))}｜{_safe(settings.get("academic_year", "114"))} 學年度</p></div>'
            f'<a class="odf-btn soft full" href="{nav_href("Settings")}">前往社團設定 →</a>'
            f'<a class="odf-btn outline full" href="{nav_href("Files")}">查看檔案庫 →</a>'
            '</div>'
        )
    return f'<div class="odf-panel-overlay"><aside class="odf-panel"><div class="odf-panel-head"><h2 class="odf-panel-title">{title}</h2><a class="odf-panel-close" href="{close_href}">×</a></div>{body}</aside></div>'


def _same_tab_links(html: str) -> str:
    # Only real anchor tags should receive target="_self".
    return re.sub(r'<a(?=\s|>)(?![^>]*\btarget=)', '<a target="_self"', html)


def page_shell(active: str, content: str) -> str:
    html = f'<div class="odf-shell">{_sidebar(active)}<main class="odf-main">{_topbar(active)}<div class="odf-content">{content}</div></main>{_panel(active)}</div>'
    return _same_tab_links(html)


def page_header(title: str, desc: str, eyebrow: str | None = None) -> str:
    eyebrow_html = f'<div class="odf-page-eyebrow">{_safe(eyebrow)}</div>' if eyebrow else ""
    return f'<div class="odf-page-header">{eyebrow_html}<h1 class="odf-page-title">{_safe(title)}</h1><p class="odf-page-desc">{_safe(desc)}</p></div>'


def eval_ring(percent: int, size: int = 132, accent: str = CORAL) -> str:
    pct = max(0, min(100, int(percent)))
    return f'<div class="odf-ring" style="--pct:{pct};--size:{size}px;--accent:{accent};"><div class="odf-ring-inner"><div class="odf-ring-value">{pct}%</div><div class="odf-ring-label">準備度</div></div></div>'


def stat_mini(icon: str, value: str, label: str, tone: str = "blue") -> str:
    return f'<div class="odf-stat-mini {tone}"><div class="stat-icon">{icon}</div><div><strong>{value}</strong><span>{label}</span></div></div>'


def action_card(title: str, desc: str, icon: str, button: str, href: str, tone: str) -> str:
    btn_cls = "primary" if tone == "blue" else tone
    return f'<section class="odf-card odf-action-card"><div class="odf-doc-icon {tone if tone != "blue" else ""}">{icon}</div><div><h3 class="odf-action-title">{title}</h3><p class="odf-action-desc">{desc}</p></div><a class="odf-btn {btn_cls} full" href="{href}">{button} <span>→</span></a></section>'


def template_row(name: str, fmt: str = "ODT", cat: str = "日常行政") -> str:
    tag_cls = "ods" if fmt == "ODS" else "odt"
    return f'<div class="odf-row-line"><span>▤</span><strong>{name}</strong><span class="odf-tag {tag_cls}">{fmt}</span><span class="odf-mini" style="text-align:right;">{cat}</span></div>'


def render_home() -> str:
    state = _runtime_state()
    settings = state["settings"]
    documents = state["documents"]
    templates = state["templates"]
    summary = state["summary"]
    counts = _status_counts(documents)
    missing_count = len(summary.get("missing_requirements") or [])
    pending_count = int(summary.get("draft_or_pending_documents") or counts["pending"])
    percent = int(summary.get("overall_completion_percentage") or 0)
    template_total = len(templates)
    odf_ratio = "100%" if template_total else "0%"
    completed_templates = max(0, template_total - 11) if template_total > 11 else template_total
    content = page_header("首頁", "快速完成社團文件下載、建立與評鑑管理", "ODFlow Workbench")
    content += '<div class="odf-home-row-top">'
    content += '<section class="odf-card odf-hero-card"><div class="odf-hero-illus"><div class="folder">📁</div><div class="odf-bubble">ODF</div></div><div><div class="odf-kicker">台灣學生社團 ODF 文件工作台</div><h2 class="odf-hero-title">一站式管理社團 ODF 文件與評鑑</h2><p class="odf-hero-desc">從空白範本、正式文件產出、版本管理到社團評鑑管理，ODFlow 讓社團文件更有效率，更有條理。</p><div class="odf-home-stat-grid">'
    content += stat_mini("▤", f"{template_total}", "官方範本") + stat_mini("👥", f"{len(documents)}", "目前文件") + stat_mini("⚡", f"{counts['done']}", "已完成", "green") + stat_mini("🛡", odf_ratio, "ODF 標準格式", "green")
    content += '</div></div></section>'
    content += '<section class="odf-card odf-eval-card"><div class="odf-eval-head"><h3 class="odf-eval-title">社團評鑑準備度</h3><span class="odf-mini">資料依目前文件更新</span></div><div class="odf-eval-layout">'
    content += eval_ring(percent)
    content += f'<div class="odf-eval-status-list"><div class="odf-tag red odf-eval-status"><span>⚠️ 缺件</span><strong>{missing_count} 份</strong></div><div class="odf-tag green odf-eval-status"><span>✅ 草稿 / 待審</span><strong>{pending_count} 份</strong></div><div class="odf-tag green odf-eval-status"><span>✅ 已完成</span><strong>{counts["done"]} 份</strong></div></div></div><p class="odf-eval-note">{"目前尚有缺件，建議先完成核心缺件。" if missing_count else "目前沒有缺件，可進一步檢查評鑑資料。"}</p><a class="odf-btn coral full" href="{nav_href("Evaluation")}">前往社團評鑑 <span>→</span></a></section></div>'
    content += '<h2 class="odf-row-title">快速開始</h2><div class="odf-home-row-action">'
    content += action_card("下載空白範本", "隨選所需 ODT / ODS 範本，快速開始撰寫文件。", "📄", "前往空白範本", nav_href("Templates"), "blue")
    content += action_card("建立正式文件", "結合內容生成與版本管理，產出標準正式文件。", "📝", "開始建立文件", nav_href("Generate"), "green")
    content += action_card("整理社團評鑑", "上傳與整理所需文件，快速準備社團評鑑資料。", "🛡", "前往社團評鑑", nav_href("Evaluation"), "purple")
    content += '</div>'
    content += '<div class="odf-home-row-bottom">'
    content += '<section class="odf-card odf-bottom-card"><div style="display:flex;justify-content:space-between;align-items:center;"><h3 class="odf-section-title">常用範本</h3><a class="odf-mini" href="' + nav_href("Templates") + '" style="text-decoration:none;color:#1d6bff;">查看全部</a></div>'
    if templates:
        for t in templates[:4]:
            content += template_row(_safe(t.get("name", "未命名範本")), _safe(t.get("suggested_format", "ODT")), _safe(t.get("library_category", "範本")))
    else:
        content += _empty_block("尚無範本資料", "目前沒有讀到範本 registry。")
    content += '</section>'
    content += '<section class="odf-card odf-bottom-card"><div style="display:flex;justify-content:space-between;align-items:center;"><h3 class="odf-section-title">檔案庫快捷入口</h3><a class="odf-mini" href="' + nav_href("Files") + '" style="text-decoration:none;color:#1d6bff;">查看全部</a></div><div class="odf-file-quick-grid"><div class="odf-file-quick-item"><div class="icon">📁</div><strong>' + str(len(documents)) + ' 份</strong><div class="odf-mini">我的文件</div></div><div class="odf-file-quick-item"><div class="icon">🕒</div><strong>' + str(counts["unfiled"]) + ' 份</strong><div class="odf-mini">未歸檔</div></div><div class="odf-file-quick-item"><div class="icon">☆</div><strong>' + str(counts["done"]) + ' 份</strong><div class="odf-mini">已完成</div></div></div><a class="odf-btn soft full" href="' + nav_href("Files") + '">前往檔案庫 <span>→</span></a></section>'
    content += f'<section class="odf-card odf-bottom-card"><div style="display:flex;justify-content:space-between;align-items:center;"><h3 class="odf-section-title">評鑑提醒</h3><a class="odf-mini" href="{nav_href("Evaluation")}" style="text-decoration:none;color:#64748b;">查看詳情</a></div><div style="display:grid;grid-template-columns:26px 1fr;gap:10px;align-items:start;"><span style="color:#f97316;font-size:22px;">♧</span><div><strong style="font-size:14px;">{"社團評鑑文件缺漏中" if missing_count else "社團評鑑狀態正常"}</strong><p class="odf-mini" style="margin:6px 0 10px 0;">目前尚有 {missing_count} 份必要文件缺漏。</p><div style="height:8px;background:#edf2f7;border-radius:999px;margin-bottom:12px;"><span style="display:block;height:8px;width:{percent}%;background:#ff5a7a;border-radius:999px;"></span></div><div style="display:flex;gap:8px;"><span class="odf-tag orange">缺漏 {missing_count} 份</span><span class="odf-tag green">待審 {pending_count} 份</span></div><a class="odf-mini" href="{nav_href("Evaluation")}" style="display:inline-block;margin-top:14px;color:#ef476f;text-decoration:none;font-weight:850;">前往社團評鑑 →</a></div></div></section>'
    content += '<section class="odf-card odf-bottom-card"><h3 class="odf-section-title">第一次使用建議</h3><div style="display:flex;flex-direction:column;gap:9px;color:#475569;font-size:13px;font-weight:650;line-height:1.35;"><div>✅ 先至空白範本下載空白範本，熟悉文件格式。</div><div>✅ 建立一份測試文件，體驗協同與管理流程。</div><div>✅ 上傳必要基礎文件，開啟評鑑準備。</div><div>✅ 完成文件檢核後，讓評鑑細節更順利。</div></div><a class="odf-mini" href="' + nav_href("Projects") + '" style="display:inline-block;margin-top:13px;color:#1d6bff;text-decoration:none;font-weight:850;">查看完整教學 →</a></section></div>'
    return page_shell("home", content)
def kpi(title: str, value: str, desc: str, icon: str, tone: str = "blue") -> str:
    return f'<section class="odf-card pad" style="height:124px;display:flex;align-items:center;gap:18px;"><div class="odf-doc-icon {tone}" style="width:60px;height:60px;border-radius:28px;font-size:26px;">{icon}</div><div><div class="odf-mini">{title}</div><div style="font-size:30px;font-weight:920;line-height:1.05;">{value}</div><div class="odf-mini" style="color:#16a34a;margin-top:6px;">↗ {desc}</div></div></section>'


def project_row(name: str, status: str, pct: int, tone: str = "blue") -> str:
    tag_tone = "blue" if tone == "blue" else "green" if tone == "green" else "orange" if tone == "orange" else "gray"
    return f'<div style="height:58px;display:grid;grid-template-columns:28px 1.45fr 90px 1fr 48px;gap:12px;align-items:center;border-bottom:1px solid #edf2f7;"><span>▤</span><strong style="font-size:14px;">{name}</strong><span class="odf-tag {tag_tone}">{status}</span><div class="odf-progress"><span style="width:{pct}%;"></span></div><strong style="font-size:14px;text-align:right;">{pct}%</strong></div>'


def template_card(name: str, fmt: str, desc: str, sheet: bool = False) -> str:
    tag = "ods" if fmt == "ODS" else "odt"
    sheet_cls = "sheet" if sheet else ""
    return f'<section class="odf-card odf-template-card"><div class="odf-template-thumb {sheet_cls}"></div><div style="min-width:0;"><h3 style="font-size:18px;margin:0 0 8px 0;line-height:1.25;">{name}</h3><span class="odf-tag {tag}">{fmt}</span><p class="odf-muted" style="font-size:13px;line-height:1.55;margin:10px 0 12px 0;">{desc}</p><div class="odf-template-actions"><a class="odf-btn outline" href="#">↓ 下載範本</a><a class="odf-btn soft" href="#">查看說明</a></div></div></section>'


def render_templates() -> str:
    state = _runtime_state()
    templates = state["templates"]
    active_cat = _first_query("cat", "全部範本")
    q = _first_query("q", "").strip()
    fmt_filter = _first_query("fmt_filter", "全部格式")
    usage_filter = _first_query("usage", "全部用途")
    category_map = {
        "全部範本": None,
        "日常行政": "日常行政型",
        "專案活動": "專案活動型",
        "財務核銷": "財務與清冊型",
        "評鑑資料": "評鑑資料",
    }
    fallback = [
        {"name": "會議紀錄", "suggested_format": "ODT", "usage_description": "記錄會議重點、決議事項與後續執行人員。", "library_category": "日常行政型"},
        {"name": "開會通知單", "suggested_format": "ODT", "usage_description": "通知會議時間、地點與議程事項。", "library_category": "日常行政型"},
        {"name": "簽到表", "suggested_format": "ODS", "usage_description": "活動或會議簽到紀錄，方便統計出席人數。", "library_category": "日常行政型"},
        {"name": "活動企劃書", "suggested_format": "ODT", "usage_description": "規劃活動目的、流程、預算與執行方式。", "library_category": "專案活動型"},
        {"name": "活動成果報告", "suggested_format": "ODT", "usage_description": "彙整活動成效、心得與照片紀錄。", "library_category": "專案活動型"},
        {"name": "經費核銷單", "suggested_format": "ODS", "usage_description": "填寫支出明細與附件，用於經費核銷。", "library_category": "財務與清冊型"},
        {"name": "借用申請單", "suggested_format": "ODT", "usage_description": "申請器材、場地或物品借用之正式文件。", "library_category": "日常行政型"},
        {"name": "場地復原確認表", "suggested_format": "ODT", "usage_description": "確認場地復原狀況與負責人簽名。", "library_category": "評鑑資料"},
    ]
    if not templates:
        templates = fallback

    def _matches(template: dict) -> bool:
        name = str(template.get("name", ""))
        desc = str(template.get("usage_description", ""))
        cat = str(template.get("library_category", ""))
        fmt = str(template.get("suggested_format", "ODT"))
        haystack = f"{name} {desc} {cat} {fmt}".lower()
        if q and q.lower() not in haystack:
            return False
        if active_cat != "全部範本":
            target = category_map.get(active_cat)
            if target and target not in cat and active_cat not in cat:
                return False
        if fmt_filter != "全部格式" and fmt != fmt_filter:
            return False
        if usage_filter != "全部用途":
            usage_target = category_map.get(usage_filter, usage_filter)
            if usage_target not in cat and usage_filter not in cat and usage_filter not in desc:
                return False
        return True

    filtered = [t for t in templates if _matches(t)]

    def _selected(value: str, current: str) -> str:
        return " selected" if value == current else ""

    content = page_header("空白範本中心", "瀏覽並下載官方 ODT / ODS 空白範本，快速建立標準化文件。")
    content += (
        f'<form class="odf-filter-form" method="get" action="/">'
        '<input type="hidden" name="page" value="Templates">'
        f'<input class="odf-filter-control" type="search" name="q" value="{_safe(q)}" placeholder="🔎　搜尋範本名稱、用途或關鍵字">'
        f'<select class="odf-filter-control" name="cat">'
        f'<option value="全部範本"{_selected("全部範本", active_cat)}>分類：全部</option>'
        f'<option value="日常行政"{_selected("日常行政", active_cat)}>日常行政</option>'
        f'<option value="專案活動"{_selected("專案活動", active_cat)}>專案活動</option>'
        f'<option value="財務核銷"{_selected("財務核銷", active_cat)}>財務核銷</option>'
        f'<option value="評鑑資料"{_selected("評鑑資料", active_cat)}>評鑑資料</option>'
        '</select>'
        f'<select class="odf-filter-control" name="fmt_filter">'
        f'<option value="全部格式"{_selected("全部格式", fmt_filter)}>格式：全部</option>'
        f'<option value="ODT"{_selected("ODT", fmt_filter)}>ODT</option>'
        f'<option value="ODS"{_selected("ODS", fmt_filter)}>ODS</option>'
        '</select>'
        f'<select class="odf-filter-control" name="usage">'
        f'<option value="全部用途"{_selected("全部用途", usage_filter)}>用途：全部</option>'
        f'<option value="日常行政"{_selected("日常行政", usage_filter)}>日常行政</option>'
        f'<option value="專案活動"{_selected("專案活動", usage_filter)}>專案活動</option>'
        f'<option value="財務核銷"{_selected("財務核銷", usage_filter)}>財務核銷</option>'
        f'<option value="評鑑資料"{_selected("評鑑資料", usage_filter)}>評鑑資料</option>'
        '</select>'
        '<button class="odf-filter-submit" type="submit">套用篩選</button>'
        '</form>'
    )
    content += '<div style="display:flex;justify-content:flex-end;margin:-6px 0 14px 0;"><a class="odf-mini" style="color:#1d6bff;text-decoration:none;font-weight:850;" href="' + nav_href("Templates") + '">清除篩選 ↻</a></div>'
    content += '<div class="odf-card" style="height:88px;display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr 1fr;margin-bottom:16px;overflow:visible;">'
    tabs = [
        ("📁", "全部範本", len(templates), "blue"),
        ("💼", "日常行政", sum("日常行政" in str(t.get("library_category","")) for t in templates), "orange"),
        ("🧩", "專案活動", sum("專案活動" in str(t.get("library_category","")) for t in templates), "green"),
        ("🧾", "財務核銷", sum(("財務" in str(t.get("library_category","")) or "清冊" in str(t.get("library_category",""))) for t in templates), "red"),
        ("📥", "評鑑資料", sum("評鑑" in str(t.get("library_category","")) for t in templates), "blue"),
    ]
    for icon, label, num, tone in tabs:
        border = "border-bottom:4px solid #1d6bff;" if label == active_cat else ""
        active_color = "#1d6bff" if label == active_cat else "#0f172a"
        content += f'<a href="{nav_href("Templates", cat=label, q=q, fmt_filter=fmt_filter, usage=usage_filter)}" style="display:flex;align-items:center;gap:16px;padding:0 24px;border-right:1px solid #e7edf4;{border}text-decoration:none;color:inherit;"><div class="odf-doc-icon {tone}" style="width:42px;height:42px;border-radius:14px;font-size:20px;">{icon}</div><strong style="font-size:17px;color:{active_color};">{label}</strong><span style="margin-left:auto;color:#1d6bff;font-weight:850;">{num}</span></a>'
    content += '</div><div class="odf-card" style="height:104px;background:linear-gradient(90deg,#eff6ff,#f8fbff);border-color:#cfe0ff;padding:20px 26px;display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;"><div><h3 style="margin:0 0 8px 0;color:#1d6bff;">先下載空白範本，再依格式填寫內容</h3><p class="odf-muted" style="margin:0;font-size:14px;">所有範本皆為官方標準格式，支援 ODT / ODS，可重複修改並重複使用。</p></div><div style="font-size:48px;color:#1d6bff;">⬇</div></div>'
    content += '<div class="odf-grid" style="grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;">'
    if filtered:
        for t in filtered[:12]:
            fmt = str(t.get("suggested_format", "ODT"))
            content += template_card(_safe(t.get("name", "未命名範本")), fmt, _safe(t.get("usage_description", "標準空白範本。")), fmt == "ODS")
    else:
        content += '<div class="odf-template-empty">' + _empty_block("沒有符合條件的範本", "請調整搜尋字詞、格式或用途條件。", "回到全部範本", nav_href("Templates")) + '</div>'
    content += '</div>'
    return page_shell("Templates", content)

def render_dashboard() -> str:
    state = _runtime_state()
    documents = state["documents"]
    summary = state["summary"]
    counts = _status_counts(documents)
    missing_count = len(summary.get("missing_requirements") or [])
    project_names = sorted({str(d.get("project_id") or d.get("project_name") or "") for d in documents if d.get("project_id") or d.get("project_name")})
    project_count = len(project_names)
    content = page_header("儀表板", "掌握社團工作進度、文件狀況與近期提醒。")
    content += '<div class="odf-grid" style="grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:18px;">' + kpi("目前專案", f"{project_count} 個", "依現有文件統計", "📁") + kpi("本週新增文件", f"{len(documents)} 份", "目前資料庫文件數", "▤", "green") + kpi("待補文件", f"{missing_count} 份", "依評鑑缺件統計", "⚠️", "orange") + kpi("未歸檔檔案", f"{counts['unfiled']} 份", "草稿或待確認文件", "🗃️", "purple") + '</div>'
    content += '<div class="odf-grid" style="grid-template-columns:1.1fr 1fr;gap:18px;margin-bottom:18px;"><section class="odf-card pad" style="min-height:318px;"><div style="display:flex;justify-content:space-between;align-items:center;"><h3 class="odf-section-title">專案進度總覽</h3><span class="odf-chip">目前資料</span></div>'
    if project_count:
        for idx, name in enumerate(project_names[:4]):
            pct = min(100, 25 + idx * 15)
            content += project_row(name or f"專案 {idx+1}", "進行中", pct, "blue")
        content += '<a href="' + nav_href("Projects") + '" class="odf-btn soft full" style="margin-top:16px;">查看全部專案 →</a>'
    else:
        content += _empty_block("目前尚無專案", "建立文件並歸入專案後，這裡會顯示進度。", "建立文件", nav_href("Generate"))
    content += '</section>'
    content += '<section class="odf-card pad" style="min-height:318px;"><div style="display:flex;justify-content:space-between;align-items:center;"><h3 class="odf-section-title">缺件 / 待補清單</h3><a class="odf-mini" href="' + nav_href("Evaluation") + '" style="color:#1d6bff;text-decoration:none;">查看全部</a></div><div class="odf-grid" style="grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px;">'
    for label, num, color in [("核心文件缺", str(missing_count), "red"), ("待審", str(counts["pending"]), "orange"), ("草稿", str(counts["draft"]), "orange"), ("已完成", str(counts["done"]), "blue")]:
        content += f'<div class="odf-card" style="padding:12px;text-align:left;"><span class="odf-tag {color}" style="width:10px;height:10px;padding:0;"></span><div class="odf-mini" style="margin-top:8px;">{label}</div><strong style="font-size:21px;">{num} 份</strong></div>'
    content += '</div>'
    missing = summary.get("missing_requirements") or []
    if missing:
        content += '<div class="odf-mini" style="font-weight:850;color:#0f172a;margin-bottom:8px;">最緊急待補文件</div>'
        for item in missing[:3]:
            name = _safe(item.get("requirement_name") if isinstance(item, dict) else item)
            content += f'<div style="height:48px;display:grid;grid-template-columns:24px 1fr 90px;align-items:center;border-bottom:1px solid #edf2f7;"><span style="color:#ef4444;">ⓘ</span><div><strong style="font-size:13px;">{name}</strong><div class="odf-mini">社團評鑑</div></div><span style="color:#ef4444;font-size:12px;font-weight:850;text-align:right;">待補</span></div>'
        content += '<a class="odf-btn soft full" style="margin-top:12px;" href="' + nav_href("Evaluation") + '">查看完整待補清單 →</a>'
    else:
        content += _empty_block("目前沒有缺件", "評鑑必要文件未偵測到缺漏，或尚未建立文件資料。", "前往社團評鑑", nav_href("Evaluation"))
    content += '</section></div>'
    content += '<div class="odf-grid" style="grid-template-columns:1.15fr .95fr .78fr;gap:18px;"><section class="odf-card pad" style="min-height:300px;"><div style="display:flex;justify-content:space-between;"><h3 class="odf-section-title">最近文件</h3><a class="odf-mini" href="' + nav_href("Files") + '" style="color:#1d6bff;text-decoration:none;">查看全部</a></div>'
    if documents:
        content += '<table class="odf-table"><tr><th>文件名稱</th><th>類型</th><th>狀態</th><th>更新時間</th></tr>'
        for d in documents[:4]:
            status = _doc_status(d)
            tone = "green" if status in {"已完成","正式版","已歸檔"} else "orange" if status in {"待確認","待審"} else "blue"
            content += f'<tr><td>▤ {_doc_title(d)}</td><td>{_doc_type(d)}</td><td><span class="odf-tag {tone}">{status}</span></td><td>{_doc_updated(d)}</td></tr>'
        content += '</table>'
    else:
        content += _empty_block("目前尚無文件", "建立第一份文件後，最近文件會顯示在這裡。", "建立文件", nav_href("Generate"))
    content += '</section><section class="odf-card pad" style="min-height:300px;"><div style="display:flex;justify-content:space-between;"><h3 class="odf-section-title">工作提醒</h3><a class="odf-mini" href="' + nav_href("Evaluation") + '" style="color:#1d6bff;text-decoration:none;">查看全部</a></div>'
    if missing_count:
        for item in (summary.get("missing_requirements") or [])[:4]:
            name = _safe(item.get("requirement_name") if isinstance(item, dict) else item)
            content += f'<div style="height:56px;display:grid;grid-template-columns:24px 1fr 86px;align-items:center;border-bottom:1px solid #edf2f7;"><span>🟠</span><div><strong style="font-size:13px;">{name}</strong><div class="odf-mini">社團評鑑</div></div><span style="color:#ef4444;font-size:12px;font-weight:850;text-align:right;">待補</span></div>'
    else:
        content += _empty_block("目前沒有工作提醒", "當有缺件、待審或未歸檔文件時，會出現在這裡。")
    content += '</section><section style="display:grid;gap:14px;grid-template-rows:1.4fr 1fr;"><div class="odf-card pad"><h3 class="odf-section-title">快捷操作</h3><div style="display:grid;gap:8px;">'
    for label, href, icon in [("下載範本", nav_href("Templates"), "📄"), ("建立文件", nav_href("Generate"), "▤"), ("查看檔案庫", nav_href("Files"), "🗂️"), ("社團設定", nav_href("Settings"), "⚙️")]:
        content += f'<a href="{href}" class="odf-btn outline full" style="height:38px;justify-content:space-between;"><span>{icon} {label}</span><span>›</span></a>'
    content += f'</div></div><div class="odf-card pad" style="background:#f0fdf4;"><h3 class="odf-section-title" style="margin-bottom:8px;">本週摘要</h3><div style="display:flex;gap:14px;align-items:center;"><div style="font-size:44px;color:#16a34a;">✓</div><div><strong style="color:#16a34a;">目前資料庫共有 {len(documents)} 份文件</strong><div class="odf-mini">草稿 {counts["draft"]} 份、待確認 {counts["pending"]} 份、已完成 {counts["done"]} 份。</div></div></div></div></section></div>'
    return page_shell("Dashboard", content)
def stepper(step: int) -> str:
    labels = ["選擇範本", "填寫資料", "預覽確認", "下載文件"]
    html = '<div class="odf-stepper">'
    for i, label in enumerate(labels, start=1):
        cls = "done" if i < step else "active" if i == step else ""
        badge = "✓" if i < step else str(i)
        html += f'<div class="odf-step {cls}"><span class="odf-step-badge">{badge}</span><span class="odf-step-label">{label}</span></div>'
    return html + '</div>'

def selected_template_card(fmt: str = "ODT", title: str = "活動企劃書") -> str:
    sheet_cls = "sheet" if fmt == "ODS" else ""
    tag = "ods" if fmt == "ODS" else "odt"
    return f'<section class="odf-card pad" style="min-height:100%;"><h3 class="odf-section-title">已選擇範本</h3><div class="odf-template-thumb {sheet_cls}" style="width:154px;height:204px;margin:0 auto 18px auto;"></div><h3 style="font-size:20px;margin:0 0 8px 0;">{title}</h3><span class="odf-tag {tag}">{fmt}</span><p class="odf-muted" style="font-size:14px;line-height:1.65;">規劃活動目的、流程、預算與執行方式。</p><a class="odf-btn outline full" href="/?page=Generate&step=1">↻ 更換範本</a></section>'


def generate_step1() -> str:
    content = page_header("生成文件", "選擇範本並填寫資料，快速建立正式文件。") + stepper(1)
    content += '<div class="odf-generate-shell">' + selected_template_card("ODT", "活動企劃書").replace("更換範本", "清除選擇")
    content += '<section class="odf-card pad odf-generate-main-card"><div class="odf-grid" style="grid-template-columns:1.4fr .7fr .7fr .7fr;gap:14px;margin-bottom:20px;"><div class="odf-input">🔎　搜尋範本名稱或關鍵字</div><div class="odf-input">全部分類⌄</div><div class="odf-input">全部格式⌄</div><div class="odf-input">全部用途⌄</div></div><div class="odf-grid" style="grid-template-columns:repeat(3,1fr);gap:16px;">'
    for name, fmt, sheet in [("會議紀錄", "ODT", False), ("開會通知單", "ODT", False), ("簽到表", "ODS", True), ("活動企劃書", "ODT", False), ("活動成果報告", "ODT", False), ("借用申請單", "ODT", False)]:
        href = f"/Generate?step=2&fmt={fmt.lower()}&template={name}"
        active = 'border-color:#1d6bff;box-shadow:0 0 0 2px rgba(29,107,255,.12);' if name == "活動企劃書" else ""
        sheet_cls = "sheet" if sheet else ""
        tag = "ods" if fmt == "ODS" else "odt"
        button = "✓ 已選擇" if name == "活動企劃書" else "選擇範本"
        content += f'<div class="odf-card odf-generate-template-card" style="{active}"><div class="odf-template-thumb {sheet_cls}" style="width:78px;height:104px;"></div><div style="min-width:0;"><h3 style="font-size:17px;margin:0 0 8px 0;line-height:1.25;">{name}</h3><span class="odf-tag {tag}">{fmt}</span><p class="odf-muted" style="font-size:13px;line-height:1.45;margin:10px 0 8px 0;">適合社團日常文件建立與歸檔。</p><a class="odf-btn outline full" href="{href}">{button}</a></div></div>'
    content += '</div><div style="display:flex;justify-content:flex-end;gap:14px;margin-top:24px;"><a class="odf-btn outline" href="/">上一步</a><a class="odf-btn primary" href="/?page=Generate&step=2&fmt=odt&template=活動企劃書">下一步</a></div></section></div>'
    return content


def generate_step2(fmt: str = "ODT", template: str = "活動企劃書") -> str:
    content = page_header("生成文件", "選擇範本並填寫資料，快速建立正式文件。") + stepper(2)
    content += '<div class="odf-generate-shell">' + selected_template_card(fmt, template)
    content += '<section class="odf-card" style="padding:24px 28px;"><h3 class="odf-section-title" style="border-left:4px solid #1d6bff;padding-left:12px;">基本資料</h3><div class="odf-grid" style="grid-template-columns:repeat(2,1fr);gap:15px 24px;">'
    fields = [("社團名稱 *", "資訊研習社"), ("活動名稱 *", "ODFlow 工作坊"), ("活動日期 *", "2026/07/20"), ("活動地點 *", "綜合大樓 3 樓會議室"), ("活動性質 *", "研習活動"), ("聯絡人 *", "王小明"), ("聯絡電話 *", "0912-345-678"), ("電子信箱 *", "example@example.com")]
    for label, value in fields:
        content += f'<div class="odf-field"><label>{label}</label><div class="odf-input">{value}</div></div>'
    content += '<div class="odf-field" style="grid-column:1/3;"><label>活動說明 *</label><div class="odf-input odf-textarea">舉辦 ODFlow 文件製作與管理的實作工作坊，提升社團成員數位技能與文件規劃能力。</div></div></div><div style="border-top:1px solid #e7edf4;margin:18px -28px 0 -28px;padding:18px 28px 0 28px;"><h3 class="odf-section-title" style="border-left:4px solid #1d6bff;padding-left:12px;">進階設定 <span class="odf-muted" style="font-size:15px;">（選填）</span></h3><div class="odf-grid" style="grid-template-columns:repeat(3,1fr);gap:16px 24px;"><div class="odf-field"><label>指導老師</label><div class="odf-input">李老師⌄</div></div><div class="odf-field"><label>預算金額</label><div class="odf-input">3000　元</div></div><div class="odf-field"><label>備註</label><div class="odf-input">適合新手參與，備有電腦設備。</div></div></div></div>'
    content += f'<div style="display:flex;justify-content:flex-end;gap:14px;margin-top:24px;"><a class="odf-btn outline" href="/?page=Generate&step=1">上一步</a><a class="odf-btn primary" href="/?page=Generate&step=3&fmt={fmt.lower()}&template={template}">下一步</a></div></section></div>'
    return content


def generate_step3(fmt: str = "ODT", template: str = "活動企劃書") -> str:
    content = page_header("生成文件", "選擇範本並填寫資料，快速建立正式文件。") + stepper(3)
    content += '<div class="odf-generate-shell"><section class="odf-card pad"><h3 class="odf-section-title">文件摘要</h3><div class="odf-template-thumb" style="width:160px;height:214px;margin:0 auto 18px auto;"></div><h3 style="font-size:20px;margin:0 0 8px 0;">' + template + f'</h3><span class="odf-tag {"ods" if fmt=="ODS" else "odt"}">{fmt}</span><div style="display:grid;gap:13px;margin-top:18px;"><div>✅ 基本資料已填寫</div><div>✅ 欄位驗證完成</div><div>✅ 可進行預覽</div></div></section>'
    content += '<section class="odf-card pad"><h3 class="odf-section-title">預覽確認</h3><div style="height:430px;background:#f8fafc;border:1px solid #dbe7f4;border-radius:14px;display:grid;grid-template-columns:1fr 230px;gap:28px;align-items:center;padding:28px;"><div style="width:390px;height:410px;background:#fff;border:1px solid #dbe7f4;margin:0 auto;box-shadow:0 12px 24px rgba(15,23,42,.08);padding:28px;font-size:12px;"><h2 style="text-align:center;margin:0 0 20px 0;">' + template + '</h2><table style="width:100%;border-collapse:collapse;">' + "".join(f'<tr><td style="border:1px solid #dbe7f4;padding:7px;">{k}</td><td style="border:1px solid #dbe7f4;padding:7px;">{v}</td></tr>' for k, v in [("社團名稱", "資訊研習社"), ("活動名稱", "ODFlow 工作坊"), ("活動日期", "2026/07/20"), ("活動地點", "綜合大樓 3 樓會議室"), ("活動性質", "研習活動")]) + '</table><p style="line-height:1.8;">活動內容與預期效益文字預覽區。</p></div><div class="odf-card pad" style="box-shadow:none;"><h3 class="odf-section-title">預覽狀態</h3><div style="display:grid;gap:18px;"><div>✅ 必填欄位完整</div><div>✅ 版面正常</div><div>✅ 可產生正式文件</div></div></div></div><div style="display:flex;justify-content:flex-end;gap:14px;margin-top:22px;"><a class="odf-btn outline" href="/?page=Generate&step=2&fmt=' + fmt.lower() + '&template=' + template + '">上一步</a><a class="odf-btn primary" href="/?page=Generate&step=4&fmt=' + fmt.lower() + '&template=' + template + '">確認並產生文件</a></div></section></div>'
    return content


def generate_step4(fmt: str = "ODT", template: str = "活動企劃書") -> str:
    native = "ODS" if fmt == "ODS" else "ODT"
    tag = "ods" if native == "ODS" else "odt"
    sheet_cls = "sheet" if native == "ODS" else ""
    size_text = "ODS 96 KB　｜　PDF 210 KB" if native == "ODS" else "ODT 128 KB　｜　PDF 284 KB"
    content = page_header("生成文件", "選擇範本並填寫資料，快速建立正式文件。") + stepper(4)
    content += '<div class="odf-grid" style="grid-template-columns:360px 1fr;gap:24px;min-height:520px;"><section class="odf-card pad"><h3 class="odf-section-title">產出結果摘要</h3><div style="display:grid;grid-template-columns:140px 1fr;gap:20px;align-items:start;"><div class="odf-template-thumb ' + sheet_cls + '" style="width:130px;height:174px;"></div><div><h3 style="font-size:20px;margin:0 0 20px 0;">' + template + '</h3><div class="odf-mini">產生時間</div><div style="margin:6px 0 18px 0;">📅 2026/07/20 14:36</div><div class="odf-mini">檔案狀態</div><span class="odf-tag green" style="margin-top:8px;">✅ 產出完成</span></div></div><div style="margin-top:22px;"><div class="odf-mini">檔案格式</div><div style="display:flex;gap:8px;margin:8px 0 18px 0;"><span class="odf-tag ' + tag + '">' + native + '</span><span class="odf-tag red">PDF</span><span class="odf-tag green">已存入檔案庫</span></div><div class="odf-mini">檔案大小</div><div style="margin-top:8px;color:#475569;font-weight:650;">' + size_text + '</div></div></section>'
    content += '<section class="odf-card pad"><div style="display:flex;gap:30px;align-items:center;border-bottom:1px solid #e7edf4;padding-bottom:28px;margin-bottom:24px;"><div style="width:92px;height:92px;border-radius:999px;background:#dcfce7;color:#16a34a;display:flex;align-items:center;justify-content:center;font-size:50px;">✓</div><div><h2 style="font-size:32px;line-height:1.25;margin:0 0 12px 0;">文件已建立完成</h2><p class="odf-muted" style="font-size:15px;margin:0;">感謝使用 ODFlow！您的文件已成功產出並存入檔案庫，您可以立即下載或前往檔案庫查看與管理。</p></div></div><h3 class="odf-section-title">下載您的文件</h3><div class="odf-grid" style="grid-template-columns:repeat(3,1fr);gap:16px;">'
    for label, desc, icon, cls in [(f"下載 {native}", "可編輯的開放文件格式", native, tag), ("下載 PDF", "適合列印的可攜式文件格式", "PDF", "red"), ("前往檔案庫", "查看檔案與更多操作", "📁", "blue")]:
        href = "/Files" if label == "前往檔案庫" else "#"
        action = "前往檔案庫 →" if label == "前往檔案庫" else f"↓ {label}"
        content += f'<div class="odf-card" style="height:168px;padding:20px;"><div style="display:flex;gap:14px;align-items:center;margin-bottom:20px;"><div class="odf-doc-icon {cls}" style="width:54px;height:54px;border-radius:14px;font-size:18px;">{icon}</div><div><h3 style="font-size:18px;margin:0 0 4px 0;">{label}</h3><div class="odf-mini">{desc}</div></div></div><a class="odf-btn outline full" href="{href}">{action}</a></div>'
    content += '</div></section></div><div style="display:flex;justify-content:flex-end;gap:18px;margin-top:24px;"><a class="odf-btn outline" href="/?page=Generate&step=1">建立另一份</a><a class="odf-btn primary" href="/">完成</a></div>'
    return content


def render_generate(step: int = 1, fmt: str = "odt", template: str = "活動企劃書") -> str:
    fmt_upper = "ODS" if fmt.lower() == "ods" else "ODT"
    if step == 2:
        content = generate_step2(fmt_upper, template)
    elif step == 3:
        content = generate_step3(fmt_upper, template)
    elif step == 4:
        content = generate_step4(fmt_upper, template)
    else:
        content = generate_step1()
    return page_shell("Generate", content)


def render_files() -> str:
    state = _runtime_state()
    documents = state["documents"]
    counts = _status_counts(documents)
    content = page_header("檔案庫", "集中管理已建立文件、版本與下載紀錄。")
    content += '<div class="odf-grid" style="grid-template-columns:1.7fr .75fr .65fr .75fr 102px 120px;gap:14px;margin-bottom:16px;"><div class="odf-input">🔎　搜尋文件名稱、專案或關鍵字</div><div class="odf-input">文件類型：全部⌄</div><div class="odf-input">狀態：全部⌄</div><div class="odf-input">專案：全部⌄</div><div class="odf-input" style="justify-content:center;">☰　▦</div><a class="odf-btn primary" href="' + nav_href("Generate") + '">＋ 建立文件</a></div>'
    content += '<div class="odf-grid" style="grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:18px;">' + kpi("共用文件", str(len(documents)), "全部文件總數", "▤") + kpi("草稿", str(counts["draft"]), "待整理文件", "🧾", "gray") + kpi("待確認", str(counts["pending"]), "需要檢查", "🕒", "orange") + kpi("已完成", str(counts["done"]), "可直接下載", "✅", "green") + '</div>'
    content += '<div class="odf-grid" style="grid-template-columns:250px 1fr;gap:20px;"><aside class="odf-card pad" style="min-height:520px;"><div class="odf-row-line" style="grid-template-columns:24px 1fr 36px;background:#eaf2ff;border-radius:10px;border:none;padding:0 12px;margin-bottom:8px;"><span>📁</span><strong>全部文件</strong><span>' + str(len(documents)) + '</span></div>'
    filters = [("我建立的", len(documents), "▤"), ("與我共享", 0, "👥"), ("草稿", counts["draft"], "🧾"), ("待確認", counts["pending"], "🕒"), ("已完成", counts["done"], "✅"), ("最近使用", len(documents[:5]), "🕘")]
    for label, num, icon in filters:
        content += f'<div class="odf-row-line" style="grid-template-columns:24px 1fr 36px;"><span>{icon}</span><strong>{label}</strong><span>{num}</span></div>'
    content += '<div style="height:1px;background:#e7edf4;margin:16px 0;"></div><div class="odf-mini" style="font-weight:900;color:#334155;margin-bottom:8px;">專案分類　＋</div>'
    project_names = sorted({str(d.get("project_id") or d.get("project_name") or "未分類") for d in documents})
    if project_names:
        for label in project_names[:4]:
            num = sum(1 for d in documents if str(d.get("project_id") or d.get("project_name") or "未分類") == label)
            content += f'<div class="odf-row-line" style="grid-template-columns:24px 1fr 36px;"><span>📁</span><strong>{_safe(label)}</strong><span>{num}</span></div>'
    else:
        content += '<div class="odf-mini">尚無專案分類</div>'
    content += '</aside><section class="odf-card" style="min-height:520px;padding:0 0 18px 0;">'
    if documents:
        content += '<table class="odf-table"><tr><th style="padding-left:26px;">文件名稱 ↑</th><th>類型</th><th>專案</th><th>狀態</th><th>更新時間 ↓</th><th>版本 / 下載 / 操作</th></tr>'
        for d in documents[:8]:
            fmt = "ODS" if "表" in _doc_type(d) or "清冊" in _doc_type(d) else "ODT"
            tag = "ods" if fmt == "ODS" else "odt"
            status = _doc_status(d)
            tone = "green" if status in {"已完成","正式版","已歸檔"} else "orange" if status in {"待確認","待審"} else "blue"
            proj = _safe(d.get("project_id") or d.get("project_name") or "未分類")
            content += f'<tr><td style="padding-left:26px;">▤　{_doc_title(d)}</td><td><span class="odf-tag {tag}">{fmt}</span></td><td>{proj}</td><td><span class="odf-tag {tone}">{status}</span></td><td>{_doc_updated(d)}</td><td>👁　↓　↺　⋮</td></tr>'
        content += '</table><div style="display:flex;justify-content:center;gap:10px;margin-top:16px;"><a class="odf-btn outline" style="height:36px;width:42px;padding:0;" href="#">‹</a><a class="odf-btn primary" style="height:36px;width:42px;padding:0;" href="#">1</a><a class="odf-btn outline" style="height:36px;width:42px;padding:0;" href="#">›</a></div>'
    else:
        content += '<div style="padding:36px;">' + _empty_block("目前尚無文件", "從生成文件建立第一份文件後，這裡會顯示檔案列表、狀態與版本操作。", "建立文件", nav_href("Generate")) + '</div>'
    content += '</section></div>'
    return page_shell("Files", content)



def render_settings() -> str:
    state = _runtime_state()
    settings = state["settings"]
    documents = state["documents"]
    counts = _status_counts(documents)
    section = _first_query("section", "club")
    allowed = {"club", "members", "documents", "notifications", "data", "system"}
    if section not in allowed:
        section = "club"

    club_name = _safe(settings.get("club_name", "ODFlow示範社團"))
    academic_year = _safe(settings.get("academic_year", "114"))
    campus = _safe(settings.get("campus", "天母校區"))

    sections = {
        "club": ("🏫", "社團與帳號", "管理目前操作的社團、年度、校區與基本資料。"),
        "members": ("👥", "成員與權限", "管理幹部成員、文件可編輯權限與下載權限。"),
        "documents": ("📄", "文件與輸出", "設定文件命名、歸檔規則、輸出格式與檔案庫分類。"),
        "notifications": ("🔔", "通知", "設定缺件、待確認與最近文件提醒。"),
        "data": ("💾", "資料與備份", "匯出文件、備份資料與查看儲存位置。"),
        "system": ("🛠️", "系統資訊", "查看 ODFlow 版本、支援格式、環境與服務狀態。"),
    }

    def nav_item(key: str) -> str:
        icon, label, _ = sections[key]
        cls = " active" if key == section else ""
        return f'<a class="odf-settings-nav-item{cls}" href="{nav_href("Settings", section=key)}"><span>{icon}</span><span>{label}</span></a>'

    def row(title: str, desc: str, value: str, action: str = "設定", tone: str = "default") -> str:
        value_html = f'<span class="odf-tag blue">{value}</span>' if tone == "pill" else _safe(value)
        return (
            '<div class="odf-setting-row">'
            f'<div class="odf-setting-main"><strong>{_safe(title)}</strong><span>{_safe(desc)}</span></div>'
            f'<div class="odf-setting-value">{value_html}</div>'
            f'<a class="odf-setting-action" href="#">{_safe(action)}</a>'
            '</div>'
        )

    section_icon, section_title, section_desc = sections[section]
    content = page_header("社團設定", "管理社團資料、成員權限、文件輸出與資料備份。")
    content += '<div class="odf-settings-layout">'
    content += '<aside class="odf-card odf-settings-nav"><div class="odf-settings-nav-title">Settings</div>'
    for key in ["club", "members", "documents", "notifications", "data", "system"]:
        content += nav_item(key)
    content += '</aside>'
    content += '<main class="odf-settings-content">'
    content += f'<div class="odf-settings-section-head"><h2>{section_icon} {section_title}</h2><p>{section_desc}</p></div>'

    if section == "club":
        content += '<section class="odf-card odf-settings-card">'
        content += row("社團名稱", "顯示於首頁、檔案庫與文件輸出資訊。", club_name, "編輯")
        content += row("學年度", "影響評鑑年度、文件歸檔與首頁社團資訊。", f"{academic_year} 學年度", "變更")
        content += row("校區", "目前社團所在校區，顯示於側邊欄與社團卡。", campus, "變更")
        content += row("社團類型", "例如學術性、服務性、康樂性、自治性社團。", settings.get("club_type") or "尚未設定", "設定")
        content += row("負責人", "主要管理 ODFlow 工作台的人員。", settings.get("president_name") or "尚未設定", "新增")
        content += row("指導老師", "可用於活動文件、評鑑文件與核章資訊。", settings.get("advisor_name") or "尚未設定", "新增")
        content += '</section>'
    elif section == "members":
        content += '<section class="odf-card odf-settings-card">'
        content += row("管理員", "可調整社團資料、建立文件與管理檔案庫。", "1 人", "管理")
        content += row("幹部成員", "可協助建立文件與整理評鑑資料的人員。", "尚未設定", "新增")
        content += row("可編輯文件的人", "控制誰可以建立、修改與儲存草稿。", "只有管理員", "設定")
        content += row("可下載檔案的人", "控制誰可以下載 ODT / ODS / PDF。", "所有幹部", "設定")
        content += row("權限狀態", "目前為本機展示權限，尚未接入正式登入。", "展示模式", "查看")
        content += '</section>'
    elif section == "documents":
        example = f"{club_name}_活動企劃書_20260720.odt"
        content += '<section class="odf-card odf-settings-card">'
        content += row("文件命名規則", "設定生成文件時的預設檔名格式，適合配合學校規範。", "社團名稱_文件類型_日期", "設定")
        content += row("命名範例", "依照目前社團與日期產生的範例檔名。", example, "查看")
        content += row("歸檔規則", "生成文件完成後是否自動加入檔案庫。", "生成後自動歸檔", "設定")
        content += row("預設輸出格式", "ODT / ODS 原始檔保留，PDF 作為提交與列印格式。", "原始檔 + PDF", "查看")
        content += row("PDF 匯出", "控制是否顯示 PDF 預覽與下載入口。", "啟用", "設定")
        content += row("檔案庫分類方式", "決定文件列表依文件類型、專案或狀態分類。", "文件類型與專案", "設定")
        content += '</section>'
    elif section == "notifications":
        pending_total = counts["pending"] + counts["draft"]
        content += '<section class="odf-card odf-settings-card">'
        content += row("缺件提醒", "當社團評鑑必要文件缺漏時，在首頁與通知中心提醒。", "開啟", "切換", "pill")
        content += row("文件待確認提醒", "有草稿或待確認文件時顯示提醒。", "開啟", "切換", "pill")
        content += row("最近文件提醒", "顯示最近使用與最近修改的文件。", "開啟", "切換", "pill")
        content += row("通知中心", "目前通知顯示於右上角鈴鐺。", f"目前 {pending_total} 項", "查看")
        content += '</section>'
    elif section == "data":
        content += '<section class="odf-card odf-settings-card">'
        content += row("匯出全部文件", "下載目前社團所有 ODT / ODS / PDF 文件。", f"{len(documents)} 份文件", "匯出")
        content += row("匯出檔案庫清單", "下載文件清單 CSV / ODS，方便交接或備份。", "CSV / ODS", "匯出")
        content += row("資料儲存位置", "目前使用本機 SQLite 儲存展示資料。", "本機 SQLite", "查看")
        content += row("備份狀態", "目前尚未啟用雲端備份。", "未啟用", "了解")
        content += row("清除展示資料", "移除本機測試資料，保留系統與範本。", "危險操作", "清除")
        content += '</section>'
    else:
        content += '<section class="odf-card odf-settings-card">'
        content += row("ODFlow 版本", "目前介面與文件流程版本。", "v0.5 UIUX", "查看")
        content += row("支援格式", "平台目前支援的文件格式。", "ODT / ODS / PDF", "查看")
        content += row("目前環境", "現在執行環境。", "本機 Streamlit", "查看")
        content += row("服務狀態", "檢查文件服務、範本服務與檔案庫狀態。", "正常", "重新檢查", "pill")
        content += row("GitHub Repository", "專案原始碼與版本管理位置。", "SA_ODFlow", "開啟")
        content += '</section>'

    content += '<div class="odf-settings-note">這一頁先完成設定中心的 UI 與資訊架構。實際編輯、切換權限、匯出與清除資料，可以在下一階段接上 Streamlit form 與後端 service。</div>'
    content += '</main></div>'
    return page_shell("Settings", content)

def render_placeholder(active: str, title: str, desc: str) -> str:
    content = page_header(title, desc)
    content += '<section class="odf-card pad" style="min-height:420px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div style="font-size:64px;margin-bottom:16px;">🛠️</div><h2 style="font-size:28px;margin:0 0 12px 0;">頁面整理中</h2><p class="odf-muted">此頁沿用同一套像素版 sidebar / topbar / card 視覺規則。</p><a class="odf-btn soft" style="margin-top:16px;" href="' + nav_href("Settings") + '">前往社團設定 →</a></div></section>'
    return page_shell(active, content)


def render_exact_page(html: str) -> None:
    inject_exact_styles()
    st.markdown(html, unsafe_allow_html=True)
