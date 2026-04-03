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
    page_title="TechSEO Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');
:root{--bg:#0a0a0f;--surface:#12121a;--surface2:#1a1a26;--border:#2a2a3d;
      --accent:#00ff88;--text:#e8e8f0;--muted:#6b6b8a;--warn:#ffaa00;--good:#00cc66;--bad:#ff3366}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif}
[data-testid="stHeader"]{background:transparent!important}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important}
.hero{text-align:center;padding:2.5rem 1rem 1.5rem}
.hero-title{font-family:'Syne',sans-serif;font-size:clamp(2rem,5vw,4rem);font-weight:800;letter-spacing:-2px;
  background:linear-gradient(135deg,#00ff88 0%,#3366ff 50%,#ff3366 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;margin-bottom:.4rem}
.hero-sub{font-family:'IBM Plex Mono',monospace;color:var(--muted);font-size:.8rem;letter-spacing:3px;text-transform:uppercase}
.stTextInput>div>div>input{background:var(--surface2)!important;border:1px solid var(--border)!important;
  border-radius:4px!important;color:var(--text)!important;font-family:'IBM Plex Mono',monospace!important;
  font-size:.95rem!important;padding:.75rem 1rem!important}
.stTextInput>div>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(0,255,136,.15)!important}
.stButton>button{background:var(--accent)!important;color:#000!important;border:none!important;border-radius:4px!important;
  font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.9rem!important;
  letter-spacing:1px!important;padding:.65rem 2rem!important;text-transform:uppercase!important}
.stButton>button:hover{background:#00cc6a!important}
.metric-card{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:1rem 1.25rem;margin-bottom:.5rem}
.metric-label{font-family:'IBM Plex Mono',monospace;font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:.25rem}
.metric-value{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:600;color:var(--text)}
.sh{font-family:'Syne',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;
  color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:.4rem;margin:1.25rem 0 .75rem}
.audit-row{display:flex;align-items:flex-start;gap:.75rem;padding:.55rem 0;border-bottom:1px solid var(--border);font-size:.88rem}
.audit-row:last-child{border-bottom:none}
.audit-icon{font-size:1rem;flex-shrink:0;margin-top:2px}
.audit-label{font-weight:600;color:var(--text)}
.audit-detail{color:var(--muted);font-family:'IBM Plex Mono',monospace;font-size:.76rem;margin-top:2px;word-break:break-all}
.tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.65rem;padding:1px 6px;
  border-radius:3px;margin-right:4px;font-weight:600}
.tag-fail{background:rgba(255,51,102,.15);color:#ff3366;border:1px solid rgba(255,51,102,.3)}
.tag-warn{background:rgba(255,170,0,.15);color:#ffaa00;border:1px solid rgba(255,170,0,.3)}
.tag-pass{background:rgba(0,204,102,.15);color:#00cc66;border:1px solid rgba(0,204,102,.3)}
.tag-info{background:rgba(51,102,255,.15);color:#3366ff;border:1px solid rgba(51,102,255,.3)}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:1px solid var(--border)!important;gap:0!important}
.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace!important;font-size:.72rem!important;
  text-transform:uppercase!important;letter-spacing:1.5px!important;color:var(--muted)!important;
  background:transparent!important;border:none!important;padding:.75rem 1.1rem!important}
.stTabs [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important}
.streamlit-expanderHeader{background:var(--surface)!important;border:1px solid var(--border)!important;
  border-radius:4px!important;font-family:'IBM Plex Mono',monospace!important;font-size:.8rem!important;color:var(--text)!important}
code{background:var(--surface2)!important;color:var(--accent)!important;font-family:'IBM Plex Mono',monospace!important;
  border-radius:3px!important;padding:.1rem .3rem!important;font-size:.8rem!important}
.stProgress>div>div>div{background:var(--accent)!important}
hr{border-color:var(--border)!important}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def metric(label, value, color=None):
    c = color or "var(--text)"
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
        f"<div style='background:var(--surface2);border:1px solid var(--border);border-radius:4px;"
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
        "likely_indexed":     ("🟢", "#00cc66", "Likely Indexed",
                               "All major signals indicate this page is (or will be) indexed by Google."),
        "at_risk":            ("🟡", "#ffaa00", "At Risk / Uncertain",
                               "Mixed signals detected. Page may be indexed but has issues that could prevent or delay it."),
        "uncertain":          ("🟡", "#ffaa00", "Uncertain",
                               "Could not conclusively determine indexing status. Check Google Search Console."),
        "likely_not_indexed": ("🔴", "#ff3366", "Likely NOT Indexed",
                               "One or more critical signals block Google from indexing this page."),
    }
    icon, color, label, summary = verdict_config.get(verdict, verdict_config["uncertain"])

    # ── Verdict card ──────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='background:var(--surface);border:2px solid {color}33;"
        f"border-left:4px solid {color};border-radius:8px;padding:1.25rem 1.5rem;margin-bottom:1.5rem'>"
        f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:.4rem'>"
        f"<span style='font-size:1.5rem'>{icon}</span>"
        f"<span style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;"
        f"color:{color}'>{label}</span></div>"
        f"<div style='font-size:.85rem;color:var(--muted)'>{summary}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Score bar ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    total_votes = max(idx["indexed_votes"] + idx["not_indexed_votes"], 1)
    index_pct = round(idx["indexed_votes"] / total_votes * 100)
    with c1: metric("Indexability Score", f"{index_pct}%",
                    "#00cc66" if index_pct >= 70 else "#ffaa00" if index_pct >= 40 else "#ff3366")
    with c2: metric("Positive Signals", str(idx["indexed_votes"]), "#00cc66")
    with c3: metric("Blocking Signals", str(idx["not_indexed_votes"]),
                    "#00cc66" if idx["not_indexed_votes"] == 0 else "#ff3366")

    # ── Quick action links ────────────────────────────────────────────────────
    sh("Quick Actions")
    st.markdown(
        f"<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:.5rem'>"
        f"<a href='{idx['manual_check_url']}' target='_blank' "
        f"style='background:var(--surface2);border:1px solid var(--border);border-radius:4px;"
        f"padding:.45rem .9rem;font-family:IBM Plex Mono,monospace;font-size:.76rem;"
        f"color:var(--accent);text-decoration:none'>🔍 Check site: in Google ↗</a>"
        f"<a href='{idx['search_console_url']}' target='_blank' "
        f"style='background:var(--surface2);border:1px solid var(--border);border-radius:4px;"
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
            exp_icon, exp_color = "🟢", "#00cc66"
        elif status == "block":
            exp_icon, exp_color = "🔴", "#ff3366"
        else:
            exp_icon, exp_color = "🟡", "#ffaa00"

        with st.expander(f"{exp_icon} {name}"):
            st.markdown(
                f"<div style='font-size:.82rem;color:var(--muted);margin-bottom:.5rem'>{detail}</div>",
                unsafe_allow_html=True
            )
            if fix:
                st.markdown(
                    f"<div style='background:rgba(255,170,0,.08);border:1px solid rgba(255,170,0,.25);"
                    f"border-radius:4px;padding:.5rem .75rem;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.76rem;color:#ffaa00'>"
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
                    f"<div style='font-size:.82rem;color:var(--muted);margin-bottom:.5rem'>{r_detail}</div>"
                    f"<div style='background:rgba(255,170,0,.08);border:1px solid rgba(255,170,0,.25);"
                    f"border-radius:4px;padding:.5rem .75rem;font-family:IBM Plex Mono,monospace;"
                    f"font-size:.76rem;color:#ffaa00'><span style='font-weight:600'>Fix: </span>{r_fix}</div>",
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
    img_list = []
    for img in soup.find_all("img"):
        src = urljoin(url, img.get("src", ""))
        alt = img.get("alt")
        img_list.append({
            "src": src, "alt": alt,
            "has_alt": alt is not None, "alt_empty": alt == "",
            "width": img.get("width", ""), "height": img.get("height", ""),
            "lazy": img.get("loading", "") == "lazy",
            "srcset": bool(img.get("srcset")),
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
    int_links, ext_links = [], []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        abs_href = urljoin(url, href)
        lp = urlparse(abs_href)
        rel_attr = a.get("rel", [])
        entry = {
            "href": abs_href, "text": a.get_text(strip=True),
            "nofollow": "nofollow" in rel_attr,
            "ugc": "ugc" in rel_attr,
            "sponsored": "sponsored" in rel_attr,
            "rel": " ".join(rel_attr),
        }
        if lp.netloc == base_domain or not lp.netloc:
            int_links.append(entry)
        else:
            ext_links.append(entry)
    r["sections"]["links"] = {"internal": int_links, "external": ext_links}

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
    for t in soup(["script", "style", "noscript", "meta", "link"]):
        t.decompose()
    text_body = soup.get_text(separator=" ", strip=True)
    words = re.findall(r"\b[a-z]{3,}\b", text_body.lower())
    r["sections"]["content"] = {
        "word_count": len(words),
        "top_keywords": Counter(words).most_common(25),
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
            f"<span style='font-size:.82rem;color:var(--muted);margin-left:8px'>"
            f"{issue['detail']}</span></div>",
            unsafe_allow_html=True
        )
        if drilldown:
            st.markdown(
                "<div style='font-size:.68rem;color:var(--muted);text-transform:uppercase;"
                "letter-spacing:2px;margin:.4rem 0'>Details & Fix</div>",
                unsafe_allow_html=True
            )
            for item in drilldown:
                color = "#ffaa00" if item.lower().startswith("action:") \
                    else "#3366ff" if item.lower().startswith("add:") \
                    else "#00cc66" if item.lower().startswith("option") \
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
                    "#00ff88" if ttfb < 200 else "#ffaa00" if ttfb < 600 else "#ff3366")
    with c2: metric("HTML Size", f"{html_kb} KB",
                    "#00ff88" if html_kb < 100 else "#ffaa00" if html_kb < 300 else "#ff3366")
    with c3: metric("Render-Blocking Scripts", str(len(blocking)),
                    "#00ff88" if not blocking else "#ff3366")
    with c4: metric("Total Scripts", str(perf.get("total_scripts", 0)))

    # ── Render-blocking scripts ───────────────────────────────────────────────
    sh(f"🔴 Render-Blocking Scripts ({len(blocking)}) — head, external, no defer/async")
    if blocking:
        for sc in blocking:
            st.markdown(
                f"<div style='background:rgba(255,51,102,.07);border:1px solid rgba(255,51,102,.3);"
                f"border-radius:5px;padding:.65rem .9rem;margin-bottom:.4rem'>"
                f"<div style='display:flex;gap:8px;align-items:center;margin-bottom:4px'>"
                f"<span style='color:#ff3366;font-family:IBM Plex Mono,monospace;font-size:.7rem;font-weight:600'>BLOCKING</span>"
                f"<span style='color:var(--muted);font-family:IBM Plex Mono,monospace;font-size:.68rem'>"
                f"location: {sc['location']} | defer: {'✓' if sc['defer'] else '✗'} | async: {'✓' if sc['async'] else '✗'}"
                f"</span></div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:.76rem;word-break:break-all;"
                f"color:var(--text);margin-bottom:4px'>{sc['src']}</div>"
                f"<div style='color:#ffaa00;font-size:.71rem;font-family:IBM Plex Mono,monospace'>"
                f"Fix → add <b>defer</b> (non-critical) or <b>async</b> (independent) attribute</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        audit_row("🟢", "No render-blocking scripts detected", color="#00cc66")

    # ── All external scripts ──────────────────────────────────────────────────
    ext = [sc for sc in scripts_all if sc["external"]]
    sh(f"All External Scripts ({len(ext)})")
    if ext:
        with st.expander(f"View all {len(ext)} external scripts", expanded=len(blocking) > 0):
            for sc in ext:
                if sc["blocking"]:
                    status_label, status_color = "BLOCKING", "#ff3366"
                elif sc["defer"]:
                    status_label, status_color = "defer", "#00cc66"
                elif sc["async"]:
                    status_label, status_color = "async", "#00cc66"
                else:
                    status_label, status_color = "no attr", "#ffaa00"
                st.markdown(
                    f"<div style='padding:.45rem 0;border-bottom:1px solid var(--border);"
                    f"font-family:IBM Plex Mono,monospace;font-size:.76rem'>"
                    f"<span style='color:{status_color};font-weight:600;min-width:72px;"
                    f"display:inline-block'>[{status_label}]</span>"
                    f"<span style='word-break:break-all;color:var(--text)'>{sc['src']}</span>"
                    f"<span style='color:var(--muted);margin-left:6px;font-size:.68rem'>({sc['location']})</span>"
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
                    "#ffaa00" if len(inline) > 20 else "#00ff88")
    with c2:
        total_inline_bytes = sum(sc.get("size_hint", 0) for sc in inline)
        metric("Total Inline Size", f"{round(total_inline_bytes/1024,1)} KB")
    with c3:
        head_inline = sum(1 for sc in inline if sc["location"] == "head")
        metric("In <head>", str(head_inline), "#ffaa00" if head_inline > 0 else "#00ff88")

    # ── Stylesheets ────────────────────────────────────────────────────────────
    sh(f"Stylesheets ({len(css_list)})")
    if css_list:
        for c in css_list:
            if c["preload"]:
                icon, note_color, note = "🟢", "#00cc66", "preloaded"
            elif c["in_head"] and c["media"] in ("all", "screen", ""):
                icon, note_color, note = "🟡", "#ffaa00", "head — render-blocking"
            else:
                icon, note_color, note = "🟢", "#00cc66", f"media={c['media']}"
            st.markdown(
                f"<div style='padding:.45rem 0;border-bottom:1px solid var(--border);"
                f"font-family:IBM Plex Mono,monospace;font-size:.76rem'>"
                f"{icon} <span style='word-break:break-all;color:var(--text)'>{c['href']}</span>"
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
                  "#00cc66" if val else "#ffaa00")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero'>
  <div class='hero-title'>TechSEO Auditor</div>
  <div class='hero-sub'>In-depth technical SEO · Drill-down issues · Indexing check</div>
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
               "#00ff88" if score >= 80 else "#ffaa00" if score >= 60 else "#ff3366")
    with c2:
        sc = results.get("status_code", "—")
        metric("HTTP Status", str(sc), "#00ff88" if sc == 200 else "#ff3366")
    with c3:
        metric("TTFB", f"{results.get('ttfb_ms', 0)} ms",
               "#00ff88" if results.get("ttfb_ms", 0) < 200
               else "#ffaa00" if results.get("ttfb_ms", 0) < 600 else "#ff3366")
    with c4:
        metric("HTML Size", f"{s.get('performance', {}).get('html_size_kb', '—')} KB")
    with c5:
        metric("Critical", str(len(fails)), "#00ff88" if not fails else "#ff3366")
    with c6:
        metric("Warnings", str(len(warns)), "#00ff88" if not warns else "#ffaa00")

    st.markdown("---")

    tabs = st.tabs([
        "🎯 Issues", "📄 Meta", "🖼 Images", "🔗 Links",
        "📐 Structure", "⚡ Performance", "🛡 Security", "📊 Content",
        "🔎 Indexing", "🔧 Raw"
    ])

    # ── ISSUES ────────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(
            "<div style='font-size:.82rem;color:var(--muted);margin-bottom:1rem'>"
            "Click any issue to expand — specific element URLs, exact values, and step-by-step fixes.</div>",
            unsafe_allow_html=True
        )
        if fails:
            sh(f"🔴 Critical Issues ({len(fails)})")
            for issue in fails:
                render_issue(issue)
        if warns:
            sh(f"🟡 Warnings ({len(warns)})")
            for issue in warns:
                render_issue(issue)
        if not issues:
            audit_row("🟢", "No issues found — page looks technically healthy!", color="#00cc66")

    # ── META ──────────────────────────────────────────────────────────────────
    with tabs[1]:
        meta = s.get("meta", {})
        tl = meta.get("title_length", 0)
        dl = meta.get("description_length", 0)

        sh("Title Tag")
        c1, c2 = st.columns(2)
        with c1:
            metric("Content", meta.get("title") or "— missing —",
                   "#00ff88" if 50 <= tl <= 60 else "#ffaa00" if 30 <= tl <= 70 else "#ff3366")
        with c2:
            metric("Length", f"{tl} chars  (ideal 50–60)",
                   "#00ff88" if 50 <= tl <= 60 else "#ffaa00" if 30 <= tl <= 70 else "#ff3366")

        sh("Meta Description")
        c1, c2 = st.columns(2)
        with c1:
            metric("Content", meta.get("description") or "— missing —",
                   "#00ff88" if 120 <= dl <= 160 else "#ffaa00" if 70 <= dl <= 200 else "#ff3366")
        with c2:
            metric("Length", f"{dl} chars  (ideal 120–160)",
                   "#00ff88" if 120 <= dl <= 160 else "#ffaa00" if 70 <= dl <= 200 else "#ff3366")

        sh("Technical Meta")
        c1, c2 = st.columns(2)
        with c1:
            metric("Canonical", meta.get("canonical") or "not set",
                   "#00ff88" if meta.get("canonical") else "#ff3366")
            metric("Robots", meta.get("robots", "not set"))
            metric("Language (lang=)", meta.get("lang") or "not set",
                   "#00ff88" if meta.get("lang") else "#ffaa00")
        with c2:
            metric("Viewport", meta.get("viewport") or "— missing —",
                   "#00ff88" if meta.get("viewport") else "#ff3366")
            metric("Charset", meta.get("charset") or "not found")
            metric("Redirects", str(results.get("redirect_count", 0)),
                   "#00ff88" if results.get("redirect_count", 0) == 0 else "#ffaa00")

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

    # ── IMAGES ────────────────────────────────────────────────────────────────
    with tabs[2]:
        imgs = s.get("images", [])
        missing_alt = [i for i in imgs if not i["has_alt"]]
        empty_alt = [i for i in imgs if i["has_alt"] and i["alt_empty"]]
        lazy_imgs = [i for i in imgs if i.get("lazy")]
        no_dims = [i for i in imgs if not i.get("width") or not i.get("height")]

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: metric("Total Images", str(len(imgs)))
        with c2: metric("Missing Alt", str(len(missing_alt)),
                         "#00ff88" if not missing_alt else "#ff3366")
        with c3: metric("Empty Alt", str(len(empty_alt)),
                         "#00ff88" if not empty_alt else "#ffaa00")
        with c4: metric("Lazy Loaded", f"{len(lazy_imgs)}/{len(imgs)}")
        with c5: metric("Missing Dims", str(len(no_dims)),
                         "#00ff88" if not no_dims else "#ffaa00")

        if missing_alt:
            sh(f"🔴 Missing Alt Attribute ({len(missing_alt)})")
            for img in missing_alt[:30]:
                st.markdown(
                    f"<div style='padding:.4rem 0;border-bottom:1px solid var(--border);"
                    f"font-family:IBM Plex Mono,monospace;font-size:.76rem;word-break:break-all'>"
                    f"<span style='color:#ff3366'>✗ no alt  </span>"
                    f"<span style='color:var(--text)'>{img['src']}</span></div>",
                    unsafe_allow_html=True
                )

        if empty_alt:
            sh(f"🟡 Empty Alt Text ({len(empty_alt)})")
            for img in empty_alt[:30]:
                st.markdown(
                    f"<div style='padding:.4rem 0;border-bottom:1px solid var(--border);"
                    f"font-family:IBM Plex Mono,monospace;font-size:.76rem;word-break:break-all'>"
                    f"<span style='color:#ffaa00'>⚠ empty  </span>"
                    f"<span style='color:var(--text)'>{img['src']}</span></div>",
                    unsafe_allow_html=True
                )

        sh("Full Image Inventory")
        if imgs:
            df = pd.DataFrame([{
                "src": i["src"][:80],
                "alt status": ("✓ ok" if (i["has_alt"] and not i["alt_empty"])
                               else ("⚠ empty" if i["alt_empty"] else "✗ missing")),
                "alt text": (i["alt"] or "")[:60],
                "lazy": "✓" if i.get("lazy") else "—",
                "dims": "✓" if (i.get("width") and i.get("height")) else "—",
                "srcset": "✓" if i.get("srcset") else "—",
            } for i in imgs[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── LINKS ─────────────────────────────────────────────────────────────────
    with tabs[3]:
        links = s.get("links", {})
        int_links = links.get("internal", [])
        ext_links = links.get("external", [])
        nofollow = [l for l in ext_links if l.get("nofollow")]
        no_text = [l for l in int_links + ext_links if not l.get("text")]

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: metric("Total", str(len(int_links) + len(ext_links)))
        with c2: metric("Internal", str(len(int_links)))
        with c3: metric("External", str(len(ext_links)))
        with c4: metric("Nofollow", str(len(nofollow)))
        with c5: metric("No Anchor Text", str(len(no_text)),
                         "#00ff88" if not no_text else "#ffaa00")

        with st.expander(f"Internal Links ({len(int_links)})", expanded=False):
            for l in int_links[:60]:
                tags_html = tag("nofollow", "warn") if l.get("nofollow") else ""
                st.markdown(
                    f"<div style='padding:.35rem 0;border-bottom:1px solid var(--border);font-size:.82rem'>"
                    f"<span style='color:#3366ff'>{l.get('text') or '(no anchor text)'}</span> {tags_html}"
                    f"<div style='font-family:IBM Plex Mono,monospace;font-size:.72rem;"
                    f"color:var(--muted);word-break:break-all'>{l['href']}</div></div>",
                    unsafe_allow_html=True
                )

        with st.expander(f"External Links ({len(ext_links)})", expanded=False):
            for l in ext_links[:60]:
                t_html = ""
                if l.get("nofollow"): t_html += tag("nofollow", "warn")
                if l.get("ugc"):      t_html += tag("ugc", "info")
                if l.get("sponsored"): t_html += tag("sponsored", "fail")
                st.markdown(
                    f"<div style='padding:.35rem 0;border-bottom:1px solid var(--border);font-size:.82rem'>"
                    f"<span style='color:var(--text)'>{l.get('text') or '(no anchor text)'}</span> {t_html}"
                    f"<div style='font-family:IBM Plex Mono,monospace;font-size:.72rem;"
                    f"color:var(--muted);word-break:break-all'>{l['href']}</div></div>",
                    unsafe_allow_html=True
                )

    # ── STRUCTURE ─────────────────────────────────────────────────────────────
    with tabs[4]:
        url_d = s.get("url", {})
        sh("URL Analysis")
        c1, c2 = st.columns(2)
        with c1:
            metric("Protocol", url_d.get("protocol", "—").upper(),
                   "#00ff88" if url_d.get("protocol") == "https" else "#ff3366")
            metric("Path Depth", str(url_d.get("path_depth", 0)),
                   "#00ff88" if url_d.get("path_depth", 0) <= 3 else "#ffaa00")
            metric("Uppercase in Path", "Yes ⚠" if url_d.get("has_uppercase") else "No ✓",
                   "#ffaa00" if url_d.get("has_uppercase") else "#00ff88")
        with c2:
            metric("Underscores", "Yes ⚠" if url_d.get("has_underscores") else "No ✓",
                   "#ffaa00" if url_d.get("has_underscores") else "#00ff88")
            metric("Query String", "Yes" if url_d.get("has_params") else "No")
            metric("Path Length", f"{url_d.get('path_length', 0)} chars")

        sh("Heading Hierarchy")
        headings = s.get("headings", {})
        found_any = False
        for level in range(1, 7):
            items = headings.get(f"h{level}", [])
            for h in items[:10]:
                found_any = True
                color = ("#00ff88" if level == 1 else "#3366ff" if level == 2
                         else "#ffaa00" if level == 3 else "var(--muted)")
                indent = "&nbsp;" * ((level - 1) * 6)
                st.markdown(
                    f"<div style='padding:.35rem 0;border-bottom:1px solid var(--border);font-size:.85rem'>"
                    f"<span style='font-family:IBM Plex Mono,monospace;color:{color};"
                    f"font-size:.68rem;margin-right:8px'>H{level}</span>"
                    f"{indent}<span style='color:var(--text)'>{h[:120]}</span></div>",
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

    # ── PERFORMANCE ───────────────────────────────────────────────────────────
    with tabs[5]:
        render_performance_tab(results)

    # ── SECURITY ──────────────────────────────────────────────────────────────
    with tabs[6]:
        hdrs = s.get("headers", {})
        url_d = s.get("url", {})

        sh("HTTPS")
        if url_d.get("protocol") == "https":
            audit_row("🟢", "Page served over HTTPS", color="#00cc66")
        else:
            audit_row("🔴", "Page NOT served over HTTPS",
                      "HTTPS is a Google ranking signal. Obtain SSL cert and redirect HTTP → HTTPS.",
                      "#ff3366")

        sh("Security Headers — click to see value or fix")
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
                with st.expander(f"🟢 {label} — present"):
                    st.markdown(
                        f"<div style='font-family:IBM Plex Mono,monospace;font-size:.78rem'>"
                        f"<div style='color:var(--muted);margin-bottom:.4rem'>{purpose}</div>"
                        f"{drill_item(val[:200], '#00cc66')}</div>",
                        unsafe_allow_html=True
                    )
            else:
                with st.expander(f"🟡 {label} — missing"):
                    st.markdown(
                        f"<div style='font-family:IBM Plex Mono,monospace;font-size:.78rem'>"
                        f"<div style='color:var(--muted);margin-bottom:.4rem'>{purpose}</div>"
                        f"{drill_item('Recommended: ' + fix, '#ffaa00')}</div>",
                        unsafe_allow_html=True
                    )

        sh("All Response Headers")
        if hdrs:
            df = pd.DataFrame(list(hdrs.items()), columns=["Header", "Value"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── CONTENT ───────────────────────────────────────────────────────────────
    with tabs[7]:
        content = s.get("content", {})
        wc = content.get("word_count", 0)
        c1, c2, c3 = st.columns(3)
        with c1:
            metric("Word Count", str(wc),
                   "#00ff88" if wc >= 300 else "#ffaa00" if wc >= 150 else "#ff3366")
        with c2:
            metric("Paragraphs", str(content.get("paragraphs", 0)))
        with c3:
            metric("Lists / Tables",
                   f"{content.get('lists', 0)} / {content.get('tables', 0)}")

        sh("Top Keywords by Frequency")
        kws = content.get("top_keywords", [])
        if kws:
            df = pd.DataFrame(kws, columns=["Keyword", "Count"])
            df["Density"] = df["Count"].apply(
                lambda x: f"{x / max(wc, 1) * 100:.2f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── INDEXING ──────────────────────────────────────────────────────────────
    with tabs[8]:
        render_indexing_tab(url, results)

    # ── RAW ───────────────────────────────────────────────────────────────────
    with tabs[9]:
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
        ("📄", "Meta & Head", "Title, description, canonical, OG, Twitter"),
        ("⚡", "Performance", "TTFB, render-blocking scripts & CSS, HTML size"),
        ("🖼", "Images", "Alt text, lazy loading, dimensions, srcset"),
        ("🔗", "Links", "Internal/external, nofollow, anchor text audit"),
        ("📐", "Structure", "H1–H6 hierarchy, JSON-LD schema, URL depth"),
        ("🛡", "Security", "HTTPS, HSTS, CSP, X-Frame, Referrer-Policy"),
        ("🔎", "Google Indexing", "site: check, robots.txt, noindex, canonical, sitemap"),
        ("📊", "Content", "Word count, keyword frequency, content signals"),
    ]
    for i, (icon, title, desc) in enumerate(cards):
        with [c1, c2, c3, c4][i % 4]:
            st.markdown(
                f"<div style='background:var(--surface);border:1px solid var(--border);"
                f"border-radius:6px;padding:1rem;margin-bottom:.75rem'>"
                f"<div style='font-size:1.4rem;margin-bottom:.35rem'>{icon}</div>"
                f"<div style='font-weight:700;font-size:.88rem;margin-bottom:.25rem'>{title}</div>"
                f"<div style='font-size:.76rem;color:var(--muted);font-family:IBM Plex Mono,monospace'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )