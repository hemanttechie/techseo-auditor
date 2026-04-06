import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
import json
from collections import Counter
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{
  --bg:#f8f9fb;--surface:#ffffff;--surface2:#f1f3f6;--border:#e2e6ea;
  --accent:#1a56db;--accent-light:#eff4ff;--text:#111827;--muted:#6b7280;
  --good:#059669;--good-bg:#ecfdf5;--warn:#d97706;--warn-bg:#fffbeb;
  --bad:#dc2626;--bad-bg:#fef2f2;--info:#1d4ed8;--info-bg:#eff6ff;
}
html,body,[data-testid="stAppViewContainer"]{
  background:var(--bg)!important;color:#111827!important;
  font-family:'Inter',sans-serif!important;font-size:14px}
[data-testid="stHeader"]{background:var(--surface)!important;
  border-bottom:1px solid #e2e6ea!important;box-shadow:0 1px 3px rgba(0,0,0,.04)!important}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid #e2e6ea!important}
h1,h2,h3,h4{font-family:'Inter',sans-serif!important;color:#111827!important}

/* Hero */
.hero{padding:2rem 0 1.5rem;border-bottom:1px solid #e2e6ea;margin-bottom:1.5rem}
.hero-badge{display:inline-block;background:var(--accent-light);color:var(--accent);
  font-size:.72rem;font-weight:600;letter-spacing:.04em;padding:3px 10px;
  border-radius:20px;margin-bottom:.75rem;text-transform:uppercase}
.hero-title{font-size:1.9rem;font-weight:700;color:#111827;letter-spacing:-.03em;
  line-height:1.2;margin-bottom:.35rem}
.hero-sub{font-size:.85rem;color:#6b7280}

/* Input */
.stTextInput>div>div>input{
  background:var(--surface)!important;border:1.5px solid #e2e6ea!important;
  border-radius:8px!important;color:#111827!important;
  font-family:'Inter',sans-serif!important;font-size:.9rem!important;
  padding:.65rem 1rem!important;box-shadow:0 1px 2px rgba(0,0,0,.04)!important}
.stTextInput>div>div>input:focus{
  border-color:var(--accent)!important;
  box-shadow:0 0 0 3px rgba(26,86,219,.1)!important}

/* Button */
.stButton>button{
  background:var(--accent)!important;color:#fff!important;border:none!important;
  border-radius:8px!important;font-family:'Inter',sans-serif!important;
  font-weight:600!important;font-size:.88rem!important;
  padding:.65rem 1.5rem!important;letter-spacing:.01em!important}
.stButton>button:hover{background:#1648c0!important}

/* Metric cards */
.metric-card{background:#ffffff;border:1px solid #e2e6ea;
  border-radius:10px;padding:.9rem 1.1rem;margin-bottom:.5rem;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.metric-label{font-size:.68rem;color:#6b7280;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:.3rem;font-weight:500}
.metric-value{font-family:'IBM Plex Mono',monospace;font-size:1.05rem;font-weight:600;color:#111827}

/* Section headers */
.sh{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:#6b7280;border-bottom:2px solid #e2e6ea;
  padding-bottom:.4rem;margin:1.5rem 0 .85rem}

/* Audit rows */
.audit-row{display:flex;align-items:flex-start;gap:.75rem;padding:.6rem 0;
  border-bottom:1px solid #e2e6ea;font-size:.875rem}
.audit-row:last-child{border-bottom:none}
.audit-icon{font-size:1rem;flex-shrink:0;margin-top:1px}
.audit-label{font-weight:500;color:#111827}
.audit-detail{color:#6b7280;font-family:'IBM Plex Mono',monospace;
  font-size:.75rem;margin-top:2px;word-break:break-all}

/* Tags */
.tag{display:inline-block;font-size:.65rem;padding:2px 7px;border-radius:4px;
  margin-right:4px;font-weight:600;letter-spacing:.02em}
.tag-fail{background:var(--bad-bg);color:var(--bad)}
.tag-warn{background:var(--warn-bg);color:var(--warn)}
.tag-pass{background:var(--good-bg);color:var(--good)}
.tag-info{background:var(--info-bg);color:var(--info)}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  background:var(--surface)!important;
  border-bottom:2px solid #e2e6ea!important;gap:0!important;
  box-shadow:0 1px 3px rgba(0,0,0,.04)!important}
.stTabs [data-baseweb="tab"]{
  font-family:'Inter',sans-serif!important;font-size:.78rem!important;
  font-weight:500!important;color:#6b7280!important;
  background:transparent!important;border:none!important;
  padding:.7rem 1.1rem!important;white-space:nowrap!important}
.stTabs [aria-selected="true"]{
  color:var(--accent)!important;font-weight:600!important;
  border-bottom:2px solid var(--accent)!important}
.stTabs [data-baseweb="tab"]:hover{color:#111827!important}

/* Expanders */
.streamlit-expanderHeader{
  background:var(--surface)!important;border:1px solid #e2e6ea!important;
  border-radius:8px!important;font-family:'Inter',sans-serif!important;
  font-size:.82rem!important;font-weight:500!important;color:#111827!important}
.streamlit-expanderContent{
  border:1px solid #e2e6ea!important;border-top:none!important;
  border-radius:0 0 8px 8px!important;padding:.75rem 1rem!important}

/* Code */
code{background:#f1f3f6!important;color:#1e40af!important;
  font-family:'IBM Plex Mono',monospace!important;border-radius:4px!important;
  padding:.15rem .4rem!important;font-size:.8rem!important;
  border:1px solid #e2e6ea!important}

/* Progress */
.stProgress>div>div>div{background:var(--accent)!important}
hr{border-color:#e2e6ea!important}

/* Dataframes */
[data-testid="stDataFrame"]{border-radius:8px!important;overflow:hidden!important;
  border:1px solid #e2e6ea!important}

/* Score badge */
.score-pill{display:inline-flex;align-items:center;gap:.4rem;
  padding:.35rem .85rem;border-radius:20px;font-weight:700;font-size:.88rem}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def metric(label, value, color=None):
    c = color or "#111827"
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div>"
                f"<div class='metric-value' style='color:{c}'>{value}</div></div>",
                unsafe_allow_html=True)

def sh(text):
    st.markdown(f"<div class='sh'>{text}</div>", unsafe_allow_html=True)

def audit_row(icon, label, detail="", color=None):
    color_style = f"color:{color};" if color else ""
    detail_html = f"<div class='audit-detail'>{detail}</div>" if detail else ""
    st.markdown(f"""
    <div class='audit-row'>
      <div class='audit-icon'>{icon}</div>
      <div>
        <div class='audit-label' style='{color_style}'>{label}</div>
        {detail_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

def tag(text, kind="info"):
    return f"<span class='tag tag-{kind}'>{text}</span>"

def drill_item(text, color="var(--text)"):
    return (
        f"<div style='background:#f1f3f6;border:1px solid #e2e6ea;border-radius:4px;"
        f"padding:.45rem .75rem;margin-bottom:.3rem;font-family:IBM Plex Mono,monospace;"
        f"font-size:.76rem;word-break:break-all;color:{color}'>{text}</div>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE INDEXING CHECK
# ─────────────────────────────────────────────────────────────────────────────

def check_google_indexing(url, page_data):
    """
    Multi-signal indexing check. Uses:
    1. site: search scrape via Google (best-effort, may be rate-limited)
    2. On-page signals from already-crawled page data
    Returns a rich dict with status, confidence, and reason list.
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path

    signals = []       # list of (status, signal_name, detail, fix)
    indexed_votes = 0
    not_indexed_votes = 0

    # ── Signal 1: robots meta tag ─────────────────────────────────────────────
    meta = page_data.get("sections", {}).get("meta", {})
    robots = meta.get("robots", "").lower()
    if "noindex" in robots:
        not_indexed_votes += 3
        signals.append(("block", "robots meta = noindex",
                         f'<meta name="robots" content="{meta.get("robots")}"> explicitly blocks indexing.',
                         'Remove "noindex" from the robots meta tag, or change to "index, follow".'))
    elif "index" in robots:
        indexed_votes += 1
        signals.append(("pass", "robots meta = index",
                         f'<meta name="robots" content="{meta.get("robots")}"> explicitly allows indexing.',
                         None))
    else:
        indexed_votes += 1
        signals.append(("pass", "No noindex directive in robots meta",
                         "No robots meta tag found — Google indexes by default.",
                         None))

    # ── Signal 2: X-Robots-Tag HTTP header ────────────────────────────────────
    headers = page_data.get("sections", {}).get("headers", {})
    x_robots = headers.get("x-robots-tag", "").lower()
    if x_robots:
        if "noindex" in x_robots:
            not_indexed_votes += 3
            signals.append(("block", "X-Robots-Tag: noindex",
                             f"HTTP header X-Robots-Tag: {x_robots} blocks indexing.",
                             "Remove or update the X-Robots-Tag header on your server/CDN."))
        else:
            indexed_votes += 1
            signals.append(("pass", f"X-Robots-Tag: {x_robots}",
                             "HTTP-level robots tag does not block indexing.",
                             None))

    # ── Signal 3: HTTP status code ────────────────────────────────────────────
    status = page_data.get("status_code", 200)
    if status == 200:
        indexed_votes += 1
        signals.append(("pass", f"HTTP {status} OK",
                         "Page returns 200 — Googlebot can access and read it.",
                         None))
    elif status in (301, 302):
        not_indexed_votes += 1
        signals.append(("warn", f"HTTP {status} Redirect",
                         f"Page redirects ({status}). Google will index the destination, not this URL.",
                         "Ensure the canonical/final URL is what you want indexed."))
    elif status in (404, 410):
        not_indexed_votes += 4
        signals.append(("block", f"HTTP {status}",
                         "Page is not found or gone. Google will not index it.",
                         "Restore the page (200) or 301-redirect to a relevant live page."))
    elif status >= 500:
        not_indexed_votes += 3
        signals.append(("block", f"HTTP {status} Server Error",
                         "Server errors prevent Googlebot from crawling.",
                         "Fix server errors. If persistent, Googlebot will eventually drop the page."))

    # ── Signal 4: Canonical URL ────────────────────────────────────────────────
    canonical = meta.get("canonical", "")
    if canonical:
        canon_parsed = urlparse(canonical)
        if canon_parsed.netloc == domain and canon_parsed.path == path:
            indexed_votes += 1
            signals.append(("pass", "Canonical points to self",
                             f"<link rel='canonical' href='{canonical}'> correctly self-references.",
                             None))
        else:
            not_indexed_votes += 2
            signals.append(("warn", "Canonical points to a different URL",
                             f"Canonical: {canonical} — Google will index that URL instead of this one.",
                             "If this page is the primary, update canonical to point to itself."))
    else:
        signals.append(("warn", "No canonical tag",
                         "Without a canonical, Google may choose which URL to index if duplicates exist.",
                         "Add <link rel='canonical' href='THIS_PAGE_URL'> to <head>."))

    # ── Signal 5: robots.txt check ────────────────────────────────────────────
    robots_url = f"{parsed.scheme}://{domain}/robots.txt"
    try:
        r = requests.get(robots_url, timeout=8,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; TechSEOBot/1.0)"})
        if r.status_code == 200:
            robots_txt = r.text.lower()
            path_lower = path.lower()
            # Simple disallow check for Googlebot and *
            blocked = False
            current_agent = None
            for line in robots_txt.splitlines():
                line = line.strip()
                if line.startswith("user-agent:"):
                    current_agent = line.split(":", 1)[1].strip()
                elif line.startswith("disallow:") and current_agent in ("*", "googlebot"):
                    disallow_path = line.split(":", 1)[1].strip()
                    if disallow_path and path_lower.startswith(disallow_path.lower()):
                        blocked = True
                        not_indexed_votes += 3
                        signals.append(("block", "Blocked by robots.txt",
                                         f"robots.txt Disallow: {disallow_path} (agent: {current_agent}) blocks this path.",
                                         f"Edit robots.txt to remove or narrow the Disallow rule for {path}."))
                        break
            if not blocked:
                indexed_votes += 1
                signals.append(("pass", "robots.txt does not block this URL",
                                 f"Checked {robots_url} — no Disallow rule matches this path.",
                                 None))
        else:
            signals.append(("warn", f"robots.txt returned HTTP {r.status_code}",
                             "Could not read robots.txt to verify crawl permissions.",
                             "Ensure robots.txt is accessible at the root domain."))
    except Exception as e:
        signals.append(("warn", "Could not fetch robots.txt",
                         str(e)[:120],
                         "Manually check: " + robots_url))

    # ── Signal 6: Google site: search (scrape) ────────────────────────────────
    google_indexed = None
    google_result_count = None
    try:
        clean_url = url.split("?")[0].rstrip("/")
        search_url = f"https://www.google.com/search?q=site:{clean_url}&num=1"
        headers_g = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        gr = requests.get(search_url, headers=headers_g, timeout=10)
        if gr.status_code == 200:
            gsoup = BeautifulSoup(gr.text, "html.parser")
            # Check for result stats
            result_stats = gsoup.find(id="result-stats") or gsoup.find("div", {"id": "result-stats"})
            no_results_patterns = [
                "did not match any documents",
                "no results found",
                "0 results",
            ]
            page_text = gsoup.get_text().lower()
            if result_stats and result_stats.get_text():
                stats_text = result_stats.get_text()
                google_result_count = stats_text
                google_indexed = True
                indexed_votes += 3
                signals.append(("pass", "Found in Google site: search",
                                 f"Google returned results for site:{clean_url} — page appears indexed.",
                                 None))
            elif any(p in page_text for p in no_results_patterns):
                google_indexed = False
                not_indexed_votes += 3
                signals.append(("block", "Not found in Google site: search",
                                 f"site:{clean_url} returned no results — page may not be indexed yet.",
                                 "Submit URL in Google Search Console → URL Inspection → Request Indexing."))
            else:
                # Inconclusive (CAPTCHA, JS-rendered results, etc.)
                signals.append(("warn", "Google site: search inconclusive",
                                 "Google may have returned a CAPTCHA or JS-rendered page. Result could not be parsed.",
                                 "Verify manually: google.com/search?q=site:" + clean_url))
        elif gr.status_code == 429:
            signals.append(("warn", "Google rate-limited this check",
                             "Too many requests. Verify manually in a browser.",
                             "Open: https://www.google.com/search?q=site:" + clean_url))
        else:
            signals.append(("warn", f"Google search returned HTTP {gr.status_code}",
                             "Could not perform site: check automatically.",
                             "Verify manually: google.com/search?q=site:" + clean_url))
    except Exception as e:
        signals.append(("warn", "Could not reach Google for site: check",
                         str(e)[:120],
                         "Check manually: https://www.google.com/search?q=site:" + url.split("?")[0]))

    # ── Signal 7: Page freshness / last-modified ──────────────────────────────
    last_mod = headers.get("last-modified", "")
    if last_mod:
        signals.append(("pass", f"Last-Modified header: {last_mod}",
                         "Server declares a modification date — useful for Googlebot freshness signals.",
                         None))
    else:
        signals.append(("warn", "No Last-Modified header",
                         "Google cannot use Last-Modified to determine freshness.",
                         "Set Last-Modified and ETag headers on your server."))

    # ── Signal 8: Sitemap presence ────────────────────────────────────────────
    sitemap_url = f"{parsed.scheme}://{domain}/sitemap.xml"
    try:
        sr = requests.get(sitemap_url, timeout=8,
                          headers={"User-Agent": "Mozilla/5.0 (compatible; TechSEOBot/1.0)"})
        if sr.status_code == 200 and "<url" in sr.text.lower():
            # Check if our URL is mentioned
            if path in sr.text or url in sr.text:
                indexed_votes += 1
                signals.append(("pass", "URL found in sitemap.xml",
                                 f"{sitemap_url} exists and contains this URL.",
                                 None))
            else:
                signals.append(("warn", "Sitemap exists but URL not found in it",
                                 f"{sitemap_url} exists but this specific URL was not found inside.",
                                 "Add this URL to your sitemap.xml and resubmit in Google Search Console."))
        elif sr.status_code == 200:
            signals.append(("warn", "sitemap.xml exists but appears empty or malformed",
                             "File found but no <url> entries detected.",
                             "Regenerate your sitemap and validate at https://www.xml-sitemaps.com/validate-xml-sitemap.html"))
        else:
            not_indexed_votes += 1
            signals.append(("warn", f"No sitemap.xml found (HTTP {sr.status_code})",
                             "A sitemap helps Google discover and index pages faster.",
                             "Create a sitemap.xml and submit it via Google Search Console."))
    except Exception:
        signals.append(("warn", "Could not fetch sitemap.xml",
                         f"Attempted: {sitemap_url}",
                         "Ensure sitemap.xml is accessible and submitted in Google Search Console."))

    # ── Verdict ───────────────────────────────────────────────────────────────
    if not_indexed_votes >= 3:
        verdict = "likely_not_indexed"
    elif not_indexed_votes >= 1 and indexed_votes <= 2:
        verdict = "at_risk"
    elif indexed_votes >= 3:
        verdict = "likely_indexed"
    else:
        verdict = "uncertain"

    return {
        "verdict": verdict,
        "indexed_votes": indexed_votes,
        "not_indexed_votes": not_indexed_votes,
        "google_indexed": google_indexed,
        "google_result_count": google_result_count,
        "signals": signals,
        "manual_check_url": "https://www.google.com/search?q=site:" + url.split("?")[0],
        "search_console_url": "https://search.google.com/search-console/inspect?resource_id="
                              + f"{parsed.scheme}://{domain}/",
    }


def render_indexing_tab(url, results):
    """Render the full Google Indexing tab."""
    with st.spinner("Running indexing checks…"):
        idx = check_google_indexing(url, results)

    verdict = idx["verdict"]
    verdict_config = {
        "likely_indexed":     ("🟢", "#059669", "Likely Indexed",
                               "All major signals indicate this page is (or will be) indexed by Google."),
        "at_risk":            ("🟡", "#d97706", "At Risk / Uncertain",
                               "Mixed signals detected. Page may be indexed but has issues that could prevent or delay it."),
        "uncertain":          ("🟡", "#d97706", "Uncertain",
                               "Could not conclusively determine indexing status. Check Google Search Console."),
        "likely_not_indexed": ("🔴", "#dc2626", "Likely NOT Indexed",
                               "One or more critical signals block Google from indexing this page."),
    }
    icon, color, label, summary = verdict_config.get(verdict, verdict_config["uncertain"])

    # ── Verdict card ──────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='background:#ffffff;border:1.5px solid {color}40;"
        f"border-left:4px solid {color};border-radius:8px;padding:1.25rem 1.5rem;margin-bottom:1.5rem'>"
        f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:.4rem'>"
        f"<span style='font-size:1.5rem'>{icon}</span>"
        f"<span style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;"
        f"color:{color}'>{label}</span></div>"
        f"<div style='font-size:.85rem;color:#6b7280'>{summary}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Score bar ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    total_votes = max(idx["indexed_votes"] + idx["not_indexed_votes"], 1)
    index_pct = round(idx["indexed_votes"] / total_votes * 100)
    with c1: metric("Indexability Score", f"{index_pct}%",
                    "#059669" if index_pct >= 70 else "#d97706" if index_pct >= 40 else "#dc2626")
    with c2: metric("Positive Signals", str(idx["indexed_votes"]), "#059669")
    with c3: metric("Blocking Signals", str(idx["not_indexed_votes"]),
                    "#059669" if idx["not_indexed_votes"] == 0 else "#dc2626")

    # ── Quick action links ────────────────────────────────────────────────────
    sh("Quick Actions")
    st.markdown(
        f"<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:.5rem'>"
        f"<a href='{idx['manual_check_url']}' target='_blank' "
        f"style='background:#f1f3f6;border:1px solid #e2e6ea;border-radius:4px;"
        f"padding:.45rem .9rem;font-family:IBM Plex Mono,monospace;font-size:.76rem;"
        f"color:var(--accent);text-decoration:none'>🔍 Check site: in Google ↗</a>"
        f"<a href='{idx['search_console_url']}' target='_blank' "
        f"style='background:#f1f3f6;border:1px solid #e2e6ea;border-radius:4px;"
        f"padding:.45rem .9rem;font-family:IBM Plex Mono,monospace;font-size:.76rem;"
        f"color:var(--accent);text-decoration:none'>📊 Google Search Console ↗</a>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Signal breakdown ──────────────────────────────────────────────────────
    sh("Signal Breakdown — click to expand")
    for sig in idx["signals"]:
        status, name, detail, fix = sig
        if status == "pass":
            exp_icon, exp_color = "🟢", "#059669"
        elif status == "block":
            exp_icon, exp_color = "🔴", "#dc2626"
        else:
            exp_icon, exp_color = "🟡", "#d97706"

        with st.expander(f"{exp_icon} {name}"):
            st.markdown(
                f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.5rem'>{detail}</div>",
                unsafe_allow_html=True
            )
            if fix:
                st.markdown(
                    f"<div style='background:#fffbeb;border:1px solid #fde68a;"
                    f"border-radius:4px;padding:.5rem .75rem;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.76rem;color:#d97706'>"
                    f"<span style='font-weight:600'>Action: </span>{fix}</div>",
                    unsafe_allow_html=True
                )

    # ── Common reasons not indexed ─────────────────────────────────────────────
    blocking = [s for s in idx["signals"] if s[0] == "block"]
    if blocking or verdict in ("likely_not_indexed", "at_risk"):
        sh("Common Reasons Pages Are Not Indexed")
        reasons = [
            ("🔴", "noindex tag or header",
             "A <meta name='robots' content='noindex'> tag or X-Robots-Tag: noindex HTTP header explicitly tells Google not to index the page.",
             "Remove the noindex directive. Check both the HTML and your server/CDN headers."),
            ("🔴", "Blocked by robots.txt",
             "A Disallow rule in robots.txt prevents Googlebot from even crawling the page.",
             "Edit robots.txt to allow the path. Use Google Search Console → robots.txt Tester to verify."),
            ("🔴", "Page not reachable (4xx / 5xx)",
             "If Googlebot gets a 404, 403, or 500 error, it cannot index the page.",
             "Ensure the page returns HTTP 200 consistently. Fix server errors immediately."),
            ("🟡", "Canonical pointing elsewhere",
             "If <link rel='canonical'> points to a different URL, Google indexes that URL instead.",
             "Self-canonical the page if it is the primary version."),
            ("🟡", "Duplicate content / thin content",
             "Pages with very little unique content may be filtered out of the index.",
             "Add substantial, unique content (300+ words). Avoid duplicate pages."),
            ("🟡", "Recently published / not yet crawled",
             "New pages can take days to weeks to appear in Google's index.",
             "Submit in Google Search Console → URL Inspection → Request Indexing. Add to sitemap."),
            ("🟡", "Not in sitemap / poor internal linking",
             "Pages not in a sitemap and with no internal links are harder for Googlebot to discover.",
             "Add the URL to sitemap.xml and link to it from other indexed pages."),
            ("🟡", "Slow TTFB / server timeouts",
             "If the server is too slow, Googlebot may time out and not fully crawl the page.",
             "Improve server response time. TTFB should be < 200 ms."),
            ("🟡", "JavaScript-heavy page (no SSR)",
             "If the page requires JavaScript to render main content, Googlebot may not index it fully.",
             "Implement Server-Side Rendering (SSR) or pre-rendering for key content."),
            ("🟡", "Low PageRank / no external links",
             "Pages with no backlinks may not get crawled frequently or at all.",
             "Build internal links from high-authority pages and acquire external backlinks."),
        ]
        for r_icon, r_name, r_detail, r_fix in reasons:
            with st.expander(f"{r_icon} {r_name}"):
                st.markdown(
                    f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.5rem'>{r_detail}</div>"
                    f"<div style='background:#fffbeb;border:1px solid #fde68a;"
                    f"border-radius:4px;padding:.5rem .75rem;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.76rem;color:#d97706'><span style='font-weight:600'>Fix: </span>{r_fix}</div>",
                    unsafe_allow_html=True
                )


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def fetch_page(url, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TechSEOBot/1.0)",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    start = time.time()
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        return resp, round((time.time() - start) * 1000), None
    except Exception as e:
        return None, 0, str(e)


def analyze_page(url):
    r = {"url": url, "sections": {}}
    parsed = urlparse(url)

    resp, ttfb_ms, err = fetch_page(url)
    if err or resp is None:
        r["fetch_error"] = err or "Unknown error"
        return r

    soup = BeautifulSoup(resp.text, "html.parser")
    r.update({
        "ttfb_ms": ttfb_ms,
        "status_code": resp.status_code,
        "final_url": resp.url,
        "redirect_count": len(resp.history),
        "html_size_bytes": len(resp.content),
    })

    # ── META ──────────────────────────────────────────────────────────────────
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    desc = desc_tag.get("content", "").strip() if desc_tag else ""
    canonical = soup.find("link", rel=lambda x: x and "canonical" in x)
    robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    viewport = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    charset_tag = soup.find("meta", attrs={"charset": True})
    html_tag = soup.find("html")
    og = {t.get("property"): t.get("content", "") for t in
          soup.find_all("meta", attrs={"property": re.compile(r"^og:", re.I)})}
    tw = {t.get("name"): t.get("content", "") for t in
          soup.find_all("meta", attrs={"name": re.compile(r"^twitter:", re.I)})}
    r["sections"]["meta"] = {
        "title": title, "title_length": len(title),
        "description": desc, "description_length": len(desc),
        "canonical": canonical.get("href", "") if canonical else "",
        "robots": robots_meta.get("content", "") if robots_meta else "not set",
        "viewport": viewport.get("content", "") if viewport else "",
        "charset": charset_tag.get("charset", "") if charset_tag else "",
        "lang": html_tag.get("lang", "") if html_tag else "",
        "og": og, "twitter": tw,
    }

    # ── HEADINGS ─────────────────────────────────────────────────────────────
    r["sections"]["headings"] = {
        f"h{n}": [t.get_text(strip=True) for t in soup.find_all(f"h{n}")]
        for n in range(1, 7)
    }

    # ── IMAGES ───────────────────────────────────────────────────────────────
    GENERIC_PATTERNS = re.compile(
        r"(whatsapp|img[-_]?\d{4,}|dsc\d+|image\d+|photo\d+|screenshot|untitled|"
        r"gettyimages|getty|shutterstock|istockphoto|depositphotos|dreamstime|"
        r"wp[-_]?\d+x\d+|resize|thumb|thumbnail|upload|download|"
        r"noname|default|placeholder|banner\d*|hero\d*|slide\d+|pic\d+|pict\d+)",
        re.I
    )
    img_list = []
    for img in soup.find_all("img"):
        src = urljoin(url, img.get("src", ""))
        alt = img.get("alt")
        src_path = urlparse(src).path
        filename = src_path.split("/")[-1].split("?")[0]
        name_no_ext = re.sub(r"\.[^.]+$", "", filename)
        is_generic = bool(GENERIC_PATTERNS.search(name_no_ext)) or (len(name_no_ext) <= 3 and name_no_ext.isdigit())
        is_stock = bool(re.search(r"getty|shutterstock|istock|depositphotos|dreamstime|123rf|alamy", src, re.I))
        is_whatsapp = bool(re.search(r"whatsapp", filename, re.I))
        img_list.append({
            "src": src, "alt": alt,
            "has_alt": alt is not None, "alt_empty": alt == "",
            "width": img.get("width", ""), "height": img.get("height", ""),
            "lazy": img.get("loading", "") == "lazy",
            "srcset": bool(img.get("srcset")),
            "filename": filename,
            "name_no_ext": name_no_ext,
            "is_generic_name": is_generic,
            "is_stock": is_stock,
            "is_whatsapp": is_whatsapp,
        })
    r["sections"]["images"] = img_list

    # ── SCRIPTS (detailed) ───────────────────────────────────────────────────
    head_el = soup.find("head")
    all_scripts = soup.find_all("script")
    head_scripts = set(head_el.find_all("script")) if head_el else set()

    scripts_detail = []
    for s_tag in all_scripts:
        src = s_tag.get("src", "")
        in_head = s_tag in head_scripts
        has_defer = s_tag.has_attr("defer")
        has_async = s_tag.has_attr("async")
        is_external = bool(src)
        is_blocking = in_head and is_external and not has_defer and not has_async
        scripts_detail.append({
            "src": urljoin(url, src) if src else "(inline)",
            "location": "head" if in_head else "body",
            "external": is_external,
            "defer": has_defer, "async": has_async,
            "blocking": is_blocking,
            "size_hint": len(s_tag.string or "") if not src else 0,
        })
    r["sections"]["scripts"] = scripts_detail

    # ── STYLESHEETS ──────────────────────────────────────────────────────────
    css_list = []
    head_links = set(head_el.find_all("link")) if head_el else set()
    for link in soup.find_all("link", rel=lambda x: x and "stylesheet" in x):
        href = link.get("href", "")
        css_list.append({
            "href": urljoin(url, href) if href else "(missing href)",
            "media": link.get("media", "all"),
            "in_head": link in head_links,
            "preload": False,
        })
    for link in soup.find_all("link", rel=lambda x: x and "preload" in x):
        if link.get("as") == "style":
            css_list.append({
                "href": urljoin(url, link.get("href", "")),
                "media": link.get("media", "all"),
                "in_head": link in head_links,
                "preload": True,
            })
    r["sections"]["stylesheets"] = css_list

    # ── LINKS ─────────────────────────────────────────────────────────────────
    base_domain = parsed.netloc

    # ── Internal links: ONLY from <a> tags inside <p> tags within article body ─
    # This excludes nav menus, sidebars, footers, related-articles widgets, etc.
    article_body_el = (
        soup.find("article") or
        soup.find("main") or
        soup.find(id=re.compile(r"content|article|story|body|post", re.I)) or
        soup.find(class_=re.compile(
            r"article[-_]?body|post[-_]?body|story[-_]?body|"
            r"article[-_]?content|entry[-_]?content|content[-_]?body|"
            r"\bstory\b|\barticle\b|\bpost\b", re.I))
    )

    # Collect <p> tags from article body (or full page if no body found)
    para_scope = (article_body_el or soup).find_all("p")

    int_links, ext_links = [], []
    seen_int_hrefs = set()   # deduplicate internal links
    seen_ext_hrefs = set()

    for p in para_scope:
        for a in p.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            abs_href = urljoin(url, href)
            lp = urlparse(abs_href)
            rel_attr = a.get("rel", [])
            entry = {
                "href": abs_href,
                "text": a.get_text(strip=True),
                "nofollow": "nofollow" in rel_attr,
                "ugc": "ugc" in rel_attr,
                "sponsored": "sponsored" in rel_attr,
                "rel": " ".join(rel_attr),
            }
            if lp.netloc == base_domain or not lp.netloc:
                if abs_href not in seen_int_hrefs:
                    seen_int_hrefs.add(abs_href)
                    int_links.append(entry)
            else:
                if abs_href not in seen_ext_hrefs:
                    seen_ext_hrefs.add(abs_href)
                    ext_links.append(entry)

    r["sections"]["links"] = {
        "internal": int_links,
        "external": ext_links,
        "internal_scope": "article body <p> tags" if article_body_el else "full page <p> tags",
    }

    # ── STRUCTURED DATA ───────────────────────────────────────────────────────
    sd = []
    for sc in soup.find_all("script", type="application/ld+json"):
        try:
            sd.append(json.loads(sc.string or "{}"))
        except Exception:
            sd.append({"_error": "parse failed", "_raw": (sc.string or "")[:200]})
    r["sections"]["structured_data"] = sd

    # ── PERFORMANCE ───────────────────────────────────────────────────────────
    blocking = [s for s in scripts_detail if s["blocking"]]
    r["sections"]["performance"] = {
        "html_size_kb": round(len(resp.content) / 1024, 1),
        "ttfb_ms": ttfb_ms,
        "render_blocking_scripts": blocking,
        "render_blocking_count": len(blocking),
        "external_scripts": sum(1 for s in scripts_detail if s["external"]),
        "inline_scripts": sum(1 for s in scripts_detail if not s["external"]),
        "stylesheets_count": len(css_list),
        "total_scripts": len(scripts_detail),
    }

    # ── HTTP HEADERS ──────────────────────────────────────────────────────────
    important = [
        "content-type", "cache-control", "x-frame-options", "x-content-type-options",
        "strict-transport-security", "content-security-policy", "x-xss-protection",
        "referrer-policy", "permissions-policy", "server", "x-powered-by",
        "last-modified", "etag", "vary", "content-encoding", "transfer-encoding",
    ]
    r["sections"]["headers"] = {h: resp.headers[h] for h in important if h in resp.headers}

    # ── URL ───────────────────────────────────────────────────────────────────
    r["sections"]["url"] = {
        "protocol": parsed.scheme, "domain": parsed.netloc,
        "path": parsed.path, "query": parsed.query,
        "path_depth": len([p for p in parsed.path.split("/") if p]),
        "path_length": len(parsed.path),
        "has_uppercase": any(c.isupper() for c in parsed.path),
        "has_underscores": "_" in parsed.path,
        "has_spaces": " " in parsed.path or "%20" in parsed.path,
        "has_params": bool(parsed.query),
    }

    # ── CONTENT ───────────────────────────────────────────────────────────────
    def clean_article_text(raw):
        """
        Strip embed/quote markers from article body text.
        Removes: [caption ...], [embed ...], [video ...], [gallery ...],
                 [tweet ...], [quote ...], [ad ...], [image ...], [photo ...]
                 and any [...] block that looks like a shortcode or embed.
        Also strips standalone lines that are just social handles,
        URLs, hashtags, or read-more prompts.
        """
        if not raw:
            return ""
        # Remove bracketed shortcodes / embeds: [caption id="..."], [/caption], [tweet 123] etc.
        text = re.sub(r"\[/?[a-zA-Z][^\]]{0,120}\]", " ", raw)
        # Remove lines that are purely URLs
        text = re.sub(r"https?://\S+", " ", text)
        # Remove lines that are hashtags or @handles
        text = re.sub(r"[@#]\w+", " ", text)
        # Remove common "read also / also read" prompts
        text = re.sub(
            r"(also read|read also|read more|यह भी पढ़ें|यह भी पढें|और पढ़ें)[^\n]*",
            " ", text, flags=re.I
        )
        # Collapse whitespace
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text

    # ── Step 1: Try to get articleBody from JSON-LD schema ────────────────────
    schema_article_body = ""
    schema_headline = ""
    schema_description = ""
    schema_word_count = 0
    source_label = "DOM"

    sd_raw = r["sections"].get("structured_data", [])
    article_schema_types = (
        "Article", "NewsArticle", "BlogPosting", "ReportageNewsArticle",
        "AnalysisNewsArticle", "OpinionNewsArticle", "ReviewNewsArticle",
        "SatiricalArticle", "ScholarlyArticle", "TechArticle",
    )
    for schema_item in sd_raw:
        if not isinstance(schema_item, dict):
            continue
        stype = schema_item.get("@type", "")
        # Handle @type as list or string
        if isinstance(stype, list):
            stype = " ".join(stype)
        if any(t in stype for t in article_schema_types):
            raw_body = schema_item.get("articleBody", "")
            if raw_body:
                schema_article_body = clean_article_text(raw_body)
            schema_headline = schema_item.get("headline", "")
            schema_description = schema_item.get("description", "")
            # Some schemas include wordCount directly
            schema_word_count = int(schema_item.get("wordCount", 0) or 0)
            break

    # ── Step 2: DOM fallback — strip nav/header/footer then extract main body ─
    for t in soup(["script", "style", "noscript", "meta", "link", "nav",
                   "header", "footer", "aside"]):
        t.decompose()

    main_el = (
        soup.find("article") or
        soup.find("main") or
        soup.find(id=re.compile(r"content|article|story|body|post", re.I)) or
        soup.find(class_=re.compile(
            r"article[-_]?body|post[-_]?body|story[-_]?body|"
            r"article[-_]?content|entry[-_]?content|content[-_]?body|"
            r"\bstory\b|\barticle\b|\bpost\b", re.I))
    )
    dom_text_raw = (main_el or soup).get_text(separator=" ", strip=True)
    dom_text_clean = clean_article_text(dom_text_raw)

    # ── Step 3: Decide which source to use for word count ─────────────────────
    if schema_article_body:
        # Primary: use cleaned schema articleBody
        article_text = schema_article_body
        source_label = "Schema articleBody"
        all_words = [w for w in re.split(r"\s+", article_text) if len(w) >= 2]
        word_count = len(all_words)
    elif schema_word_count > 0:
        # Schema declares wordCount but no body text
        article_text = dom_text_clean
        word_count = schema_word_count
        source_label = "Schema wordCount"
    else:
        # Fallback: cleaned DOM text
        article_text = dom_text_clean
        all_words = [w for w in re.split(r"\s+", article_text) if len(w) >= 2]
        word_count = len(all_words)
        source_label = "DOM (no schema)"

    # ── Step 4: Extract named entities from article text ─────────────────────
    # Use full article text for entity extraction (richer context than title alone)
    article_entities = extract_entities(article_text)

    r["sections"]["content"] = {
        "word_count": word_count,
        "word_count_source": source_label,
        "article_text_preview": article_text[:500],
        "schema_headline": schema_headline,
        "schema_description": schema_description,
        "article_entities": article_entities,
        "paragraphs": len(soup.find_all("p")),
        "lists": len(soup.find_all(["ul", "ol"])),
        "tables": len(soup.find_all("table")),
    }
    return r


# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def compute_score(r):
    s = r.get("sections", {})
    score = 100
    issues = []

    def iss(pts, sev, cat, msg, detail="", drilldown=None):
        nonlocal score
        score -= pts
        issues.append({"severity": sev, "category": cat, "message": msg,
                        "detail": detail, "drilldown": drilldown or []})

    if r.get("fetch_error"):
        return 0, [{"severity": "fail", "category": "Fetch", "message": "Page could not be fetched",
                    "detail": r["fetch_error"], "drilldown": []}]

    sc = r.get("status_code", 200)
    if sc >= 400:
        iss(30, "fail", "HTTP", f"HTTP {sc} error", "Page returns an error response.")
    elif sc >= 300:
        iss(5, "warn", "HTTP", f"HTTP {sc} redirect",
            f"{r.get('redirect_count',0)} redirect(s). Final: {r.get('final_url','')}")

    meta = s.get("meta", {})
    tl = meta.get("title_length", 0)
    if not meta.get("title"):
        iss(15, "fail", "Meta", "Missing <title> tag", "No title element found in <head>.")
    elif tl < 30:
        iss(8, "warn", "Meta", f"Title too short ({tl} chars)",
            f'Current: "{meta["title"]}" — ideal 50–60 chars.',
            drilldown=[f'Current value ({tl} chars): "{meta["title"]}"',
                       "Action: expand to 50–60 characters with primary keyword near the start"])
    elif tl > 60:
        iss(5, "warn", "Meta", f"Title too long ({tl} chars)",
            "May be truncated in SERPs at ~60 chars.",
            drilldown=[f'Current value ({tl} chars): "{meta["title"][:120]}"',
                       "Action: shorten to 50–60 characters"])

    dl = meta.get("description_length", 0)
    if not meta.get("description"):
        iss(10, "fail", "Meta", "Missing meta description",
            "No meta description found.",
            drilldown=["Action: add <meta name='description' content='...'> in <head>",
                       "Ideal length: 120–160 characters"])
    elif dl < 70:
        iss(5, "warn", "Meta", f"Meta description too short ({dl} chars)",
            "Ideal: 120–160 chars.",
            drilldown=[f'Current ({dl} chars): "{meta["description"]}"',
                       "Action: expand to 120–160 characters"])
    elif dl > 160:
        iss(5, "warn", "Meta", f"Meta description too long ({dl} chars)",
            "May be cut off in SERPs.",
            drilldown=[f'Current ({dl} chars): "{meta["description"][:160]}…"',
                       "Action: shorten to ≤ 160 characters"])

    if not meta.get("canonical"):
        iss(8, "warn", "Meta", "No canonical URL set",
            "Prevents duplicate content issues.",
            drilldown=["Action: add <link rel='canonical' href='FULL_URL'> inside <head>",
                       "This page's URL should be: " + r.get("final_url", r.get("url", ""))])
    if not meta.get("lang"):
        iss(5, "warn", "Meta", "Missing lang attribute on <html>",
            "Required for accessibility and language targeting.",
            drilldown=["Action: add lang='en' (or your language code) to the <html> tag",
                       "Example: <html lang='en'>"])
    if not meta.get("viewport"):
        iss(8, "fail", "Mobile", "Missing viewport meta tag",
            "Required for mobile rendering.",
            drilldown=["Action: add inside <head>:",
                       "<meta name='viewport' content='width=device-width, initial-scale=1'>"])
    if not meta.get("og"):
        iss(4, "warn", "Social", "No Open Graph tags",
            "OG tags control how the page appears when shared on social media.",
            drilldown=["Add: <meta property='og:title' content='...'>",
                       "Add: <meta property='og:description' content='...'>",
                       "Add: <meta property='og:image' content='FULL_IMAGE_URL'>",
                       "Add: <meta property='og:url' content='CANONICAL_URL'>"])
    if not meta.get("twitter"):
        iss(2, "warn", "Social", "No Twitter Card tags",
            "Twitter Card tags control how the page looks when shared on Twitter/X.",
            drilldown=["Add: <meta name='twitter:card' content='summary_large_image'>",
                       "Add: <meta name='twitter:title' content='...'>",
                       "Add: <meta name='twitter:description' content='...'>"])

    h = s.get("headings", {})
    h1s = h.get("h1", [])
    if not h1s:
        iss(12, "fail", "Headings", "No H1 tag found",
            "Every page should have exactly one H1.",
            drilldown=["Action: add a single <h1> tag containing the primary keyword for this page",
                       "The H1 should describe the page content clearly"])
    elif len(h1s) > 1:
        iss(6, "warn", "Headings", f"Multiple H1 tags ({len(h1s)} found)",
            "Use exactly one H1 per page.",
            drilldown=[f"H1 #{i+1}: {t[:120]}" for i, t in enumerate(h1s)] +
                      ["Action: keep one H1, convert others to H2 or H3"])

    imgs = s.get("images", [])
    missing_alt = [i for i in imgs if not i["has_alt"]]
    empty_alt = [i for i in imgs if i["has_alt"] and i["alt_empty"]]
    no_dims = [i for i in imgs if not i.get("width") or not i.get("height")]
    no_lazy = [i for i in imgs if not i.get("lazy")]

    if missing_alt:
        iss(min(12, len(missing_alt) * 2), "fail", "Images",
            f"{len(missing_alt)} image(s) missing alt attribute",
            "Required for accessibility and image SEO.",
            drilldown=[f"src: {i['src']}" for i in missing_alt[:15]] +
                      (["… and more"] if len(missing_alt) > 15 else []) +
                      ["Action: add alt='descriptive text' to each image"])
    if empty_alt:
        iss(min(6, len(empty_alt)), "warn", "Images",
            f"{len(empty_alt)} image(s) have empty alt text",
            "Only use empty alt for purely decorative images.",
            drilldown=[f"src: {i['src']}" for i in empty_alt[:15]] +
                      ["Action: add descriptive alt text, or confirm image is decorative"])
    if no_dims:
        iss(min(5, len(no_dims)), "warn", "Images",
            f"{len(no_dims)} image(s) missing width/height attributes",
            "Missing dimensions cause Cumulative Layout Shift (CLS).",
            drilldown=[f"src: {i['src']}" for i in no_dims[:15]] +
                      ["Action: add explicit width and height attributes to every <img>"])
    if imgs and no_lazy:
        iss(3, "warn", "Performance", f"{len(no_lazy)} image(s) not lazy-loaded",
            "Lazy-loading below-the-fold images improves LCP.",
            drilldown=[f"src: {i['src']}" for i in no_lazy[:15]] +
                      ["Action: add loading='lazy' to all non-critical images"])

    perf = s.get("performance", {})
    blocking = perf.get("render_blocking_scripts", [])
    if blocking:
        iss(min(12, len(blocking) * 4), "fail", "Performance",
            f"{len(blocking)} render-blocking script(s) in <head>",
            "Scripts in <head> without defer/async block HTML parsing and delay page render.",
            drilldown=[f"{sc['src']}" for sc in blocking] +
                      ["Action: add defer attribute to non-critical scripts",
                       "Action: add async attribute to independent scripts (analytics, ads)",
                       "Rule: defer = execute after parse; async = execute as soon as downloaded"])

    scripts_all = s.get("scripts", [])
    slow_ext = [sc for sc in scripts_all
                if sc["external"] and not sc["defer"] and not sc["async"] and not sc["blocking"]]
    if slow_ext:
        iss(min(6, len(slow_ext) * 2), "warn", "Performance",
            f"{len(slow_ext)} external script(s) without defer/async (body)",
            "Body scripts still benefit from defer/async for parse efficiency.",
            drilldown=[f"{sc['src']}  [body, no defer/async]" for sc in slow_ext[:15]] +
                      ["Action: add defer or async to these script tags"])

    if perf.get("html_size_kb", 0) > 300:
        iss(8, "warn", "Performance",
            f"Large HTML document ({perf['html_size_kb']} KB)",
            "Large HTML slows parse time. Ideal < 100 KB.",
            drilldown=[f"Current: {perf['html_size_kb']} KB  (ideal: < 100 KB)",
                       "Likely cause: large inline scripts or inline CSS (check inline script count)",
                       "Action: minify HTML, move inline scripts to external files with caching"])

    if perf.get("ttfb_ms", 0) > 600:
        hdrs = s.get("headers", {})
        iss(10, "warn", "Performance",
            f"Slow TTFB ({perf['ttfb_ms']} ms)",
            "Time to First Byte > 600 ms. Target < 200 ms.",
            drilldown=[
                f"TTFB: {perf['ttfb_ms']} ms  (good: <200 ms | acceptable: <600 ms)",
                f"Server: {hdrs.get('server', 'unknown')}",
                f"Cache-Control: {hdrs.get('cache-control', 'not set')}",
                f"Content-Encoding: {hdrs.get('content-encoding', 'not set')}",
                "Fixes: add server-side caching, use a CDN, enable gzip/brotli compression",
            ])

    if perf.get("inline_scripts", 0) > 20:
        iss(4, "warn", "Performance",
            f"High inline script count ({perf['inline_scripts']})",
            "Inline scripts cannot be cached by the browser.",
            drilldown=[f"Inline script count: {perf['inline_scripts']}",
                       "Action: move inline scripts to external .js files with long cache headers"])

    css_list = s.get("stylesheets", [])
    blocking_css = [c for c in css_list
                    if c["in_head"] and not c["preload"] and c["media"] in ("all", "screen", "")]
    if len(blocking_css) > 3:
        iss(4, "warn", "Performance",
            f"{len(blocking_css)} render-blocking stylesheet(s)",
            "Multiple CSS files in <head> delay first paint.",
            drilldown=[c["href"] for c in blocking_css[:15]] +
                      ["Action: consolidate CSS files, inline critical CSS, or use preload"])

    url_d = s.get("url", {})
    if url_d.get("protocol") != "https":
        iss(15, "fail", "Security", "Page not served over HTTPS",
            "HTTPS is a confirmed Google ranking signal.",
            drilldown=[f"Current protocol: {url_d.get('protocol', 'unknown')}",
                       "Action: obtain SSL certificate, configure HTTPS, 301 redirect HTTP → HTTPS"])
    if url_d.get("has_uppercase"):
        iss(3, "warn", "URL", "Uppercase letters in URL path",
            "Google treats URLs as case-sensitive; keep them lowercase.",
            drilldown=[f"Path: {url_d.get('path', '')}",
                       "Action: lowercase all URL segments and add 301 redirects"])
    if url_d.get("has_underscores"):
        iss(2, "warn", "URL", "Underscores in URL path",
            "Google treats underscores as word-joiners, not separators.",
            drilldown=[f"Path: {url_d.get('path', '')}",
                       "Action: replace underscores with hyphens, add 301 redirects"])
    if url_d.get("path_depth", 0) > 4:
        iss(3, "warn", "URL", f"Deep URL path (depth {url_d['path_depth']})",
            "Flat URL structures are preferred for crawlability.",
            drilldown=[f"Path: {url_d.get('path', '')}",
                       f"Depth: {url_d['path_depth']} levels (recommended: ≤ 3)"])

    hdrs = s.get("headers", {})
    if "x-content-type-options" not in hdrs:
        iss(2, "warn", "Security", "Missing X-Content-Type-Options",
            "Prevents MIME-type sniffing.",
            drilldown=["Add response header: X-Content-Type-Options: nosniff"])
    if "x-frame-options" not in hdrs and "content-security-policy" not in hdrs:
        iss(3, "warn", "Security", "No clickjacking protection",
            "No X-Frame-Options or CSP frame-ancestors directive.",
            drilldown=["Option A: X-Frame-Options: SAMEORIGIN",
                       "Option B: Content-Security-Policy: frame-ancestors 'self'"])
    if "strict-transport-security" not in hdrs and url_d.get("protocol") == "https":
        iss(3, "warn", "Security", "Missing HSTS header",
            "HSTS enforces HTTPS and prevents protocol downgrade.",
            drilldown=["Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"])
    if "referrer-policy" not in hdrs:
        iss(1, "warn", "Security", "Missing Referrer-Policy",
            "Controls how much referrer info is sent cross-origin.",
            drilldown=["Recommended: Referrer-Policy: strict-origin-when-cross-origin"])

    sd = s.get("structured_data", [])
    if not sd:
        iss(5, "warn", "Schema", "No structured data (JSON-LD) found",
            "Schema markup enables rich results in Google SERPs.",
            drilldown=["Consider adding schema types relevant to this page:",
                       "Article / NewsArticle — for editorial/news content",
                       "BreadcrumbList — for navigation path",
                       "FAQPage — for FAQ sections",
                       "Organization / WebSite — on homepage",
                       "Reference: https://schema.org"])

    int_links = s.get("links", {}).get("internal", [])
    ext_links = s.get("links", {}).get("external", [])
    no_anchor = [l for l in int_links + ext_links if not l.get("text")]
    if no_anchor:
        iss(min(5, len(no_anchor)), "warn", "Links",
            f"{len(no_anchor)} link(s) with no anchor text",
            "Empty anchors miss keyword signals and hurt accessibility.",
            drilldown=[l["href"] for l in no_anchor[:15]] +
                      ["Action: add descriptive anchor text to all links"])

    wc = s.get("content", {}).get("word_count", 0)
    if wc < 300:
        iss(5, "warn", "Content", f"Low word count ({wc} words)",
            "Thin content tends to rank poorly.",
            drilldown=[f"Current word count: {wc}",
                       "Recommendation: aim for 300+ words of original, helpful content",
                       "For news articles: 400–600 words minimum"])

    return max(0, score), issues


# ─────────────────────────────────────────────────────────────────────────────
# ISSUE EXPANDER WITH DRILL-DOWN
# ─────────────────────────────────────────────────────────────────────────────

def render_issue(issue):
    sev = issue["severity"]
    icon = "🔴" if sev == "fail" else "🟡"
    cat_html = tag(issue["category"], "fail" if sev == "fail" else "warn")
    drilldown = issue.get("drilldown", [])

    with st.expander(f"{icon} {issue['message']}", expanded=False):
        st.markdown(
            f"<div style='margin-bottom:.6rem'>{cat_html}"
            f"<span style='font-size:.82rem;color:#6b7280;margin-left:8px'>"
            f"{issue['detail']}</span></div>",
            unsafe_allow_html=True
        )
        if drilldown:
            st.markdown(
                "<div style='font-size:.68rem;color:#6b7280;text-transform:uppercase;"
                "letter-spacing:2px;margin:.4rem 0'>Details & Fix</div>",
                unsafe_allow_html=True
            )
            for item in drilldown:
                color = "#d97706" if item.lower().startswith("action:") \
                    else "#1d4ed8" if item.lower().startswith("add:") \
                    else "#059669" if item.lower().startswith("option") \
                    else "var(--text)"
                st.markdown(drill_item(item, color), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PERFORMANCE TAB  (rich script/CSS drill-down)
# ─────────────────────────────────────────────────────────────────────────────

def render_performance_tab(results):
    s = results.get("sections", {})
    perf = s.get("performance", {})
    scripts_all = s.get("scripts", [])
    css_list = s.get("stylesheets", [])
    hdrs = s.get("headers", {})

    ttfb = perf.get("ttfb_ms", 0)
    html_kb = perf.get("html_size_kb", 0)
    blocking = perf.get("render_blocking_scripts", [])

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("TTFB", f"{ttfb} ms",
                    "#059669" if ttfb < 200 else "#d97706" if ttfb < 600 else "#dc2626")
    with c2: metric("HTML Size", f"{html_kb} KB",
                    "#059669" if html_kb < 100 else "#d97706" if html_kb < 300 else "#dc2626")
    with c3: metric("Render-Blocking Scripts", str(len(blocking)),
                    "#059669" if not blocking else "#dc2626")
    with c4: metric("Total Scripts", str(perf.get("total_scripts", 0)))

    # ── Render-blocking scripts ───────────────────────────────────────────────
    sh(f"🔴 Render-Blocking Scripts ({len(blocking)}) — head, external, no defer/async")
    if blocking:
        for sc in blocking:
            st.markdown(
                f"<div style='background:#fef2f2;border:1px solid #fecaca;"
                f"border-radius:5px;padding:.65rem .9rem;margin-bottom:.4rem'>"
                f"<div style='display:flex;gap:8px;align-items:center;margin-bottom:4px'>"
                f"<span style='color:#dc2626;font-family:IBM Plex Mono,monospace;font-size:.7rem;font-weight:600'>BLOCKING</span>"
                f"<span style='color:#6b7280;font-family:IBM Plex Mono,monospace;font-size:.68rem'>"
                f"location: {sc['location']} | defer: {'✓' if sc['defer'] else '✗'} | async: {'✓' if sc['async'] else '✗'}"
                f"</span></div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:.76rem;word-break:break-all;"
                f"color:#111827;margin-bottom:4px'>{sc['src']}</div>"
                f"<div style='color:#d97706;font-size:.71rem;font-family:IBM Plex Mono,monospace'>"
                f"Fix → add <b>defer</b> (non-critical) or <b>async</b> (independent) attribute</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        audit_row("🟢", "No render-blocking scripts detected", color="#059669")

    # ── All external scripts ──────────────────────────────────────────────────
    ext = [sc for sc in scripts_all if sc["external"]]
    sh(f"All External Scripts ({len(ext)})")
    if ext:
        with st.expander(f"View all {len(ext)} external scripts", expanded=len(blocking) > 0):
            for sc in ext:
                if sc["blocking"]:
                    status_label, status_color = "BLOCKING", "#dc2626"
                elif sc["defer"]:
                    status_label, status_color = "defer", "#059669"
                elif sc["async"]:
                    status_label, status_color = "async", "#059669"
                else:
                    status_label, status_color = "no attr", "#d97706"
                st.markdown(
                    f"<div style='padding:.45rem 0;border-bottom:1px solid #e2e6ea;"
                    f"font-family:IBM Plex Mono,monospace;font-size:.76rem'>"
                    f"<span style='color:{status_color};font-weight:600;min-width:72px;"
                    f"display:inline-block'>[{status_label}]</span>"
                    f"<span style='word-break:break-all;color:#111827'>{sc['src']}</span>"
                    f"<span style='color:#6b7280;margin-left:6px;font-size:.68rem'>({sc['location']})</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    else:
        audit_row("🟡", "No external scripts found")

    # ── Inline scripts ────────────────────────────────────────────────────────
    inline = [sc for sc in scripts_all if not sc["external"]]
    sh(f"Inline Scripts ({len(inline)})")
    c1, c2, c3 = st.columns(3)
    with c1: metric("Count", str(len(inline)),
                    "#d97706" if len(inline) > 20 else "#059669")
    with c2:
        total_inline_bytes = sum(sc.get("size_hint", 0) for sc in inline)
        metric("Total Inline Size", f"{round(total_inline_bytes/1024,1)} KB")
    with c3:
        head_inline = sum(1 for sc in inline if sc["location"] == "head")
        metric("In <head>", str(head_inline), "#d97706" if head_inline > 0 else "#059669")

    # ── Stylesheets ────────────────────────────────────────────────────────────
    sh(f"Stylesheets ({len(css_list)})")
    if css_list:
        for c in css_list:
            if c["preload"]:
                icon, note_color, note = "🟢", "#059669", "preloaded"
            elif c["in_head"] and c["media"] in ("all", "screen", ""):
                icon, note_color, note = "🟡", "#d97706", "head — render-blocking"
            else:
                icon, note_color, note = "🟢", "#059669", f"media={c['media']}"
            st.markdown(
                f"<div style='padding:.45rem 0;border-bottom:1px solid #e2e6ea;"
                f"font-family:IBM Plex Mono,monospace;font-size:.76rem'>"
                f"{icon} <span style='word-break:break-all;color:#111827'>{c['href']}</span>"
                f" <span style='color:{note_color};font-size:.68rem;margin-left:6px'>{note}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        audit_row("🟡", "No external stylesheets detected")

    # ── Caching & compression headers ─────────────────────────────────────────
    sh("Caching & Compression")
    for h in ["cache-control", "etag", "last-modified", "content-encoding", "vary", "server", "x-powered-by"]:
        val = hdrs.get(h, "")
        audit_row("🟢" if val else "🟡", h, val or "not set",
                  "#059669" if val else "#d97706")


# ─────────────────────────────────────────────────────────────────────────────
# ON-PAGE SEO ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

# ── Stop-words to exclude from entity extraction ─────────────────────────────
_STOP_WORDS = {
    # English articles, prepositions, conjunctions, auxiliaries, pronouns
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "shall","can","this","that","these","those","it","its","he","she","they",
    "we","you","i","my","his","her","their","our","your","who","which","what",
    "when","where","how","why","not","no","yes","also","then","than","so",
    "if","as","up","out","about","after","before","over","under","just","now",
    "more","most","other","said","says","say","new","one","two","three",
    "first","last","next","all","any","some","such","into","through",
    "during","while","since","until","per","each","both","few","many",
    "much","more","even","yet","still","back","only","well","get","got",
    "him","them","us","me","her","its","am","here","there","very","too",
    # Hindi/Urdu common words (transliterated)
    "ne","ko","ka","ki","ke","hai","hain","tha","thi","the","se","par",
    "mein","aur","ya","jo","kya","koi","yeh","woh","ek","do","teen","bhi",
    "nahi","nahin","kuch","sab","ap","aap","hum","tum","unhe","unka",
    # Common news article verbs/noise
    "told","says","said","reported","according","official","officials",
    "however","therefore","meanwhile","although","despite","following",
    "amid","regarding","related","including","added","noted","called",
    "asked","took","made","came","went","seen","given","known","used",
    "based","held","comes","goes","puts","gets","sets","led","let",
}

# Entity type badge colours
_ENTITY_COLORS = {
    "PERSON":  ("#1e40af", "#dbeafe", "Person"),
    "ORG":     ("#065f46", "#d1fae5", "Org"),
    "PLACE":   ("#92400e", "#fef3c7", "Place"),
    "EVENT":   ("#6d28d9", "#ede9fe", "Event"),
    "NUMBER":  ("#374151", "#f3f4f6", "Number/Stat"),
    "KEYWORD": ("#be123c", "#fff1f2", "Key Term"),
}

def extract_entities(text):
    """
    Rule-based NER without any external model.
    Returns a list of {"text", "type", "count", "in_title", "in_desc"} dicts,
    filtered to remove stop-words, verbs, articles, and other noise.
    Works on English, Hindi-transliterated, and mixed-script text.
    """
    if not text:
        return []

    results = {}   # normalised_text -> {text, type, count}

    # ── 1. NUMBERS & STATS ────────────────────────────────────────────────────
    # Match quantities with units: 50%, $5bn, Rs 2000 crore, 3.5 million, etc.
    num_pat = re.compile(
        r"(?:rs\.?\s*|\$|€|£|usd\s*)?\b"
        r"(\d{1,3}(?:[,.]\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)"
        r"\s*(?:crore|lakh|billion|million|trillion|thousand|hundred|"
        r"%|percent|km|kg|mt|mw|gw|bn|mn|\$|€|£)?\b",
        re.I
    )
    for m in num_pat.finditer(text):
        raw = m.group(0).strip()
        if len(raw) < 2 or re.fullmatch(r"\d", raw):  # skip single digits
            continue
        key = raw.lower()
        if key in results:
            results[key]["count"] += 1
        else:
            results[key] = {"text": raw, "type": "NUMBER", "count": 1}

    # ── 2. PROPER NOUN SEQUENCES (NNP chains) ─────────────────────────────────
    # Match 1-4 consecutive Title-Case tokens — catches names, orgs, places
    nnp_pat = re.compile(
        r"\b([A-Z][a-záéíóúäöüàèìòùãõâêîôûçñ\'\-]+"
        r"(?:\s+[A-Z][a-záéíóúäöüàèìòùãõâêîôûçñ\'\-]+){0,3})\b"
    )
    for m in nnp_pat.finditer(text):
        phrase = m.group(1).strip()
        # Skip if only stop-words
        tokens = phrase.lower().split()
        if all(t in _STOP_WORDS for t in tokens):
            continue
        if len(phrase) < 3:
            continue
        # Skip pure number phrases caught above
        if re.fullmatch(r"[\d\s.,]+", phrase):
            continue
        key = phrase.lower()
        if key in results:
            results[key]["count"] += 1
        else:
            results[key] = {"text": phrase, "type": "KEYWORD", "count": 1}

    # ── 3. CLASSIFY by known patterns ─────────────────────────────────────────
    # Place suffixes / known place names
    place_re = re.compile(
        r"\b("
        # Indian cities / regions
        r"Mumbai|Delhi|New Delhi|Chennai|Bangalore|Bengaluru|Kolkata|Hyderabad|"
        r"Pune|Ahmedabad|Surat|Jaipur|Lucknow|Kanpur|Nagpur|Patna|Bhopal|"
        r"Indore|Vadodara|Agra|Varanasi|Meerut|Noida|Gurgaon|Gurugram|"
        r"[A-Z]\w+abad|[A-Z]\w+pur|[A-Z]\w+nagar|[A-Z]\w+puram|"
        # Countries
        r"India|Pakistan|China|USA|America|Russia|Ukraine|Israel|Iran|Iraq|"
        r"Syria|Turkey|Egypt|Saudi Arabia|UAE|Qatar|Kuwait|Afghanistan|"
        r"Bangladesh|Sri Lanka|Nepal|Myanmar|Japan|Korea|Taiwan|"
        r"UK|Britain|England|France|Germany|Italy|Spain|Canada|Australia|"
        # World cities
        r"London|Paris|Berlin|Washington|New York|Beijing|Shanghai|Tokyo|"
        r"Moscow|Kyiv|Tehran|Islamabad|Kabul|Riyadh|Jerusalem|Gaza|"
        r"Dubai|Abu Dhabi|Singapore|Hong Kong|Geneva|Brussels|"
        # Seas, rivers, regions
        r"Hormuz|Strait of Hormuz|Red Sea|Arabian Sea|Indian Ocean|"
        r"Kashmir|Punjab|Gujarat|Maharashtra|Rajasthan|Uttar Pradesh|"
        r"Bihar|Jharkhand|Odisha|Assam|West Bengal|Tamil Nadu|Kerala"
        r")\b", re.I
    )
    for m in place_re.finditer(text):
        phrase = m.group(1)
        key = phrase.lower()
        if key in results:
            results[key]["type"] = "PLACE"
        else:
            results[key] = {"text": phrase, "type": "PLACE", "count": 1}

    # Event / topic keywords
    event_re = re.compile(
        r"\b("
        r"election|elections|referendum|coup|war|ceasefire|peace talks|"
        r"summit|G20|G7|BRICS|NATO|UN|United Nations|"
        r"IPL|World Cup|Olympics|T20|ODI|Test match|Grand Prix|"
        r"budget|GDP|inflation|recession|interest rate|repo rate|"
        r"earthquake|flood|cyclone|tsunami|disaster|accident|crash|explosion|"
        r"arrest|verdict|trial|hearing|judgment|bail|conviction|acquittal|"
        r"launch|inauguration|protest|strike|shutdown|bandh|rally|"
        r"nuclear|missile|airstrike|attack|bombing|ceasefire|sanction|"
        r"merger|acquisition|IPO|funding|bankruptcy|layoff|"
        r"pandemic|outbreak|vaccine|virus|COVID"
        r")\b", re.I
    )
    for m in event_re.finditer(text):
        phrase = m.group(1)
        key = phrase.lower()
        if key in results:
            results[key]["type"] = "EVENT"
        else:
            results[key] = {"text": phrase, "type": "EVENT", "count": 1}

    # Organisation indicators
    org_re = re.compile(
        r"\b("
        r"BJP|Congress|AAP|SP|BSP|TMC|NDA|UPA|INDIA alliance|"
        r"Supreme Court|High Court|CBI|ED|NIA|RAW|IB|SEBI|RBI|"
        r"ISRO|DRDO|HAL|ONGC|NTPC|BHEL|"
        r"NASA|FBI|CIA|Pentagon|White House|Kremlin|"
        r"UN|WHO|IMF|World Bank|WTO|OPEC|"
        r"Google|Meta|Apple|Microsoft|Amazon|Tesla|OpenAI|Anthropic|"
        r"Tata|Reliance|Adani|Ambani|Infosys|Wipro|TCS|"
        r"Army|Navy|Air Force|Police|CRPF|BSF|ITBP|NSG"
        r")\b", re.I
    )
    for m in org_re.finditer(text):
        phrase = m.group(1)
        key = phrase.lower()
        if key in results:
            results[key]["type"] = "ORG"
        else:
            results[key] = {"text": phrase, "type": "ORG", "count": 1}

    # ── 4. Post-filter: remove stop-words and noisy single tokens ─────────────
    filtered = []
    for key, item in results.items():
        tokens = item["text"].lower().split()
        # Remove if ALL tokens are stop-words
        if all(t in _STOP_WORDS for t in tokens):
            continue
        # Remove very short single-token entries unless they are numbers/orgs/places
        if len(tokens) == 1 and len(item["text"]) <= 3 and item["type"] == "KEYWORD":
            continue
        # Remove entries that are just common adjectives / past-tense verbs
        if item["type"] == "KEYWORD" and len(tokens) == 1:
            w = tokens[0]
            if w.endswith(("ing", "tion", "ed", "ly", "ous", "ful", "ive", "ble")):
                # Only keep if it appeared 2+ times (suggests topical importance)
                if item["count"] < 2:
                    continue
        filtered.append(item)

    # ── 5. Sort: type priority then frequency ────────────────────────────────
    type_order = {"PLACE": 0, "PERSON": 1, "ORG": 2, "EVENT": 3, "NUMBER": 4, "KEYWORD": 5}
    filtered.sort(key=lambda x: (type_order.get(x["type"], 9), -x["count"]))

    return filtered[:40]   # cap at 40 entities


def analyze_onpage(url, results):
    """Deep on-page SEO analysis with entity, AEO, Google preview."""
    s = results.get("sections", {})
    meta = s.get("meta", {})
    headings = s.get("headings", {})
    content = s.get("content", {})
    imgs = s.get("images", [])
    links_data = s.get("links", {})

    title = meta.get("title", "")
    description = meta.get("description", "")
    h1s = headings.get("h1", [])
    h1 = h1s[0] if h1s else ""

    # ── Title vs H1 comparison ─────────────────────────────────────────────
    title_words = set(re.findall(r"\b\w{3,}\b", title.lower()))
    h1_words = set(re.findall(r"\b\w{3,}\b", h1.lower()))
    overlap = title_words & h1_words
    title_h1_same = title.strip().lower() == h1.strip().lower()
    title_h1_overlap_pct = round(len(overlap) / max(len(title_words | h1_words), 1) * 100)

    # ── Entity extraction from title + description + H1 ──────────────────
    full_text = title + " " + description + " " + " ".join(h1s)
    # Also pull article-body entities already computed
    article_entities = s.get("content", {}).get("article_entities", [])
    meta_entities    = extract_entities(full_text)

    # Merge: article entities provide context, meta entities show what's in title/desc
    # Build a unified list keyed by lower-text, preferring article entity types
    merged = {}
    for ent in article_entities + meta_entities:
        key = ent["text"].lower()
        if key not in merged:
            merged[key] = dict(ent)
        else:
            merged[key]["count"] += ent["count"]
    entities = sorted(merged.values(),
                      key=lambda x: ({"PLACE":0,"ORG":1,"EVENT":2,"NUMBER":3,"KEYWORD":4}.get(x["type"],5),
                                     -x["count"]))[:35]

    # Presence check: is each entity mentioned in title / description?
    for ent in entities:
        ent["in_title"] = ent["text"].lower() in title.lower()
        ent["in_desc"]  = ent["text"].lower() in description.lower()
        ent["in_h1"]    = ent["text"].lower() in h1.lower()

    # ── AEO checks (Answer Engine Optimization) ────────────────────────────
    sd = s.get("structured_data", [])
    sd_types = [item.get("@type", "") for item in sd if isinstance(item, dict)]
    aeo_signals = {
        "has_faq_schema": any("FAQ" in t for t in sd_types),
        "has_howto_schema": any("HowTo" in t for t in sd_types),
        "has_article_schema": any(t in ("Article", "NewsArticle", "BlogPosting") for t in sd_types),
        "has_speakable": any("speakable" in str(item) for item in sd),
        "has_qa_schema": any("QAPage" in t for t in sd_types),
        "has_definition_list": False,  # checked below from soup — placeholder
        "description_is_question_answer": bool(
            re.search(r"(what|how|why|when|where|who)\b.{5,}\?", description, re.I)
        ),
        "title_has_question": bool(re.search(r"\?", title)),
        "has_table_of_contents": False,
    }

    # ── Image filename audit ───────────────────────────────────────────────
    generic_imgs = [i for i in imgs if i.get("is_generic_name")]
    stock_imgs = [i for i in imgs if i.get("is_stock")]
    whatsapp_imgs = [i for i in imgs if i.get("is_whatsapp")]

    # ── Heading audit ──────────────────────────────────────────────────────
    heading_audit = []
    for level in range(1, 7):
        for txt in headings.get(f"h{level}", []):
            heading_audit.append({
                "level": level, "text": txt,
                "length": len(txt),
                "too_long": len(txt) > 70,
                "too_short": len(txt) < 5,
                "has_keyword": any(ent["text"].lower() in txt.lower() for ent in entities[:5]),
            })

    # ── Internal link audit ────────────────────────────────────────────────
    int_links = links_data.get("internal", [])
    ext_links = links_data.get("external", [])

    return {
        "title": title,
        "description": description,
        "h1": h1,
        "h1s": h1s,
        "title_h1_same": title_h1_same,
        "title_h1_overlap_pct": title_h1_overlap_pct,
        "title_h1_shared_words": list(overlap),
        "entities": entities,
        "aeo_signals": aeo_signals,
        "sd_types": sd_types,
        "generic_imgs": generic_imgs,
        "stock_imgs": stock_imgs,
        "whatsapp_imgs": whatsapp_imgs,
        "heading_audit": heading_audit,
        "word_count": content.get("word_count", 0),
        "internal_link_count": len(int_links),
        "external_link_count": len(ext_links),
    }


def fetch_pagespeed(url):
    """Call PageSpeed Insights API (free, no key needed for basic use) — LAB data only."""
    api_url = (
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={requests.utils.quote(url, safe='')}"
        "&strategy=mobile&category=performance"
    )
    try:
        resp = requests.get(api_url, timeout=30)
        if resp.status_code != 200:
            return {"error": f"API returned HTTP {resp.status_code}"}
        data = resp.json()
        lhr = data.get("lighthouseResult", {})
        cats = lhr.get("categories", {})
        audits = lhr.get("audits", {})
        perf_score = int((cats.get("performance", {}).get("score", 0) or 0) * 100)

        def av(key):
            a = audits.get(key, {})
            return a.get("displayValue", "—"), a.get("score", None), a.get("description", "")

        metrics = {
            "performance_score": perf_score,
            "fcp":  av("first-contentful-paint"),
            "lcp":  av("largest-contentful-paint"),
            "tbt":  av("total-blocking-time"),
            "cls":  av("cumulative-layout-shift"),
            "si":   av("speed-index"),
            "tti":  av("interactive"),
        }
        # Opportunities
        opportunities = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity":
                savings = audit.get("details", {}).get("overallSavingsMs", 0)
                if savings and savings > 100:
                    opportunities.append({
                        "title": audit.get("title", key),
                        "savings_ms": round(savings),
                        "score": audit.get("score"),
                        "description": audit.get("description", "")[:200],
                    })
        opportunities.sort(key=lambda x: x["savings_ms"], reverse=True)
        metrics["opportunities"] = opportunities[:8]
        metrics["psi_url"] = (
            "https://pagespeed.web.dev/report?url="
            + requests.utils.quote(url, safe="")
        )
        return metrics
    except Exception as e:
        return {"error": str(e)[:200]}


def fetch_similar_articles(url, title, description):
    """
    Find similar articles using:
    1. Google related: search scrape
    2. DuckDuckGo HTML search (more reliable, no JS)
    Both are free / open-source approaches.
    """
    results_list = []
    parsed = urlparse(url)
    domain = parsed.netloc

    # Build a focused query from title
    query_words = re.findall(r"\b[a-zA-Z]{4,}\b", title)[:8]
    query = " ".join(query_words[:6])

    # ── DuckDuckGo HTML search (most reliable scrape) ──────────────────────
    try:
        ddg_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(ddg_url, headers=headers, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for result in soup.select(".result")[:12]:
                title_el = result.select_one(".result__title a") or result.select_one("a.result__a")
                snippet_el = result.select_one(".result__snippet")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                # DDG wraps URLs — extract actual URL
                if "uddg=" in href:
                    from urllib.parse import parse_qs, urlparse as up2
                    qs = parse_qs(up2(href).query)
                    href = qs.get("uddg", [href])[0]
                r_domain = urlparse(href).netloc
                if r_domain == domain:
                    continue  # skip same domain
                result_title = title_el.get_text(strip=True)
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                if result_title and href.startswith("http"):
                    results_list.append({
                        "title": result_title,
                        "url": href,
                        "domain": r_domain,
                        "snippet": snippet[:200],
                        "source": "DuckDuckGo",
                    })
    except Exception as e:
        pass

    # ── Google related: scrape as fallback ────────────────────────────────
    if len(results_list) < 4:
        try:
            g_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=10"
            headers_g = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
            gr = requests.get(g_url, headers=headers_g, timeout=12)
            if gr.status_code == 200:
                gsoup = BeautifulSoup(gr.text, "html.parser")
                for div in gsoup.select("div.g, div[data-sokoban-container]")[:10]:
                    a_tag = div.select_one("a[href^='http']")
                    h3 = div.select_one("h3")
                    snippet_el = div.select_one(".VwiC3b, span[class*='snippet']")
                    if not a_tag or not h3:
                        continue
                    href = a_tag.get("href", "")
                    r_domain = urlparse(href).netloc
                    if r_domain == domain:
                        continue
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    results_list.append({
                        "title": h3.get_text(strip=True),
                        "url": href,
                        "domain": r_domain,
                        "snippet": snippet[:200],
                        "source": "Google",
                    })
        except Exception:
            pass

    # Deduplicate by domain
    seen_domains = set()
    unique = []
    for item in results_list:
        if item["domain"] not in seen_domains:
            seen_domains.add(item["domain"])
            unique.append(item)
    return unique[:10]


def render_onpage_tab(url, results):
    """Render the full On-Page SEO tab."""
    onpage = analyze_onpage(url, results)
    title = onpage["title"]
    description = onpage["description"]
    h1 = onpage["h1"]

    # ── 1. SERP GOOGLE PREVIEW ────────────────────────────────────────────
    sh("Google SERP Preview")
    parsed = urlparse(url)
    breadcrumb = f"{parsed.netloc} › {' › '.join([p for p in parsed.path.split('/') if p])}"
    display_title = title[:60] + ("..." if len(title) > 60 else "")
    display_desc = description[:160] + ("..." if len(description) > 160 else "")
    title_color = "#1a0dab" if len(title) <= 60 else "#d93025"
    st.markdown(f"""
    <div style='background:#ffffff;border:1px solid #dfe1e5;border-radius:8px;
                padding:1.25rem 1.5rem;max-width:600px;font-family:Arial,sans-serif'>
      <div style='font-size:13px;color:#202124;margin-bottom:2px'>{breadcrumb}</div>
      <div style='font-size:20px;color:{title_color};margin-bottom:4px;
                  line-height:1.3;font-weight:400'>{display_title or "<em style='color:#777'>No title</em>"}</div>
      <div style='font-size:14px;color:#3c4043;line-height:1.6'>
        {display_desc or "<em style='color:#777'>No meta description — Google will auto-generate a snippet.</em>"}
      </div>
    </div>
    <div style='margin-top:.5rem;font-family:IBM Plex Mono,monospace;font-size:.72rem;color:#6b7280'>
      Title: <span style='color:{"#059669" if 50<=len(title)<=60 else "#d97706" if 30<=len(title)<50 else "#dc2626"}'>{len(title)} chars</span>
      &nbsp;|&nbsp; Description: <span style='color:{"#059669" if 120<=len(description)<=160 else "#d97706" if 70<=len(description)<120 else "#dc2626"}'>{len(description)} chars</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. BASIC SEO RULES ────────────────────────────────────────────────
    sh("Basic SEO Rules")
    rules = [
        # (pass?, label, detail)
        (50 <= len(title) <= 60,
         f"Title length: {len(title)} chars",
         "Ideal: 50–60 chars. Longer titles get truncated in SERPs."),
        (120 <= len(description) <= 160,
         f"Description length: {len(description)} chars",
         "Ideal: 120–160 chars. Too short wastes space; too long gets cut."),
        (bool(h1),
         "H1 tag present",
         "Every page needs exactly one H1 tag."),
        (not onpage["title_h1_same"],
         "Title ≠ H1 (good — they should differ)",
         "Title and H1 serve different purposes. Title is for SERPs; H1 is for page context."),
        (onpage["title_h1_overlap_pct"] >= 40 and not onpage["title_h1_same"],
         f"Title/H1 share {onpage['title_h1_overlap_pct']}% keywords (ideal 40–80%)",
         "Title and H1 should share core keywords but not be identical."),
        (bool(results.get("sections", {}).get("meta", {}).get("canonical")),
         "Canonical URL set",
         "Prevents duplicate content issues."),
        (bool(results.get("sections", {}).get("meta", {}).get("og", {}).get("og:image")),
         "OG image present",
         "Required for rich social media previews."),
        (onpage["word_count"] >= 300,
         f"Word count: {onpage['word_count']} words",
         "Minimum 300 words for indexable content."),
        (onpage["internal_link_count"] >= 3,
         f"Internal links in article body: {onpage['internal_link_count']}",
         "At least 3–5 internal links within article paragraphs for good crawlability."),
    ]
    for passes, label, detail in rules:
        icon = "🟢" if passes else "🔴"
        color = "#059669" if passes else "#dc2626"
        audit_row(icon, label, detail, color)

    # ── 3. TITLE vs H1 ────────────────────────────────────────────────────
    sh("Title vs H1 Comparison")
    c1, c2 = st.columns(2)
    _title_display = title if title else "<em style='color:#6b7280'>missing</em>"
    _h1_display = h1 if h1 else "<em style='color:#6b7280'>missing</em>"
    with c1:
        st.markdown(
            f"<div style='background:#f1f3f6;border:1px solid #e2e6ea;"
            f"border-radius:6px;padding:.75rem 1rem'>"
            f"<div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;"
            f"letter-spacing:2px;margin-bottom:.4rem'>Title Tag</div>"
            f"<div style='font-family:IBM Plex Mono,monospace;font-size:.82rem;"
            f"color:#111827'>{_title_display}</div>"
            f"<div style='font-size:.7rem;color:#6b7280;margin-top:.3rem'>{len(title)} chars</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div style='background:#f1f3f6;border:1px solid #e2e6ea;"
            f"border-radius:6px;padding:.75rem 1rem'>"
            f"<div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;"
            f"letter-spacing:2px;margin-bottom:.4rem'>H1 Tag</div>"
            f"<div style='font-family:IBM Plex Mono,monospace;font-size:.82rem;"
            f"color:#111827'>{_h1_display}</div>"
            f"<div style='font-size:.7rem;color:#6b7280;margin-top:.3rem'>{len(h1)} chars</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    if onpage["title_h1_same"]:
        st.markdown(
            "<div style='background:rgba(255,170,0,.1);border:1px solid rgba(255,170,0,.3);"
            "border-radius:4px;padding:.5rem .75rem;margin-top:.5rem;"
            "font-size:.82rem;color:#d97706'>⚠ Title and H1 are identical. Differentiate them — "
            "the Title should target SERP click-through; H1 should describe the page to the reader.</div>",
            unsafe_allow_html=True
        )
    if onpage["title_h1_shared_words"]:
        st.markdown(
            f"<div style='font-size:.76rem;color:#6b7280;margin-top:.4rem;"
            f"font-family:IBM Plex Mono,monospace'>"
            f"Shared keywords: {', '.join(onpage['title_h1_shared_words'][:10])}</div>",
            unsafe_allow_html=True
        )

    # ── 4. ALL HEADINGS ───────────────────────────────────────────────────
    sh("Heading Structure Detail")
    if onpage["heading_audit"]:
        for h in onpage["heading_audit"]:
            warn_flags = []
            if h["too_long"]: warn_flags.append("too long >70 chars")
            if h["too_short"]: warn_flags.append("too short")
            status_icon = "🟢" if not warn_flags else "🟡"
            color = ("#059669" if h["level"] == 1 else
                     "#1d4ed8" if h["level"] == 2 else
                     "#d97706" if h["level"] == 3 else "var(--muted)")
            indent = "&nbsp;" * (h["level"] - 1) * 4
            flag_html = "".join(
                f"<span style='background:#fffbeb;color:#d97706;"
                f"font-size:.65rem;padding:1px 5px;border-radius:3px;margin-left:6px'>{f}</span>"
                for f in warn_flags
            )
            kw_badge = (
                "<span style='background:#ecfdf5;color:#059669;"
                "font-size:.65rem;padding:1px 5px;border-radius:3px;margin-left:4px'>has keyword</span>"
                if h["has_keyword"] else ""
            )
            st.markdown(
                f"<div style='padding:.35rem 0;border-bottom:1px solid #e2e6ea'>"
                f"<span style='font-family:IBM Plex Mono,monospace;color:{color};"
                f"font-size:.68rem;font-weight:600;margin-right:6px'>{indent}H{h['level']}</span>"
                f"<span style='font-size:.84rem;color:#111827'>{h['text'][:120]}</span>"
                f"{flag_html}{kw_badge}"
                f"<span style='font-size:.68rem;color:#6b7280;margin-left:8px'>{h['length']} chars</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        audit_row("🔴", "No headings found on page")

    # ── 5. IMAGE FILENAME AUDIT ───────────────────────────────────────────
    sh("Image Filename & Quality Audit")
    imgs = results.get("sections", {}).get("images", [])
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Total Images", str(len(imgs)))
    with c2: metric("Generic Names", str(len(onpage["generic_imgs"])),
                    "#059669" if not onpage["generic_imgs"] else "#dc2626")
    with c3: metric("Stock/Getty", str(len(onpage["stock_imgs"])),
                    "#059669" if not onpage["stock_imgs"] else "#d97706")
    with c4: metric("WhatsApp Images", str(len(onpage["whatsapp_imgs"])),
                    "#059669" if not onpage["whatsapp_imgs"] else "#dc2626")

    if onpage["whatsapp_imgs"]:
        st.markdown(
            "<div style='background:#fef2f2;border:1px solid #fecaca;"
            "border-radius:5px;padding:.65rem .9rem;margin:.5rem 0'>"
            "<div style='color:#dc2626;font-weight:600;font-size:.84rem;margin-bottom:.3rem'>"
            "🔴 WhatsApp images detected — serious SEO issue</div>"
            "<div style='font-size:.78rem;color:#6b7280'>WhatsApp images have generic filenames, "
            "are often low-resolution, and signal low-quality content to Google. "
            "Replace with original, properly named images.</div></div>",
            unsafe_allow_html=True
        )

    all_img_issues = [i for i in imgs if i.get("is_generic_name") or i.get("is_stock") or i.get("is_whatsapp")]
    if all_img_issues:
        with st.expander(f"Images with filename issues ({len(all_img_issues)})", expanded=True):
            for img in all_img_issues[:30]:
                flags = []
                if img.get("is_whatsapp"):   flags.append(("🔴", "WhatsApp", "#dc2626"))
                elif img.get("is_stock"):    flags.append(("🟡", "Stock image", "#d97706"))
                elif img.get("is_generic_name"): flags.append(("🟡", "Generic name", "#d97706"))
                badges = "".join(
                    f"<span style='background:rgba(0,0,0,.2);color:{c};"
                    f"font-size:.65rem;padding:1px 5px;border-radius:3px;margin-right:4px'>{i} {l}</span>"
                    for i, l, c in flags
                )
                st.markdown(
                    f"<div style='padding:.4rem 0;border-bottom:1px solid #e2e6ea'>"
                    f"<div style='font-family:IBM Plex Mono,monospace;font-size:.76rem'>"
                    f"{badges}"
                    f"<span style='color:#6b7280'>filename: </span>"
                    f"<span style='color:#111827'>{img.get('filename','?')}</span></div>"
                    f"<div style='font-family:IBM Plex Mono,monospace;font-size:.68rem;"
                    f"color:#6b7280;word-break:break-all;margin-top:2px'>{img['src'][:100]}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # All images table
    with st.expander(f"All Images ({len(imgs)})", expanded=False):
        if imgs:
            df = pd.DataFrame([{
                "filename": i.get("filename", "?")[:40],
                "alt": (i.get("alt") or "")[:50] or ("⚠ empty" if i.get("has_alt") else "✗ missing"),
                "generic?": "⚠ yes" if i.get("is_generic_name") else "✓ no",
                "whatsapp?": "🔴 yes" if i.get("is_whatsapp") else "—",
                "stock?": "⚠ yes" if i.get("is_stock") else "—",
                "lazy": "✓" if i.get("lazy") else "—",
                "dims": "✓" if (i.get("width") and i.get("height")) else "—",
            } for i in imgs[:60]])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── 6. KEYWORD / ENTITY PRESENCE ─────────────────────────────────────
    sh("Key Entities — People, Places, Orgs, Events, Numbers")
    entities = onpage["entities"]

    if not entities:
        st.markdown(
            "<div style='color:#6b7280;font-size:.84rem'>No significant entities detected.</div>",
            unsafe_allow_html=True
        )
    else:
        # Group by type for display
        type_order = ["PLACE", "ORG", "EVENT", "NUMBER", "KEYWORD"]
        grouped = {}
        for ent in entities:
            t = ent["type"]
            grouped.setdefault(t, []).append(ent)

        # Header row
        st.markdown(
            "<div style='display:grid;grid-template-columns:1fr 80px 80px 80px 80px;"
            "gap:6px;padding:.4rem .5rem;background:#f1f3f6;border-radius:6px;"
            "font-size:.68rem;font-weight:600;color:#6b7280;margin-bottom:4px'>"
            "<div>Entity</div><div>In Title</div><div>In Desc</div>"
            "<div>In H1</div><div>Mentions</div></div>",
            unsafe_allow_html=True
        )

        for etype in type_order:
            ents = grouped.get(etype, [])
            if not ents:
                continue
            cfg = _ENTITY_COLORS.get(etype, ("#374151", "#f3f4f6", etype))
            text_color, bg_color, label = cfg

            for ent in ents[:12]:
                in_t  = ent.get("in_title", False)
                in_d  = ent.get("in_desc",  False)
                in_h1 = ent.get("in_h1",    False)

                def tick(val):
                    return (f"<span style='color:#059669;font-weight:600'>✓</span>"
                            if val else
                            f"<span style='color:#d1d5db'>—</span>")

                type_badge = (
                    f"<span style='background:{bg_color};color:{text_color};"
                    f"font-size:.62rem;padding:1px 5px;border-radius:3px;"
                    f"font-weight:600;margin-right:6px'>{label}</span>"
                )
                st.markdown(
                    f"<div style='display:grid;grid-template-columns:1fr 80px 80px 80px 80px;"
                    f"gap:6px;padding:.35rem .5rem;border-bottom:1px solid #f1f3f6;"
                    f"align-items:center;font-size:.82rem'>"
                    f"<div style='color:#111827'>{type_badge}{ent['text']}</div>"
                    f"<div style='text-align:center'>{tick(in_t)}</div>"
                    f"<div style='text-align:center'>{tick(in_d)}</div>"
                    f"<div style='text-align:center'>{tick(in_h1)}</div>"
                    f"<div style='text-align:center;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.75rem;color:#6b7280'>{ent['count']}×</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Coverage hint
        missing_from_title = [e for e in entities
                               if not e.get("in_title") and e["type"] in ("PLACE","ORG","EVENT")]
        if missing_from_title:
            missing_labels = ", ".join(e["text"] for e in missing_from_title[:4])
            st.markdown(
                f"<div style='background:#fffbeb;border:1px solid #fde68a;"
                f"border-radius:6px;padding:.55rem .85rem;margin-top:.6rem;"
                f"font-size:.8rem;color:#92400e'>"
                f"<strong>Tip:</strong> Key entities not in title: "
                f"<em>{missing_labels}</em>. "
                f"Including the primary place/org/event in the title improves "
                f"relevance signals and AI Overview citation likelihood.</div>",
                unsafe_allow_html=True
            )

    # ── 7. AEO OPTIMIZATION ───────────────────────────────────────────────
    sh("AEO — Answer Engine Optimization (AI Overview / Voice / Featured Snippets)")
    aeo = onpage["aeo_signals"]
    aeo_checks = [
        (aeo["has_faq_schema"],       "FAQ Schema (FAQPage JSON-LD)",
         "Enables FAQ rich results. Google and AI Overviews extract Q&A pairs directly.",
         "Add FAQPage schema with at least 3 questions relevant to the article topic."),
        (aeo["has_howto_schema"],     "HowTo Schema",
         "Enables step-by-step rich results for instructional content.",
         "Add HowTo schema if this page contains step-by-step instructions."),
        (aeo["has_article_schema"],   "Article / NewsArticle Schema",
         "Signals to Google that this is editorial content, improves freshness signals.",
         "Add NewsArticle or Article JSON-LD with author, datePublished, dateModified."),
        (aeo["has_speakable"],        "Speakable Schema",
         "Marks content suitable for voice assistants (Google Assistant).",
         "Add speakable property to your Article schema pointing to the key paragraphs."),
        (aeo["has_qa_schema"],        "QAPage Schema",
         "Enables Q&A rich results for community/forum-style content.",
         "Add QAPage schema if the page has community answers."),
        (aeo["description_is_question_answer"],
         "Meta description answers a question",
         "Descriptions phrased as direct answers have higher featured snippet potential.",
         "Rewrite description to directly answer the primary question: 'What is X? X is...'"),
        (aeo["title_has_question"],   "Title contains a question",
         "Question-format titles attract featured snippets and AI Overview citations.",
         "Consider adding a question format: 'What is...', 'How to...', 'Why...'"),
    ]
    for passes, label, detail, fix in aeo_checks:
        icon = "🟢" if passes else "🟡"
        color = "#059669" if passes else "#d97706"
        with st.expander(f"{icon} {label}", expanded=not passes):
            st.markdown(
                f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.4rem'>{detail}</div>",
                unsafe_allow_html=True
            )
            if not passes:
                st.markdown(
                    f"<div style='background:#fffbeb;border:1px solid #fde68a;"
                    f"border-radius:4px;padding:.5rem .75rem;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.76rem;color:#d97706'><b>Recommendation: </b>{fix}</div>",
                    unsafe_allow_html=True
                )

    # AEO score summary
    aeo_score = sum(1 for p, *_ in aeo_checks if p)
    aeo_pct = round(aeo_score / len(aeo_checks) * 100)
    st.markdown(
        f"<div style='margin-top:.75rem;font-family:IBM Plex Mono,monospace;font-size:.78rem;"
        f"color:#6b7280'>AEO Readiness: "
        f"<span style='color:{'#059669' if aeo_pct>=70 else '#d97706' if aeo_pct>=40 else '#dc2626'}'>"
        f"{aeo_score}/{len(aeo_checks)} signals ({aeo_pct}%)</span></div>",
        unsafe_allow_html=True
    )


def render_pagespeed_tab(url):
    """Render PageSpeed Insights LAB data tab."""
    sh("PageSpeed Insights — LAB Data (Mobile)")
    psi_url_link = "https://pagespeed.web.dev/report?url=" + requests.utils.quote(url, safe="")
    st.markdown(
        f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.75rem'>"
        f"Free Google Lighthouse LAB data (mobile). "
        f"<a href='{psi_url_link}' target='_blank' style='color:var(--accent)'>Open full report ↗</a>"
        f"</div>",
        unsafe_allow_html=True
    )
    with st.spinner("Calling PageSpeed Insights API…"):
        psi = fetch_pagespeed(url)

    if "error" in psi:
        st.markdown(
            f"<div style='background:#fffbeb;border:1px solid #fde68a;border-radius:8px;"
            f"padding:.75rem 1rem;font-size:.82rem;color:#92400e'>"
            f"⚠ PageSpeed API unavailable ({psi['error'][:80]}). "
            f"<a href='{psi_url_link}' target='_blank' style='color:#1d4ed8;font-weight:600'>"
            f"Run the test directly on PageSpeed.web.dev ↗</a></div>",
            unsafe_allow_html=True
        )
        return

    # Score card
    ps = psi["performance_score"]
    ps_color = "#059669" if ps >= 90 else "#d97706" if ps >= 50 else "#dc2626"
    st.markdown(
        f"<div style='background:#ffffff;border:2px solid {ps_color}33;"
        f"border-left:4px solid {ps_color};border-radius:8px;"
        f"padding:1rem 1.5rem;margin-bottom:1.25rem;display:flex;align-items:center;gap:1.5rem'>"
        f"<div style='font-family:IBM Plex Mono,monospace;font-size:2.5rem;font-weight:600;color:{ps_color}'>{ps}</div>"
        f"<div><div style='font-weight:700;font-size:.9rem'>Performance Score (Mobile)</div>"
        f"<div style='font-size:.78rem;color:#6b7280'>0–49 Poor · 50–89 Needs Improvement · 90–100 Good</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    # Core Web Vitals
    sh("Core Web Vitals (LAB)")
    cwv = [
        ("LCP", psi["lcp"], "Largest Contentful Paint — loading performance. Good: <2.5s"),
        ("FCP", psi["fcp"], "First Contentful Paint — time to first content. Good: <1.8s"),
        ("TBT", psi["tbt"], "Total Blocking Time — interactivity proxy. Good: <200ms"),
        ("CLS", psi["cls"], "Cumulative Layout Shift — visual stability. Good: <0.1"),
        ("SI",  psi["si"],  "Speed Index — how quickly content is visually populated. Good: <3.4s"),
        ("TTI", psi["tti"], "Time to Interactive — fully interactive. Good: <3.8s"),
    ]
    cols = st.columns(3)
    for i, (name, (value, score, desc), tip) in enumerate(cwv):
        col_color = ("#059669" if score is not None and score >= 0.9
                     else "#d97706" if score is not None and score >= 0.5
                     else "#dc2626")
        with cols[i % 3]:
            st.markdown(
                f"<div style='background:#ffffff;border:1px solid #e2e6ea;"
                f"border-radius:6px;padding:.75rem 1rem;margin-bottom:.5rem'>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:.65rem;"
                f"color:#6b7280;text-transform:uppercase;letter-spacing:2px'>{name}</div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:1.3rem;"
                f"font-weight:600;color:{col_color};margin:.2rem 0'>{value}</div>"
                f"<div style='font-size:.7rem;color:#6b7280'>{tip}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Opportunities
    if psi.get("opportunities"):
        sh("Top Optimization Opportunities")
        for opp in psi["opportunities"]:
            opp_color = "#dc2626" if opp["savings_ms"] > 1000 else "#d97706"
            with st.expander(f"⚡ {opp['title']} — saves ~{opp['savings_ms']} ms"):
                st.markdown(
                    f"<div style='font-size:.82rem;color:#6b7280'>{opp['description']}</div>",
                    unsafe_allow_html=True
                )

    # Link to full report
    st.markdown(
        f"<div style='margin-top:1rem'>"
        f"<a href='{psi['psi_url']}' target='_blank' "
        f"style='background:#f1f3f6;border:1px solid #e2e6ea;border-radius:4px;"
        f"padding:.5rem 1rem;font-family:IBM Plex Mono,monospace;font-size:.76rem;"
        f"color:var(--accent);text-decoration:none'>📊 View full PageSpeed report ↗</a></div>",
        unsafe_allow_html=True
    )


def render_similar_articles_tab(url, results):
    """Find and render similar articles."""
    meta = results.get("sections", {}).get("meta", {})
    title = meta.get("title", "")
    description = meta.get("description", "")

    if not title:
        st.warning("No title found — cannot search for similar articles.")
        return

    sh("Similar Articles in Search Results")
    st.markdown(
        "<div style='font-size:.8rem;color:#6b7280;margin-bottom:1rem'>"
        "Finding similar articles via DuckDuckGo and Google (free, no API key). "
        "These are pages competing for the same topic.</div>",
        unsafe_allow_html=True
    )

    with st.spinner("Searching for similar articles…"):
        similar = fetch_similar_articles(url, title, description)

    if not similar:
        st.info("No similar articles found. Try checking manually with the query below.")
    else:
        for i, art in enumerate(similar):
            source_badge = (
                "<span style='background:#ecfdf5;color:#059669;"
                "font-size:.65rem;padding:1px 5px;border-radius:3px;margin-left:6px'>"
                f"{art['source']}</span>"
            )
            st.markdown(
                f"<div style='background:#ffffff;border:1px solid #e2e6ea;"
                f"border-radius:6px;padding:.75rem 1rem;margin-bottom:.5rem'>"
                f"<div style='font-size:.88rem;font-weight:600;color:#1d4ed8;margin-bottom:.2rem'>"
                f"<a href='{art['url']}' target='_blank' "
                f"style='color:#1d4ed8;text-decoration:none'>{art['title']}</a> {source_badge}</div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:.7rem;"
                f"color:#6b7280;margin-bottom:.3rem'>{art['domain']}</div>"
                f"<div style='font-size:.78rem;color:#6b7280'>{art['snippet']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Search query used
    query_words = re.findall(r"\b[a-zA-Z]{4,}\b", title)[:6]
    query = " ".join(query_words)
    ddg_link = f"https://duckduckgo.com/?q={requests.utils.quote(query)}"
    google_link = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    st.markdown(
        f"<div style='margin-top:.75rem;font-size:.76rem;font-family:IBM Plex Mono,monospace;"
        f"color:#6b7280'>Query used: <code>{query}</code> &nbsp;"
        f"<a href='{ddg_link}' target='_blank' style='color:var(--accent);margin-right:12px'>"
        f"Search DuckDuckGo ↗</a>"
        f"<a href='{google_link}' target='_blank' style='color:var(--accent)'>Search Google ↗</a>"
        f"</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero'>
  <div class='hero-badge'>Free SEO Tool</div>
  <div class='hero-title'>SEO Analysis</div>
  <div class='hero-sub'>Comprehensive on-page, technical & indexing audit — no API key needed</div>
</div>
""", unsafe_allow_html=True)

col_i, col_b = st.columns([5, 1])
with col_i:
    url_input = st.text_input("", placeholder="https://example.com/page-to-audit",
                              label_visibility="collapsed")
with col_b:
    st.markdown("<div style='padding-top:.35rem'></div>", unsafe_allow_html=True)
    run = st.button("Analyze →")

st.markdown("---")

if run and url_input:
    url = url_input.strip()
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Crawling page…"):
        prog = st.progress(0)
        prog.progress(15)
        results = analyze_page(url)
        prog.progress(75)
        score, issues = compute_score(results)
        prog.progress(100)
        prog.empty()

    if results.get("fetch_error"):
        st.error(f"❌ {results['fetch_error']}")
        st.stop()

    s = results.get("sections", {})
    fails = [i for i in issues if i["severity"] == "fail"]
    warns = [i for i in issues if i["severity"] == "warn"]

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric("SEO Score", f"{score}/100",
               "#059669" if score >= 80 else "#d97706" if score >= 60 else "#dc2626")
    with c2:
        sc = results.get("status_code", "—")
        metric("HTTP Status", str(sc), "#059669" if sc == 200 else "#dc2626")
    with c3:
        metric("TTFB", f"{results.get('ttfb_ms', 0)} ms",
               "#059669" if results.get("ttfb_ms", 0) < 200
               else "#d97706" if results.get("ttfb_ms", 0) < 600 else "#dc2626")
    with c4:
        metric("HTML Size", f"{s.get('performance', {}).get('html_size_kb', '—')} KB")
    with c5:
        metric("Critical", str(len(fails)), "#059669" if not fails else "#dc2626")
    with c6:
        metric("Warnings", str(len(warns)), "#059669" if not warns else "#d97706")

    st.markdown("---")

    tabs = st.tabs([
        "🎯 Issues",        # 0
        "📝 On-Page SEO",   # 1
        "📄 Meta",          # 2
        "📐 Structure",     # 3
        "🖼 Images",        # 4
        "🔗 Links",         # 5
        "⚡ Performance",   # 6
        "🛡 Security",      # 7
        "🔎 Indexing",      # 8
        "🔍 Similar",       # 9
        "🔧 Raw"            # 10
    ])

    # ── TAB 0: ISSUES ─────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(
            "<div style='font-size:.82rem;color:#6b7280;margin-bottom:1rem'>"
            "Click any issue to expand — exact values, affected URLs, and step-by-step fixes.</div>",
            unsafe_allow_html=True
        )
        if fails:
            sh(f"Critical Issues ({len(fails)})")
            for issue in fails:
                render_issue(issue)
        if warns:
            sh(f"Warnings ({len(warns)})")
            for issue in warns:
                render_issue(issue)
        if not issues:
            audit_row("🟢", "No issues found — page looks technically healthy!", color="#059669")

    # ── TAB 1: ON-PAGE SEO (includes content) ─────────────────────────────────
    with tabs[1]:
        render_onpage_tab(url, results)
        # ── Content Metrics ────────────────────────────────────────────────────
        content_s = s.get("content", {})
        wc = content_s.get("word_count", 0)
        wc_source = content_s.get("word_count_source", "DOM")
        schema_hl = content_s.get("schema_headline", "")
        schema_desc = content_s.get("schema_description", "")
        article_preview = content_s.get("article_text_preview", "")

        sh("Content Metrics")

        # Show schema headline / description if available from JSON-LD
        if schema_hl or schema_desc:
            st.markdown(
                "<div style='background:#eff6ff;border:1px solid #bfdbfe;"
                "border-radius:8px;padding:.75rem 1rem;margin-bottom:.75rem'>"
                "<div style='font-size:.68rem;font-weight:600;color:#1d4ed8;"
                "text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem'>"
                "From NewsArticle / Article Schema</div>"
                + (f"<div style='font-size:.85rem;font-weight:600;color:#111827;"
                   f"margin-bottom:.25rem'>{schema_hl}</div>" if schema_hl else "")
                + (f"<div style='font-size:.82rem;color:#374151'>{schema_desc}</div>"
                   if schema_desc else "")
                + "</div>",
                unsafe_allow_html=True
            )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric("Word Count", str(wc),
                   "#059669" if wc >= 300 else "#d97706" if wc >= 150 else "#dc2626")
        with c2:
            metric("Count Source", wc_source,
                   "#059669" if "Schema" in wc_source else "#6b7280")
        with c3:
            metric("Paragraphs", str(content_s.get("paragraphs", 0)))
        with c4:
            metric("Lists / Tables",
                   f"{content_s.get('lists', 0)} / {content_s.get('tables', 0)}")

        # Article text preview (what was actually counted)
        if article_preview:
            with st.expander("Article text used for word count (preview)", expanded=False):
                st.markdown(
                    f"<div style='font-size:.8rem;color:#374151;line-height:1.7;"
                    f"font-family:IBM Plex Mono,monospace;white-space:pre-wrap;"
                    f"background:#f8f9fb;padding:.75rem;border-radius:6px'>"
                    f"{article_preview}…</div>",
                    unsafe_allow_html=True
                )

        # Entity table moved to On-Page SEO section above (section 6)
        # Show a compact entity summary here as well
        art_ents = content_s.get("article_entities", [])
        if art_ents:
            sh("Key Entities from Article Body")
            places  = [e["text"] for e in art_ents if e["type"] == "PLACE"][:6]
            orgs    = [e["text"] for e in art_ents if e["type"] == "ORG"][:4]
            events  = [e["text"] for e in art_ents if e["type"] == "EVENT"][:4]
            numbers = [e["text"] for e in art_ents if e["type"] == "NUMBER"][:4]
            def pill_row(label, items, bg, fg):
                if not items: return ""
                pills = " ".join(
                    f"<span style='background:{bg};color:{fg};border-radius:4px;"
                    f"padding:2px 8px;font-size:.75rem;margin:2px 2px;display:inline-block'>"
                    f"{i}</span>" for i in items)
                return (f"<div style='margin-bottom:.4rem'>"
                        f"<span style='font-size:.68rem;font-weight:600;color:#6b7280;"
                        f"text-transform:uppercase;letter-spacing:.06em;margin-right:8px'>"
                        f"{label}</span>{pills}</div>")
            html = (
                pill_row("Places",  places,  "#fef3c7", "#92400e") +
                pill_row("Orgs",    orgs,    "#d1fae5", "#065f46") +
                pill_row("Events",  events,  "#ede9fe", "#6d28d9") +
                pill_row("Numbers", numbers, "#f3f4f6", "#374151")
            )
            st.markdown(html, unsafe_allow_html=True)

    # ── TAB 2: META ───────────────────────────────────────────────────────────
    with tabs[2]:
        meta = s.get("meta", {})
        tl = meta.get("title_length", 0)
        dl = meta.get("description_length", 0)

        sh("Title Tag")
        c1, c2 = st.columns(2)
        with c1:
            metric("Content", meta.get("title") or "— missing —",
                   "#059669" if 50 <= tl <= 60 else "#d97706" if 30 <= tl <= 70 else "#dc2626")
        with c2:
            metric("Length", f"{tl} chars  (ideal 50–60)",
                   "#059669" if 50 <= tl <= 60 else "#d97706" if 30 <= tl <= 70 else "#dc2626")

        sh("Meta Description")
        c1, c2 = st.columns(2)
        with c1:
            metric("Content", meta.get("description") or "— missing —",
                   "#059669" if 120 <= dl <= 160 else "#d97706" if 70 <= dl <= 200 else "#dc2626")
        with c2:
            metric("Length", f"{dl} chars  (ideal 120–160)",
                   "#059669" if 120 <= dl <= 160 else "#d97706" if 70 <= dl <= 200 else "#dc2626")

        sh("Technical Meta")
        c1, c2 = st.columns(2)
        with c1:
            metric("Canonical", meta.get("canonical") or "not set",
                   "#059669" if meta.get("canonical") else "#dc2626")
            metric("Robots", meta.get("robots", "not set"))
            metric("Language (lang=)", meta.get("lang") or "not set",
                   "#059669" if meta.get("lang") else "#d97706")
        with c2:
            metric("Viewport", meta.get("viewport") or "— missing —",
                   "#059669" if meta.get("viewport") else "#dc2626")
            metric("Charset", meta.get("charset") or "not found")
            metric("Redirects", str(results.get("redirect_count", 0)),
                   "#059669" if results.get("redirect_count", 0) == 0 else "#d97706")

        sh("Open Graph")
        og = meta.get("og", {})
        if og:
            for k, v in og.items():
                metric(k, str(v)[:120])
        else:
            audit_row("🔴", "No Open Graph tags found",
                      "Add og:title, og:description, og:image, og:url to control social sharing previews.")

        sh("Twitter Cards")
        tw = meta.get("twitter", {})
        if tw:
            for k, v in tw.items():
                metric(k, str(v)[:120])
        else:
            audit_row("🟡", "No Twitter Card tags found",
                      "Add twitter:card, twitter:title, twitter:description, twitter:image.")

    # ── TAB 3: STRUCTURE ──────────────────────────────────────────────────────
    with tabs[3]:
        url_d = s.get("url", {})
        sh("URL Analysis")
        c1, c2 = st.columns(2)
        with c1:
            metric("Protocol", url_d.get("protocol", "—").upper(),
                   "#059669" if url_d.get("protocol") == "https" else "#dc2626")
            metric("Path Depth", str(url_d.get("path_depth", 0)),
                   "#059669" if url_d.get("path_depth", 0) <= 3 else "#d97706")
            metric("Uppercase in Path", "Yes ⚠" if url_d.get("has_uppercase") else "No ✓",
                   "#d97706" if url_d.get("has_uppercase") else "#059669")
        with c2:
            metric("Underscores", "Yes ⚠" if url_d.get("has_underscores") else "No ✓",
                   "#d97706" if url_d.get("has_underscores") else "#059669")
            metric("Query String", "Yes" if url_d.get("has_params") else "No")
            metric("Path Length", f"{url_d.get('path_length', 0)} chars")

        sh("Heading Hierarchy")
        headings = s.get("headings", {})
        found_any = False
        for level in range(1, 7):
            items = headings.get(f"h{level}", [])
            for h in items[:10]:
                found_any = True
                color = ("#059669" if level == 1 else "#1d4ed8" if level == 2
                         else "#d97706" if level == 3 else "#6b7280")
                indent = "&nbsp;" * ((level - 1) * 6)
                st.markdown(
                    f"<div style='padding:.35rem 0;border-bottom:1px solid #e2e6ea'>"
                    f"<span style='font-family:IBM Plex Mono,monospace;color:{color};"
                    f"font-size:.68rem;font-weight:600;margin-right:6px'>{indent}H{level}</span>"
                    f"<span style='font-size:.84rem;color:#111827'>{h[:120]}</span></div>",
                    unsafe_allow_html=True
                )
        if not found_any:
            audit_row("🔴", "No headings found on page")

        sh("Structured Data (JSON-LD)")
        sd = s.get("structured_data", [])
        if sd:
            for i, item in enumerate(sd):
                schema_type = item.get("@type", "Unknown") if isinstance(item, dict) else "Parse error"
                with st.expander(f"Schema #{i+1}: {schema_type}"):
                    st.json(item)
        else:
            audit_row("🟡", "No structured data found",
                      "Consider adding JSON-LD schema markup for rich results.")

    # ── TAB 4: IMAGES ─────────────────────────────────────────────────────────
    with tabs[4]:
        imgs = s.get("images", [])
        missing_alt = [i for i in imgs if not i["has_alt"]]
        empty_alt = [i for i in imgs if i["has_alt"] and i["alt_empty"]]
        lazy_imgs = [i for i in imgs if i.get("lazy")]
        no_dims = [i for i in imgs if not i.get("width") or not i.get("height")]
        generic_imgs = [i for i in imgs if i.get("is_generic_name")]
        whatsapp_imgs = [i for i in imgs if i.get("is_whatsapp")]

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: metric("Total", str(len(imgs)))
        with c2: metric("Missing Alt", str(len(missing_alt)),
                         "#059669" if not missing_alt else "#dc2626")
        with c3: metric("Empty Alt", str(len(empty_alt)),
                         "#059669" if not empty_alt else "#d97706")
        with c4: metric("Lazy Loaded", f"{len(lazy_imgs)}/{len(imgs)}")
        with c5: metric("Generic Names", str(len(generic_imgs)),
                         "#059669" if not generic_imgs else "#d97706")
        with c6: metric("WhatsApp", str(len(whatsapp_imgs)),
                         "#059669" if not whatsapp_imgs else "#dc2626")

        if whatsapp_imgs:
            st.markdown(
                "<div style='background:#fef2f2;border:1px solid #fecaca;"
                "border-radius:8px;padding:.75rem 1rem;margin:.5rem 0'>"
                "<strong style='color:#dc2626'>WhatsApp images detected</strong>"
                "<div style='font-size:.82rem;color:#6b7280;margin-top:3px'>"
                "WhatsApp images have generic filenames and signal low-quality content to Google. "
                "Replace with original, properly named images.</div></div>",
                unsafe_allow_html=True
            )

        if missing_alt:
            sh(f"Missing Alt ({len(missing_alt)})")
            for img in missing_alt[:20]:
                st.markdown(
                    f"<div style='padding:.4rem 0;border-bottom:1px solid #e2e6ea;"
                    f"font-family:IBM Plex Mono,monospace;font-size:.76rem;word-break:break-all'>"
                    f"<span style='color:#dc2626'>✗ no alt &nbsp;</span>"
                    f"<span style='color:#111827'>{img['src'][:100]}</span></div>",
                    unsafe_allow_html=True
                )

        sh("All Images")
        if imgs:
            df = pd.DataFrame([{
                "filename": i.get("filename", "?")[:40],
                "alt status": ("✓ ok" if (i.get("has_alt") and not i.get("alt_empty"))
                               else ("⚠ empty" if i.get("alt_empty") else "✗ missing")),
                "alt text": (i.get("alt") or "")[:50],
                "generic?": "⚠ yes" if i.get("is_generic_name") else "—",
                "whatsapp?": "🔴 yes" if i.get("is_whatsapp") else "—",
                "lazy": "✓" if i.get("lazy") else "—",
                "dims": "✓" if (i.get("width") and i.get("height")) else "—",
            } for i in imgs[:60]])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB 5: LINKS ──────────────────────────────────────────────────────────
    with tabs[5]:
        links = s.get("links", {})
        int_links  = links.get("internal", [])
        ext_links  = links.get("external", [])
        scope_label = links.get("internal_scope", "article body <p> tags")
        nofollow   = [l for l in ext_links if l.get("nofollow")]
        no_text_int = [l for l in int_links if not l.get("text")]
        no_text_ext = [l for l in ext_links if not l.get("text")]

        # Scope notice
        st.markdown(
            f"<div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;"
            f"padding:.6rem 1rem;margin-bottom:.85rem;font-size:.82rem;color:#1e40af'>"
            f"<strong>Internal links scope:</strong> {scope_label} "
            f"— nav menus, sidebars and footers are excluded.</div>",
            unsafe_allow_html=True
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: metric("Total (article)", str(len(int_links) + len(ext_links)))
        with c2: metric("Internal", str(len(int_links)),
                        "#059669" if len(int_links) >= 3 else "#d97706")
        with c3: metric("External", str(len(ext_links)))
        with c4: metric("Nofollow Ext", str(len(nofollow)))
        with c5: metric("No Anchor Text", str(len(no_text_int) + len(no_text_ext)),
                        "#059669" if not (no_text_int + no_text_ext) else "#d97706")

        # Internal links
        sh(f"Internal Links from Article Body ({len(int_links)})")
        if int_links:
            with st.expander(f"View all {len(int_links)} internal links", expanded=True):
                for i, l in enumerate(int_links[:60], 1):
                    nf_badge = tag("nofollow", "warn") if l.get("nofollow") else ""
                    anchor_color = "#111827" if l.get("text") else "#dc2626"
                    anchor_text  = l.get("text") or "⚠ no anchor text"
                    st.markdown(
                        f"<div style='display:grid;grid-template-columns:24px 1fr;"
                        f"gap:8px;padding:.4rem 0;border-bottom:1px solid #e2e6ea;"
                        f"align-items:start'>"
                        f"<div style='font-size:.68rem;color:#9ca3af;padding-top:2px'>{i}</div>"
                        f"<div>"
                        f"<div style='font-size:.84rem;color:{anchor_color};font-weight:500'>"
                        f"{anchor_text[:80]} {nf_badge}</div>"
                        f"<div style='font-family:IBM Plex Mono,monospace;font-size:.72rem;"
                        f"color:#6b7280;word-break:break-all;margin-top:1px'>{l['href']}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                "<div style='background:#fffbeb;border:1px solid #fde68a;border-radius:6px;"
                "padding:.6rem 1rem;font-size:.82rem;color:#92400e'>"
                "No internal links found inside article body paragraphs. "
                "Add internal links to related articles within the article text.</div>",
                unsafe_allow_html=True
            )

        # External links
        sh(f"External Links from Article Body ({len(ext_links)})")
        if ext_links:
            with st.expander(f"View all {len(ext_links)} external links", expanded=False):
                for i, l in enumerate(ext_links[:60], 1):
                    t_html = ""
                    if l.get("nofollow"):   t_html += tag("nofollow", "warn")
                    if l.get("ugc"):        t_html += tag("ugc", "info")
                    if l.get("sponsored"):  t_html += tag("sponsored", "fail")
                    st.markdown(
                        f"<div style='display:grid;grid-template-columns:24px 1fr;"
                        f"gap:8px;padding:.4rem 0;border-bottom:1px solid #e2e6ea;"
                        f"align-items:start'>"
                        f"<div style='font-size:.68rem;color:#9ca3af;padding-top:2px'>{i}</div>"
                        f"<div>"
                        f"<div style='font-size:.84rem;color:#111827;font-weight:500'>"
                        f"{l.get('text') or '(no anchor text)'} {t_html}</div>"
                        f"<div style='font-family:IBM Plex Mono,monospace;font-size:.72rem;"
                        f"color:#6b7280;word-break:break-all;margin-top:1px'>{l['href']}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
        else:
            audit_row("🟡", "No external links in article body", "#6b7280")

    # ── TAB 6: PERFORMANCE (includes PageSpeed) ───────────────────────────────
    with tabs[6]:
        render_performance_tab(results)
        st.markdown("---")
        render_pagespeed_tab(url)

    # ── TAB 7: SECURITY ───────────────────────────────────────────────────────
    with tabs[7]:
        hdrs = s.get("headers", {})
        url_d = s.get("url", {})

        sh("HTTPS")
        if url_d.get("protocol") == "https":
            audit_row("🟢", "Page served over HTTPS", color="#059669")
        else:
            audit_row("🔴", "Page NOT served over HTTPS",
                      "HTTPS is a Google ranking signal. Obtain SSL cert and redirect HTTP → HTTPS.",
                      "#dc2626")

        sh("Security Headers")
        sec_headers = [
            ("strict-transport-security", "HSTS",
             "Enforces HTTPS, prevents protocol downgrade attacks.",
             "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"),
            ("x-content-type-options", "X-Content-Type-Options",
             "Prevents MIME-type sniffing.",
             "X-Content-Type-Options: nosniff"),
            ("x-frame-options", "X-Frame-Options",
             "Prevents clickjacking via iframe embedding.",
             "X-Frame-Options: SAMEORIGIN"),
            ("content-security-policy", "Content-Security-Policy",
             "Controls which resources can be loaded.",
             "Content-Security-Policy: default-src 'self'; ..."),
            ("referrer-policy", "Referrer-Policy",
             "Controls referrer info sent in requests.",
             "Referrer-Policy: strict-origin-when-cross-origin"),
            ("permissions-policy", "Permissions-Policy",
             "Restricts access to browser features.",
             "Permissions-Policy: geolocation=(), camera=(), microphone=()"),
        ]
        for key, label, purpose, fix in sec_headers:
            val = hdrs.get(key)
            if val:
                with st.expander(f"✅ {label} — present"):
                    st.markdown(
                        f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.4rem'>{purpose}</div>"
                        f"{drill_item(val[:200], '#059669')}",
                        unsafe_allow_html=True
                    )
            else:
                with st.expander(f"⚠️ {label} — missing"):
                    st.markdown(
                        f"<div style='font-size:.82rem;color:#6b7280;margin-bottom:.4rem'>{purpose}</div>"
                        f"{drill_item('Recommended: ' + fix, '#d97706')}",
                        unsafe_allow_html=True
                    )

        sh("All Response Headers")
        if hdrs:
            df = pd.DataFrame(list(hdrs.items()), columns=["Header", "Value"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB 8: INDEXING ───────────────────────────────────────────────────────
    with tabs[8]:
        render_indexing_tab(url, results)

    # ── TAB 9: SIMILAR ARTICLES ───────────────────────────────────────────────
    with tabs[9]:
        render_similar_articles_tab(url, results)

    # ── TAB 10: RAW ───────────────────────────────────────────────────────────
    with tabs[10]:
        sh("Full Analysis JSON")
        display = {k: v for k, v in results.items() if k != "sections"}
        display["sections"] = {k: v for k, v in s.items()
                                if k not in ("images", "scripts", "stylesheets")}
        st.json(display)

elif run and not url_input:
    st.warning("Please enter a URL.")
else:
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🎯", "Issues & Score", "Scored audit — critical fails and warnings with fixes"),
        ("📝", "On-Page SEO", "SERP preview, headings, entities, AEO hints"),
        ("📄", "Meta & Head", "Title, description, canonical, OG, Twitter"),
        ("📐", "Structure", "H1–H6, JSON-LD schema, URL analysis"),
        ("🖼", "Images", "Alt text, lazy load, generic filename detection"),
        ("🔗", "Links", "Internal/external, nofollow, anchor audit"),
        ("⚡", "Performance", "TTFB, render-blocking scripts, PageSpeed LAB"),
        ("🛡", "Security", "HTTPS, HSTS, CSP, X-Frame, Referrer-Policy"),
        ("🔎", "Indexing", "robots.txt, noindex, canonical, sitemap, site: check"),
        ("🔍", "Similar Articles", "Competing content via DuckDuckGo/Google"),
    ]
    c1, c2, c3, c4, c5 = st.columns(5)
    cols = [c1, c2, c3, c4, c5]
    for i, (icon, title, desc) in enumerate(cards):
        with cols[i % 5]:
            st.markdown(
                f"<div style='background:#ffffff;border:1px solid #e2e6ea;"
                f"border-radius:10px;padding:1rem;margin-bottom:.75rem;"
                f"box-shadow:0 1px 3px rgba(0,0,0,.04)'>"
                f"<div style='font-size:1.3rem;margin-bottom:.35rem'>{icon}</div>"
                f"<div style='font-weight:600;font-size:.85rem;margin-bottom:.2rem;color:#111827'>{title}</div>"
                f"<div style='font-size:.75rem;color:#6b7280;line-height:1.4'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )