import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
import json
from collections import Counter
import ssl
import socket
import hashlib

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechSEO Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #2a2a3d;
    --accent: #00ff88;
    --accent2: #ff3366;
    --accent3: #3366ff;
    --text: #e8e8f0;
    --muted: #6b6b8a;
    --warn: #ffaa00;
    --good: #00cc66;
    --bad: #ff3366;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }

h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #00ff88 0%, #3366ff 50%, #ff3366 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Input area */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,255,136,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 1px !important;
    padding: 0.65rem 2rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00cc6a !important;
    transform: translateY(-1px) !important;
}

/* Score ring container */
.score-ring-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1.5rem 0;
}

/* Metric cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.25rem;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
}

/* Issue tags */
.tag-pass { color: var(--good); font-size: 0.8rem; }
.tag-warn { color: var(--warn); font-size: 0.8rem; }
.tag-fail { color: var(--bad); font-size: 0.8rem; }

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
}

/* Audit row */
.audit-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.audit-icon { font-size: 1rem; flex-shrink: 0; margin-top: 2px; }
.audit-label { font-weight: 600; color: var(--text); }
.audit-detail { color: var(--muted); font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; margin-top: 2px; word-break: break-all; }

/* Score badge */
.score-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3.5rem;
    font-weight: 600;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-align: center;
}

/* Tab override */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 1.25rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--text) !important;
}

/* Code blocks */
code {
    background: var(--surface2) !important;
    color: var(--accent) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    border-radius: 3px !important;
    padding: 0.1rem 0.35rem !important;
    font-size: 0.82rem !important;
}
pre {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 1rem !important;
    overflow-x: auto !important;
}

/* DataFrame */
[data-testid="stDataFrame"] { background: var(--surface) !important; }

/* Dividers */
hr { border-color: var(--border) !important; }

