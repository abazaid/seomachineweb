import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[3]
CONTEXT_DIR = ROOT / "context"


def _load_env() -> None:
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / "data_sources" / "config" / ".env")


def _normalize_credentials_paths() -> None:
    """
    Normalize GA4/GSC credentials paths to absolute paths relative to project root.
    Prevents failures when backend runs from a different working directory.
    """
    for key in ("GA4_CREDENTIALS_PATH", "GSC_CREDENTIALS_PATH"):
        raw = os.getenv(key)
        if not raw:
            continue
        p = Path(raw)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        os.environ[key] = str(p)


def _read_context_summary() -> List[Dict[str, Any]]:
    summary: List[Dict[str, Any]] = []
    if not CONTEXT_DIR.exists():
        return summary

    for p in sorted(CONTEXT_DIR.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
            summary.append({"file": p.name, "lines": len(text.splitlines())})
        except Exception:
            continue
    return summary


def _match_topic_keywords(topic: str, rows: List[Dict[str, Any]], limit: int = 15) -> List[Dict[str, Any]]:
    terms = [t for t in topic.strip().split() if t]
    if not terms:
        return []

    matched = []
    for row in rows:
        q = row.get("keyword", "")
        if any(t in q for t in terms):
            matched.append(row)
    matched.sort(key=lambda x: x.get("impressions", 0), reverse=True)
    return matched[:limit]


def generate_research_brief(keyword: str, title: str | None = None) -> str:
    """
    Generate a practical research brief from live providers + context files.
    This replaces placeholder text in the web platform with real data snapshots.
    """
    _load_env()
    _normalize_credentials_paths()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    blog_path = os.getenv("BLOG_PATH", "/blog/")
    location_code = int(os.getenv("DATAFORSEO_LOCATION_CODE", "2682"))
    language_code = os.getenv("DATAFORSEO_LANGUAGE_CODE", "ar")

    source_status: Dict[str, str] = {"dataforseo": "not_run", "gsc": "not_run", "ga4": "not_run"}
    context_summary = _read_context_summary()

    serp: Dict[str, Any] = {}
    ideas: List[Dict[str, Any]] = []
    questions: List[Dict[str, Any]] = []
    gsc_keywords: List[Dict[str, Any]] = []
    ga_top_pages: List[Dict[str, Any]] = []

    try:
        from data_sources.modules.dataforseo import DataForSEO

        dfs = DataForSEO()
        serp = dfs.get_serp_data(keyword, location_code=location_code, language_code=language_code, limit=10)
        ideas = dfs.get_keyword_ideas(keyword, location_code=location_code, limit=20)
        questions = dfs.get_questions(keyword, location_code=location_code, limit=20)
        source_status["dataforseo"] = "ok"
    except Exception as exc:
        source_status["dataforseo"] = f"fail: {exc}"

    try:
        from data_sources.modules.google_search_console import GoogleSearchConsole

        gsc = GoogleSearchConsole()
        all_keywords = gsc.get_keyword_positions(days=30, limit=500)
        gsc_keywords = _match_topic_keywords(keyword, all_keywords)
        source_status["gsc"] = "ok"
    except Exception as exc:
        source_status["gsc"] = f"fail: {exc}"

    try:
        from data_sources.modules.google_analytics import GoogleAnalytics

        ga = GoogleAnalytics()
        ga_top_pages = ga.get_top_pages(days=30, limit=10, path_filter=blog_path)
        source_status["ga4"] = "ok"
    except Exception as exc:
        source_status["ga4"] = f"fail: {exc}"

    top_domains: Dict[str, int] = {}
    for item in (serp.get("organic_results") or [])[:10]:
        domain = (item.get("domain") or "").lower()
        if domain:
            top_domains[domain] = top_domains.get(domain, 0) + 1

    lines: List[str] = []
    lines.append(f"# Research Brief: {title or keyword}")
    lines.append("")
    lines.append(f"- Generated at: {now}")
    lines.append(f"- Topic: {keyword}")
    lines.append(f"- Source status: {source_status}")
    lines.append("")
    lines.append("## Context Files Read")
    if context_summary:
        for row in context_summary:
            lines.append(f"- {row['file']} ({row['lines']} lines)")
    else:
        lines.append("- No context files found")

    lines.append("")
    lines.append("## DataForSEO Snapshot")
    if source_status["dataforseo"] == "ok":
        lines.append(f"- SERP search volume: {serp.get('search_volume')}")
        lines.append(f"- SERP CPC: {serp.get('cpc')}")
        lines.append(f"- SERP features: {', '.join(serp.get('features', [])) or 'none'}")
        lines.append("- Top SERP domains:")
        for d, count in sorted(top_domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"- {d} ({count})")
        lines.append("- Keyword ideas (top 10):")
        for row in ideas[:10]:
            lines.append(f"- {row.get('keyword')} | vol: {row.get('search_volume')} | cpc: {row.get('cpc')}")
        lines.append("- Question ideas (top 10):")
        for row in questions[:10]:
            lines.append(f"- {row.get('question')} | vol: {row.get('search_volume')}")
    else:
        lines.append(f"- DataForSEO unavailable: {source_status['dataforseo']}")

    lines.append("")
    lines.append("## GSC Topic-Matched Keywords (Last 30 Days)")
    if gsc_keywords:
        for row in gsc_keywords[:15]:
            lines.append(
                f"- {row.get('keyword')} | clicks: {row.get('clicks')} | "
                f"impr: {row.get('impressions')} | ctr: {row.get('ctr')} | pos: {row.get('position')}"
            )
    else:
        lines.append("- No matched topic keywords or GSC unavailable")

    lines.append("")
    lines.append("## GA4 Top Blog Pages (Last 30 Days)")
    if ga_top_pages:
        for row in ga_top_pages[:10]:
            lines.append(
                f"- {row.get('title')} ({row.get('path')}) | "
                f"views: {row.get('pageviews')} | sessions: {row.get('sessions')} | bounce: {row.get('bounce_rate')}"
            )
    else:
        lines.append("- No GA4 page data or GA4 unavailable")

    lines.append("")
    lines.append("## Suggested Direction")
    lines.append("- Focus on commercial-intent long-tail keywords with clear purchase intent.")
    lines.append("- Prioritize pages/keywords with high impressions and weak CTR from GSC.")
    lines.append("- Add strong internal links to best-selling products and relevant category pages.")
    lines.append("- Use bullet-list comparisons if table blocks are unsupported in your CMS.")

    return "\n".join(lines).strip() + "\n"