/* Progress bar */
.stProgress > div > div > div { background: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def fetch_page(url: str, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TechSEOBot/1.0; +https://techseo.dev)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    start = time.time()
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        ttfb = time.time() - start
        return resp, ttfb, None
    except requests.exceptions.SSLError as e:
        return None, 0, f"SSL Error: {e}"
    except requests.exceptions.ConnectionError as e:
        return None, 0, f"Connection Error: {e}"
    except requests.exceptions.Timeout:
        return None, 0, "Request timed out"
    except Exception as e:
        return None, 0, str(e)


def analyze_page(url: str) -> dict:
    """Run full technical SEO analysis on a URL."""
    results = {"url": url, "sections": {}}
    parsed = urlparse(url)

    # ── 1. Fetch ──────────────────────────────────────────────────────────────
    resp, ttfb, err = fetch_page(url)
    if err or resp is None:
        results["fetch_error"] = err or "Unknown fetch error"
        return results

    soup = BeautifulSoup(resp.text, "html.parser")
    html_size = len(resp.content)
    results["ttfb"] = round(ttfb, 3)
    results["status_code"] = resp.status_code
    results["final_url"] = resp.url
    results["redirect_count"] = len(resp.history)
    results["html_size"] = html_size

    # ── 2. META & HEAD ────────────────────────────────────────────────────────
    meta = {}

    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    meta["title"] = title_text
    meta["title_length"] = len(title_text)

    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    desc_text = desc_tag.get("content", "").strip() if desc_tag else ""
    meta["description"] = desc_text
    meta["description_length"] = len(desc_text)

    canonical = soup.find("link", rel=lambda x: x and "canonical" in x)
    meta["canonical"] = canonical.get("href", "") if canonical else ""

    robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    meta["robots"] = robots_meta.get("content", "") if robots_meta else "not set"

    # Viewport
    viewport = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    meta["viewport"] = viewport.get("content", "") if viewport else ""

    # Charset
    charset_tag = soup.find("meta", attrs={"charset": True})
    if not charset_tag:
        charset_tag = soup.find("meta", attrs={"http-equiv": re.compile(r"content-type", re.I)})
    meta["charset"] = charset_tag.get("charset", "declared via http-equiv") if charset_tag else "not found"

    # Lang
    html_tag = soup.find("html")
    meta["lang"] = html_tag.get("lang", "") if html_tag else ""

    results["sections"]["meta"] = meta

    # ── 3. HEADINGS ───────────────────────────────────────────────────────────
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        headings[f"h{level}"] = [t.get_text(strip=True) for t in tags]
    results["sections"]["headings"] = headings

    # ── 4. OPEN GRAPH & TWITTER ───────────────────────────────────────────────
    og = {}
    for tag in soup.find_all("meta", attrs={"property": re.compile(r"^og:", re.I)}):
        og[tag.get("property")] = tag.get("content", "")
    twitter = {}
    for tag in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:", re.I)}):
        twitter[tag.get("name")] = tag.get("content", "")
    results["sections"]["social"] = {"og": og, "twitter": twitter}

    # ── 5. IMAGES ─────────────────────────────────────────────────────────────
    imgs = soup.find_all("img")
    img_data = []
    for img in imgs:
        src = img.get("src", "")
        alt = img.get("alt")
        width = img.get("width", "")
        height = img.get("height", "")
        loading = img.get("loading", "")
        img_data.append({
            "src": src[:80] + "…" if len(src) > 80 else src,
            "alt": alt,
            "has_alt": alt is not None,
            "alt_empty": alt == "",
            "width": width,
            "height": height,
            "lazy": loading == "lazy",
        })
    results["sections"]["images"] = img_data

    # ── 6. LINKS ──────────────────────────────────────────────────────────────
    base_domain = parsed.netloc
    all_links = soup.find_all("a", href=True)
    internal_links, external_links, nofollow_links = [], [], []
    for a in all_links:
        href = a.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        abs_href = urljoin(url, href)
        lp = urlparse(abs_href)
        rel = a.get("rel", [])
        is_nofollow = "nofollow" in rel
        entry = {"href": abs_href[:80], "text": a.get_text(strip=True)[:50], "nofollow": is_nofollow}
        if lp.netloc == base_domain:
            internal_links.append(entry)
        else:
            external_links.append(entry)
        if is_nofollow:
            nofollow_links.append(entry)

    results["sections"]["links"] = {
        "internal": internal_links,
        "external": external_links,
        "nofollow_count": len(nofollow_links),
        "total": len(all_links),
    }

    # ── 7. STRUCTURED DATA ────────────────────────────────────────────────────
    sd = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            sd.append(data)
        except Exception:
            sd.append({"_parse_error": script.string[:100] if script.string else ""})
    results["sections"]["structured_data"] = sd

    # ── 8. PAGE PERFORMANCE SIGNALS ──────────────────────────────────────────
    perf = {}
    perf["html_size_kb"] = round(html_size / 1024, 1)
    perf["ttfb_ms"] = round(ttfb * 1000)

    scripts = soup.find_all("script", src=True)
    perf["external_scripts"] = len(scripts)
    inline_scripts = soup.find_all("script", src=False)
    perf["inline_scripts"] = len(inline_scripts)

    stylesheets = soup.find_all("link", rel=lambda x: x and "stylesheet" in x)
    perf["stylesheets"] = len(stylesheets)

    # Render-blocking: scripts in <head> without defer/async
    head = soup.find("head")
    render_blocking = 0
    if head:
        for s in head.find_all("script", src=True):
            if not s.get("defer") and not s.get("async"):
                render_blocking += 1
    perf["render_blocking_scripts"] = render_blocking

    results["sections"]["performance"] = perf

    # ── 9. HTTP HEADERS ───────────────────────────────────────────────────────
    headers_data = {}
    important_headers = [
        "content-type", "cache-control", "x-frame-options", "x-content-type-options",
        "strict-transport-security", "content-security-policy", "x-xss-protection",
        "referrer-policy", "permissions-policy", "server", "x-powered-by",
        "last-modified", "etag", "vary",
    ]
    for h in important_headers:
        val = resp.headers.get(h)
        if val:
            headers_data[h] = val
    results["sections"]["headers"] = headers_data

    # ── 10. URL ANALYSIS ──────────────────────────────────────────────────────
    url_data = {
        "protocol": parsed.scheme,
        "domain": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query,
        "fragment": parsed.fragment,
        "path_depth": len([p for p in parsed.path.split("/") if p]),
        "has_www": parsed.netloc.startswith("www."),
        "path_length": len(parsed.path),
        "has_uppercase": any(c.isupper() for c in parsed.path),
        "has_underscores": "_" in parsed.path,
        "has_spaces": " " in parsed.path or "%20" in parsed.path,
        "has_params": bool(parsed.query),
    }
    results["sections"]["url"] = url_data

    # ── 11. CONTENT SIGNALS ───────────────────────────────────────────────────
    for t in soup(["script", "style", "noscript", "meta", "link"]):
        t.decompose()
    text_content = soup.get_text(separator=" ", strip=True)
    words = re.findall(r"\b[a-z]{3,}\b", text_content.lower())
    word_count = len(words)
    freq = Counter(words).most_common(20)

    content = {
        "word_count": word_count,
        "top_keywords": freq,
        "paragraphs": len(soup.find_all("p")),
    }
    results["sections"]["content"] = content

    return results


# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def compute_score(results: dict) -> tuple[int, list]:
    """Return (0-100 score, list of issues)."""
    s = results.get("sections", {})
    score = 100
    issues = []  # (severity, category, message, detail)

    def deduct(points, severity, cat, msg, detail=""):
        nonlocal score
        score -= points
        issues.append((severity, cat, msg, detail))

    # ── Fetch issues ──────────────────────────────────────────────────────────
    if results.get("fetch_error"):
        return 0, [("fail", "Fetch", "Page could not be fetched", results["fetch_error"])]

    status = results.get("status_code", 200)
    if status >= 400:
        deduct(30, "fail", "HTTP", f"HTTP {status} error", "Page returns an error status code.")
    elif status >= 300:
        deduct(5, "warn", "HTTP", f"HTTP {status} redirect", f"{results.get('redirect_count',0)} redirect(s) detected.")

    # ── Meta ──────────────────────────────────────────────────────────────────
    meta = s.get("meta", {})
    title = meta.get("title", "")
    tl = meta.get("title_length", 0)
    if not title:
        deduct(15, "fail", "Meta", "Missing <title> tag", "Title tag is absent from the page.")
    elif tl < 30:
        deduct(8, "warn", "Meta", f"Title too short ({tl} chars)", "Ideal: 50–60 characters.")
    elif tl > 60:
        deduct(5, "warn", "Meta", f"Title too long ({tl} chars)", "May get truncated in SERPs. Ideal: 50–60 chars.")

    dl = meta.get("description_length", 0)
    desc = meta.get("description", "")
    if not desc:
        deduct(10, "fail", "Meta", "Missing meta description", "No meta description found.")
    elif dl < 70:
        deduct(5, "warn", "Meta", f"Description too short ({dl} chars)", "Ideal: 120–160 characters.")
    elif dl > 160:
        deduct(5, "warn", "Meta", f"Description too long ({dl} chars)", "May get truncated. Ideal: 120–160 chars.")

    if not meta.get("canonical"):
        deduct(8, "warn", "Meta", "No canonical URL", "Missing <link rel='canonical'>.")

    if not meta.get("lang"):
        deduct(5, "warn", "Meta", "Missing lang attribute", "Add lang attribute to <html> tag.")

    if not meta.get("viewport"):
        deduct(8, "fail", "Mobile", "Missing viewport meta tag", "Required for mobile-friendliness.")

    # ── Headings ──────────────────────────────────────────────────────────────
    h = s.get("headings", {})
    h1s = h.get("h1", [])
    if not h1s:
        deduct(12, "fail", "Headings", "No H1 tag found", "Every page should have exactly one H1.")
    elif len(h1s) > 1:
        deduct(6, "warn", "Headings", f"Multiple H1 tags ({len(h1s)})", "Use only one H1 per page.")

    # ── Images ────────────────────────────────────────────────────────────────
    imgs = s.get("images", [])
    missing_alt = [i for i in imgs if not i["has_alt"]]
    empty_alt = [i for i in imgs if i["has_alt"] and i["alt_empty"]]
    no_dims = [i for i in imgs if not i.get("width") or not i.get("height")]

    if missing_alt:
        deduct(min(10, len(missing_alt) * 2), "fail", "Images", f"{len(missing_alt)} image(s) missing alt attribute", "Alt text is required for accessibility & SEO.")
    if empty_alt:
        deduct(min(5, len(empty_alt)), "warn", "Images", f"{len(empty_alt)} image(s) have empty alt text", "Non-decorative images need descriptive alt text.")
    lazy_count = sum(1 for i in imgs if i.get("lazy"))
    if imgs and lazy_count == 0:
        deduct(4, "warn", "Performance", "No images use lazy loading", "Add loading='lazy' to below-the-fold images.")

    # ── Performance ──────────────────────────────────────────────────────────
    perf = s.get("performance", {})
    if perf.get("html_size_kb", 0) > 300:
        deduct(8, "warn", "Performance", f"Large HTML ({perf['html_size_kb']} KB)", "Consider optimizing HTML. Ideal < 100 KB.")
    if perf.get("ttfb_ms", 0) > 600:
        deduct(10, "warn", "Performance", f"Slow TTFB ({perf['ttfb_ms']} ms)", "Time to first byte > 600 ms. Aim for < 200 ms.")
    if perf.get("render_blocking_scripts", 0) > 0:
        deduct(min(10, perf["render_blocking_scripts"] * 3), "warn", "Performance",
               f"{perf['render_blocking_scripts']} render-blocking script(s)", "Add defer or async attributes.")

    # ── Structured data ───────────────────────────────────────────────────────
    sd = s.get("structured_data", [])
    if not sd:
        deduct(5, "warn", "Schema", "No structured data found", "Add JSON-LD schema markup.")

    # ── URL ───────────────────────────────────────────────────────────────────
    url_d = s.get("url", {})
    if url_d.get("protocol") != "https":
        deduct(15, "fail", "Security", "Page not served over HTTPS", "HTTPS is a Google ranking factor.")
    if url_d.get("has_uppercase"):
        deduct(3, "warn", "URL", "Uppercase letters in URL path", "Use lowercase URLs consistently.")
    if url_d.get("has_underscores"):
        deduct(2, "warn", "URL", "Underscores in URL path", "Prefer hyphens over underscores.")
    if url_d.get("path_depth", 0) > 4:
        deduct(3, "warn", "URL", f"Deep URL path (depth {url_d['path_depth']})", "Shallow URL structure is preferred.")

    # ── Security headers ─────────────────────────────────────────────────────
    hdrs = s.get("headers", {})
    if "x-content-type-options" not in hdrs:
        deduct(2, "warn", "Security", "Missing X-Content-Type-Options header", "Set to 'nosniff'.")
    if "x-frame-options" not in hdrs and "content-security-policy" not in hdrs:
        deduct(2, "warn", "Security", "Missing X-Frame-Options or CSP", "Prevents clickjacking attacks.")
    if "strict-transport-security" not in hdrs and url_d.get("protocol") == "https":
        deduct(3, "warn", "Security", "Missing HSTS header", "Enforce HTTPS with Strict-Transport-Security.")

    # ── Social tags ──────────────────────────────────────────────────────────
    social = s.get("social", {})
    if not social.get("og"):
        deduct(4, "warn", "Social", "No Open Graph tags", "Add og:title, og:description, og:image.")
    if not social.get("twitter"):
        deduct(2, "warn", "Social", "No Twitter Card tags", "Add twitter:card and related tags.")

    # ── Content ───────────────────────────────────────────────────────────────
    content = s.get("content", {})
    if content.get("word_count", 0) < 300:
        deduct(5, "warn", "Content", f"Low word count ({content.get('word_count',0)} words)", "Aim for at least 300+ words of quality content.")

    return max(0, score), issues


# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def severity_icon(sev: str) -> str:
    return {"fail": "🔴", "warn": "🟡", "pass": "🟢"}.get(sev, "⚪")


def score_color(score: int) -> str:
    if score >= 80: return "#00ff88"
    if score >= 60: return "#ffaa00"
    return "#ff3366"


def render_audit_row(icon, label, detail="", color=None):
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

def render_metric(label, value, color=None):
    color_style = f"color:{color};" if color else "color:var(--text);"
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-label'>{label}</div>
      <div class='metric-value' style='{color_style}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero'>
  <div class='hero-title'>TechSEO Auditor</div>
  <div class='hero-sub'>In-depth technical SEO analysis · Instant results</div>
</div>
""", unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    url_input = st.text_input("", placeholder="https://example.com/page", label_visibility="collapsed")
with col_btn:
    st.markdown("<div style='padding-top:0.35rem'></div>", unsafe_allow_html=True)
    run = st.button("Analyze →")

st.markdown("---")

if run and url_input:
    # Normalize URL
    url = url_input.strip()
    if not url.startswith("http"):
        url = "https://" + url

    with st.spinner("Crawling page and running audits…"):
        prog = st.progress(0)
        prog.progress(20)
        results = analyze_page(url)
        prog.progress(80)
        score, issues = compute_score(results)
        prog.progress(100)
        prog.empty()

    if results.get("fetch_error"):
        st.error(f"❌ Could not fetch page: {results['fetch_error']}")
        st.stop()

    s = results.get("sections", {})

    # ── OVERVIEW ROW ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric("SEO Score", f"{score}/100", score_color(score))
    with c2:
        sc = results.get("status_code", "—")
        render_metric("HTTP Status", str(sc), "#00ff88" if sc == 200 else "#ff3366")
    with c3:
        render_metric("TTFB", f"{results.get('ttfb_ms', results.get('ttfb',0)*1000):.0f} ms",
                      "#00ff88" if results.get("ttfb", 1) < 0.6 else "#ffaa00")
    with c4:
        render_metric("HTML Size", f"{s.get('performance',{}).get('html_size_kb','—')} KB")
    with c5:
        render_metric("Redirects", str(results.get("redirect_count", 0)),
                      "#00ff88" if results.get("redirect_count", 0) == 0 else "#ffaa00")

    st.markdown("---")

    # ── TABS ─────────────────────────────────────────────────────────────────
    tabs = st.tabs(["🎯 Issues", "📄 Meta", "🖼 Images", "🔗 Links", "📐 Structure", "⚡ Performance", "🛡 Security", "📊 Content", "🔧 Raw Data"])

    # ── TAB: Issues ──────────────────────────────────────────────────────────
    with tabs[0]:
        fails = [i for i in issues if i[0] == "fail"]
        warns = [i for i in issues if i[0] == "warn"]

        c1, c2, c3 = st.columns(3)
        with c1: render_metric("Critical Issues", str(len(fails)), "#ff3366" if fails else "#00ff88")
        with c2: render_metric("Warnings", str(len(warns)), "#ffaa00" if warns else "#00ff88")
        with c3: render_metric("Passed Checks", str(max(0, 30 - len(issues))), "#00ff88")

        if fails:
            st.markdown("<div class='section-header'>🔴 Critical Issues</div>", unsafe_allow_html=True)
            for sev, cat, msg, detail in fails:
                render_audit_row("🔴", f"[{cat}] {msg}", detail, "#ff3366")

        if warns:
            st.markdown("<div class='section-header'>🟡 Warnings</div>", unsafe_allow_html=True)
            for sev, cat, msg, detail in warns:
                render_audit_row("🟡", f"[{cat}] {msg}", detail, "#ffaa00")

        if not issues:
            st.success("✅ No issues found! This page looks technically healthy.")

    # ── TAB: Meta ────────────────────────────────────────────────────────────
    with tabs[1]:
        meta = s.get("meta", {})
        st.markdown("<div class='section-header'>Title Tag</div>", unsafe_allow_html=True)
        tl = meta.get("title_length", 0)
        tcolor = "#00ff88" if 50 <= tl <= 60 else ("#ffaa00" if 30 <= tl <= 70 else "#ff3366")
        render_metric("Title", meta.get("title") or "— missing —", tcolor)
        render_metric("Title Length", f"{tl} characters", tcolor)

        st.markdown("<div class='section-header'>Meta Description</div>", unsafe_allow_html=True)
        dl = meta.get("description_length", 0)
        dcolor = "#00ff88" if 120 <= dl <= 160 else ("#ffaa00" if 70 <= dl <= 200 else "#ff3366")
        render_metric("Description", meta.get("description") or "— missing —", dcolor)
        render_metric("Description Length", f"{dl} characters", dcolor)

        st.markdown("<div class='section-header'>Technical Meta</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            render_metric("Canonical URL", meta.get("canonical") or "— not set —",
                          "#00ff88" if meta.get("canonical") else "#ff3366")
            render_metric("Robots Directive", meta.get("robots", "not set"))
        with col2:
            render_metric("Viewport", meta.get("viewport") or "— missing —",
                          "#00ff88" if meta.get("viewport") else "#ff3366")
            render_metric("Language", meta.get("lang") or "— not set —",
                          "#00ff88" if meta.get("lang") else "#ffaa00")

        st.markdown("<div class='section-header'>Open Graph</div>", unsafe_allow_html=True)
        og = s.get("social", {}).get("og", {})
        if og:
            for k, v in og.items():
                render_metric(k, str(v)[:120])
        else:
            render_audit_row("🔴", "No Open Graph tags found", "Add og:title, og:description, og:image")

        st.markdown("<div class='section-header'>Twitter Cards</div>", unsafe_allow_html=True)
        tw = s.get("social", {}).get("twitter", {})
        if tw:
            for k, v in tw.items():
                render_metric(k, str(v)[:120])
        else:
            render_audit_row("🟡", "No Twitter Card tags found")

    # ── TAB: Images ──────────────────────────────────────────────────────────
    with tabs[2]:
        imgs = s.get("images", [])
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric("Total Images", str(len(imgs)))
        with c2:
            missing = sum(1 for i in imgs if not i["has_alt"])
            render_metric("Missing Alt", str(missing), "#ff3366" if missing else "#00ff88")
        with c3:
            empty = sum(1 for i in imgs if i["has_alt"] and i["alt_empty"])
            render_metric("Empty Alt", str(empty), "#ffaa00" if empty else "#00ff88")
        with c4:
            lazy = sum(1 for i in imgs if i.get("lazy"))
            render_metric("Lazy Loaded", f"{lazy}/{len(imgs)}", "#00ff88" if lazy == len(imgs) else "#ffaa00")

        if imgs:
            st.markdown("<div class='section-header'>Image Inventory</div>", unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame([{
                "src": i["src"],
                "alt": i["alt"] if i["alt"] is not None else "⚠ missing",
                "lazy": "✓" if i.get("lazy") else "—",
                "dims": f"{i['width']}×{i['height']}" if i.get("width") and i.get("height") else "—",
            } for i in imgs[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB: Links ───────────────────────────────────────────────────────────
    with tabs[3]:
        links = s.get("links", {})
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric("Total Links", str(links.get("total", 0)))
        with c2: render_metric("Internal", str(len(links.get("internal", []))))
        with c3: render_metric("External", str(len(links.get("external", []))))
        with c4: render_metric("Nofollow", str(links.get("nofollow_count", 0)))

        with st.expander(f"Internal Links ({len(links.get('internal',[]))})", expanded=False):
            for l in links.get("internal", [])[:50]:
                render_audit_row("🔵", l.get("text") or "(no anchor text)", l["href"],
                                 "#3366ff" if not l["nofollow"] else "#ffaa00")

        with st.expander(f"External Links ({len(links.get('external',[]))})", expanded=False):
            for l in links.get("external", [])[:30]:
                icon = "🔴" if l["nofollow"] else "🌐"
                render_audit_row(icon, l.get("text") or "(no anchor text)", l["href"])

    # ── TAB: Structure ───────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("<div class='section-header'>URL Analysis</div>", unsafe_allow_html=True)
        url_d = s.get("url", {})
        c1, c2 = st.columns(2)
        with c1:
            render_metric("Protocol", url_d.get("protocol", "—").upper(),
                          "#00ff88" if url_d.get("protocol") == "https" else "#ff3366")
            render_metric("Path Depth", str(url_d.get("path_depth", 0)),
                          "#00ff88" if url_d.get("path_depth", 0) <= 3 else "#ffaa00")
            render_metric("Has Uppercase", "Yes ⚠" if url_d.get("has_uppercase") else "No ✓",
                          "#ffaa00" if url_d.get("has_uppercase") else "#00ff88")
        with c2:
            render_metric("Underscores in path", "Yes ⚠" if url_d.get("has_underscores") else "No ✓",
                          "#ffaa00" if url_d.get("has_underscores") else "#00ff88")
            render_metric("Query string", "Yes" if url_d.get("has_params") else "No")
            render_metric("Path length", f"{url_d.get('path_length',0)} chars")

        st.markdown("<div class='section-header'>Heading Structure</div>", unsafe_allow_html=True)
        headings = s.get("headings", {})
        for level in range(1, 7):
            items = headings.get(f"h{level}", [])
            if items:
                color = "#00ff88" if level == 1 else "#3366ff" if level == 2 else "var(--text)"
                for h in items[:10]:
                    indent = "&nbsp;" * ((level - 1) * 4)
                    render_audit_row(f"H{level}", f"{indent}{h}", color=color)

        st.markdown("<div class='section-header'>Structured Data (JSON-LD)</div>", unsafe_allow_html=True)
        sd = s.get("structured_data", [])
        if sd:
            for i, item in enumerate(sd):
                schema_type = item.get("@type", "Unknown") if isinstance(item, dict) else "Parse error"
                with st.expander(f"Schema #{i+1}: {schema_type}"):
                    st.json(item)
        else:
            render_audit_row("🟡", "No structured data (JSON-LD) detected", "Consider adding schema markup.")

    # ── TAB: Performance ─────────────────────────────────────────────────────
    with tabs[5]:
        perf = s.get("performance", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            ttfb = perf.get("ttfb_ms", results.get("ttfb", 0) * 1000)
            render_metric("TTFB", f"{ttfb:.0f} ms",
                          "#00ff88" if ttfb < 200 else "#ffaa00" if ttfb < 600 else "#ff3366")
        with c2:
            render_metric("HTML Size", f"{perf.get('html_size_kb','—')} KB",
                          "#00ff88" if perf.get("html_size_kb", 0) < 100 else "#ffaa00")
        with c3:
            rb = perf.get("render_blocking_scripts", 0)
            render_metric("Render-Blocking Scripts", str(rb),
                          "#ff3366" if rb > 0 else "#00ff88")

        st.markdown("<div class='section-header'>Resource Counts</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: render_metric("External Scripts", str(perf.get("external_scripts", 0)))
        with c2: render_metric("Inline Scripts", str(perf.get("inline_scripts", 0)))
        with c3: render_metric("Stylesheets", str(perf.get("stylesheets", 0)))

        st.markdown("<div class='section-header'>Recommendations</div>", unsafe_allow_html=True)
        if ttfb > 600:
            render_audit_row("🔴", "Slow TTFB — investigate server response time, caching, CDN", "", "#ff3366")
        elif ttfb > 200:
            render_audit_row("🟡", "TTFB could be faster. Consider caching or CDN.", "", "#ffaa00")
        else:
            render_audit_row("🟢", "TTFB looks good!", "", "#00ff88")

        if rb > 0:
            render_audit_row("🔴", f"{rb} render-blocking script(s) in <head>",
                             "Add defer or async attributes to non-critical scripts.", "#ff3366")

    # ── TAB: Security ────────────────────────────────────────────────────────
    with tabs[6]:
        hdrs = s.get("headers", {})
        url_d = s.get("url", {})

        st.markdown("<div class='section-header'>HTTPS</div>", unsafe_allow_html=True)
        if url_d.get("protocol") == "https":
            render_audit_row("🟢", "Page served over HTTPS", color="#00ff88")
        else:
            render_audit_row("🔴", "Page NOT served over HTTPS", "HTTPS is a Google ranking signal.", "#ff3366")

        st.markdown("<div class='section-header'>Security Headers</div>", unsafe_allow_html=True)
        security_headers = {
            "strict-transport-security": ("HSTS", "Enforce HTTPS connections"),
            "x-content-type-options": ("X-Content-Type-Options", "Prevent MIME sniffing"),
            "x-frame-options": ("X-Frame-Options", "Prevent clickjacking"),
            "content-security-policy": ("Content-Security-Policy", "Control resource loading"),
            "referrer-policy": ("Referrer-Policy", "Control referrer information"),
            "permissions-policy": ("Permissions-Policy", "Control browser features"),
        }
        for key, (label, purpose) in security_headers.items():
            val = hdrs.get(key)
            if val:
                render_audit_row("🟢", f"{label}: {val[:60]}", purpose, "#00ff88")
            else:
                render_audit_row("🟡", f"{label}: missing", purpose, "#ffaa00")

        st.markdown("<div class='section-header'>All Response Headers</div>", unsafe_allow_html=True)
        if hdrs:
            import pandas as pd
            df = pd.DataFrame(list(hdrs.items()), columns=["Header", "Value"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("No response headers captured.")

    # ── TAB: Content ─────────────────────────────────────────────────────────
    with tabs[7]:
        content = s.get("content", {})
        c1, c2 = st.columns(2)
        with c1:
            wc = content.get("word_count", 0)
            render_metric("Word Count", str(wc),
                          "#00ff88" if wc >= 300 else "#ffaa00" if wc >= 150 else "#ff3366")
        with c2:
            render_metric("Paragraphs", str(content.get("paragraphs", 0)))

        st.markdown("<div class='section-header'>Top Keywords (by frequency)</div>", unsafe_allow_html=True)
        kws = content.get("top_keywords", [])
        if kws:
            import pandas as pd
            df = pd.DataFrame(kws, columns=["Keyword", "Count"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB: Raw Data ─────────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown("<div class='section-header'>Full Analysis JSON</div>", unsafe_allow_html=True)
        # Remove bulky image list for cleaner display
        display_results = {k: v for k, v in results.items() if k != "sections"}
        display_results["sections"] = {k: v for k, v in results.get("sections", {}).items() if k != "images"}
        st.json(display_results)

elif run and not url_input:
    st.warning("Please enter a URL to analyze.")
else:
    # Landing state
    st.markdown("""
    <div style='text-align:center;padding:3rem 0 2rem;'>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.8rem;color:var(--muted,#666);letter-spacing:2px;margin-bottom:2rem;text-transform:uppercase;'>
        What gets analyzed
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("📄", "Meta & Head", "Title, description, canonical, robots, charset, viewport"),
        ("🖼", "Images", "Alt text, lazy loading, dimensions"),
        ("⚡", "Performance", "TTFB, HTML size, render-blocking resources"),
        ("🔗", "Links", "Internal/external ratio, nofollow audit"),
        ("📐", "Structure", "H1–H6 hierarchy, JSON-LD schema, URL analysis"),
        ("🛡", "Security", "HTTPS, HSTS, CSP, X-Frame-Options, headers"),
        ("📣", "Social", "Open Graph tags, Twitter Cards"),
        ("📊", "Content", "Word count, keyword frequency, paragraph count"),
    ]
    for i, (icon, title, desc) in enumerate(items):
        col = [c1, c2, c3, c4][i % 4]
        with col:
            st.markdown(f"""
            <div style='background:var(--surface,#1a1a1a);border:1px solid var(--border,#333);border-radius:6px;
                        padding:1rem;margin-bottom:0.75rem;'>
              <div style='font-size:1.5rem;margin-bottom:0.4rem'>{icon}</div>
              <div style='font-family:Syne,sans-serif;font-weight:700;font-size:0.9rem;margin-bottom:0.3rem'>{title}</div>
              <div style='font-size:0.78rem;color:var(--muted,#666);font-family:IBM Plex Mono,monospace'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)