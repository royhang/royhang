#!/usr/bin/env python3
"""Zero-dependency GitHub Profile Neofetch Terminal SVG generator."""

import argparse
import datetime
import json
import math
import os
import sys
import unicodedata
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

WIDTH = 856
HEIGHT = 624
FONT_MONO = (
    "'JetBrains Mono', 'SF Mono', 'Fira Code', ui-monospace, "
    "SFMono-Regular, Menlo, Monaco, Consolas, monospace, "
    "'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', sans-serif"
)

THEMES: Dict[str, Dict[str, Any]] = {
    "dark": {
        "window_bg": "#0E1117",
        "titlebar_bg": "#131720",
        "border": "#242B35",
        "divider": "#1E242E",
        "surface": "#131720",
        "surface_border": "#21262D",
        "text_primary": "#E6EDF3",
        "text_secondary": "#8B949E",
        "text_dim": "#6E7681",
        "dot": "#30363D",
        "accent": "#79C0FF",
        "highlight": "#A5D6FF",
        "ascii_tones": ["#4A5568", "#8B949E", "#79C0FF", "#A5D6FF", "#E6EDF3"],
        "heatmap": ["#161B22", "#172A40", "#1F446E", "#3878C2", "#79C0FF"],
        "status_dot": "#79C0FF",
        "palette": ["#30363D", "#6E7681", "#8B949E", "#79C0FF", "#E6EDF3"],
    },
    "light": {
        "window_bg": "#FFFFFF",
        "titlebar_bg": "#F6F8FA",
        "border": "#D0D7DE",
        "divider": "#E5E9F0",
        "surface": "#F6F8FA",
        "surface_border": "#D8DEE4",
        "text_primary": "#1F2328",
        "text_secondary": "#57606A",
        "text_dim": "#8C959F",
        "dot": "#D0D7DE",
        "accent": "#0969DA",
        "highlight": "#0550AE",
        "ascii_tones": ["#AFB8C1", "#6E7781", "#0969DA", "#0550AE", "#1F2328"],
        "heatmap": ["#EBEDF0", "#CBE4FF", "#80BEFF", "#2F81F7", "#0969DA"],
        "status_dot": "#0969DA",
        "palette": ["#D0D7DE", "#8C959F", "#57606A", "#0969DA", "#1F2328"],
    },
}

# Each preset has 13 lines of (tone_index, segment_text) tuples.
# Tone indices map to theme["ascii_tones"]:
#   0 = faint/stars/frame, 1 = muted structure, 2 = ice-blue accent,
#   3 = bright highlight, 4 = crisp foreground
ASCII_PRESETS: Dict[str, List[List[Tuple[int, str]]]] = {
    "alpine": [
        [(0, "   ·        "), (3, "*"), (0, "             ·       ")],
        [(0, "        .        "), (3, "/\\"), (0, "        .      ")],
        [(0, "                "), (3, "/"), (4, "^^"), (2, "\\"), (0, "              ")],
        [(0, "   *    "), (3, "/\\"), (0, "     "), (3, "/"), (1, "::::"), (2, "\\"), (0, "      ·     ")],
        [(0, "       "), (3, "/"), (4, "^^"), (2, "\\"), (0, "   "), (3, "/"), (1, "::::::"), (2, "\\"), (0, "           ")],
        [(0, "      "), (3, "/"), (1, "::::"), (2, "\\"), (0, " "), (3, "/"), (1, "::::::::"), (2, "\\"), (0, "   "), (3, "/\\"), (0, "     ")],
        [(0, "     "), (3, "/"), (1, "::::::"), (2, "V"), (1, "::::::::::"), (2, "\\"), (0, " "), (3, "/"), (4, "^^"), (2, "\\"), (0, "    ")],
        [(0, "    "), (3, "/"), (1, ":::::::::::"), (4, "/\\"), (1, "::::::"), (2, "V::::\\"), (0, "   ")],
        [(0, "   "), (3, "/"), (1, ":::::::::::"), (4, "/  \\"), (1, ":::::::::::"), (2, "\\"), (0, "  ")],
        [(0, "  "), (3, "/"), (1, ":::::::::::"), (4, "/    \\"), (1, ":::::::::::"), (2, "\\"), (0, " ")],
        [(0, " "), (1, "/"), (2, "───────────────────────────────"), (1, "\\")],
        [(0, "  "), (0, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "), (0, "")],
        [(0, "   "), (2, "01"), (0, " · "), (1, "ALT 4,820m"), (0, " · "), (2, "CLEAR NIGHT")],
    ],
    "prism": [
        [(0, "          ·          "), (3, "*"), (0, "           ")],
        [(0, "               "), (3, "/\\"), (0, "                ")],
        [(0, "              "), (3, "/"), (4, "||"), (2, "\\"), (0, "               ")],
        [(0, "            "), (3, "/"), (1, "::"), (4, "||"), (1, "::"), (2, "\\"), (0, "             ")],
        [(0, "          "), (3, "/"), (1, "::::"), (4, "||"), (1, "::::"), (2, "\\"), (0, "           ")],
        [(0, "        "), (3, "/"), (1, "::::::"), (4, "||"), (1, "::::::"), (2, "\\"), (0, "         ")],
        [(0, "       "), (4, "<"), (2, "───────"), (3, "()"), (2, "───────"), (4, ">"), (0, "        ")],
        [(0, "        "), (2, "\\"), (1, "::::::"), (4, "||"), (1, "::::::"), (3, "/"), (0, "         ")],
        [(0, "          "), (2, "\\"), (1, "::::"), (4, "||"), (1, "::::"), (3, "/"), (0, "           ")],
        [(0, "            "), (2, "\\"), (1, "::"), (4, "||"), (1, "::"), (3, "/"), (0, "             ")],
        [(0, "              "), (2, "\\"), (4, "||"), (3, "/"), (0, "               ")],
        [(0, "               "), (2, "\\/"), (0, "                ")],
        [(0, "     "), (2, "PRISM"), (0, " · "), (1, "OCTAHEDRON"), (0, " · "), (2, "v1.0")],
    ],
    "orbit": [
        [(0, "   ·           "), (3, "*"), (0, "          .       ")],
        [(0, "          "), (2, ".--===--."), (0, "       ·      ")],
        [(0, "        "), (2, "/"), (1, "  .---.  "), (2, "\\"), (0, "             ")],
        [(0, "       "), (3, "|"), (1, "  / "), (4, "o"), (1, "  \\  "), (2, "|"), (0, "    "), (3, "*"), (0, "      ")],
        [(0, "    "), (2, ".--"), (3, "+"), (1, "-|  "), (4, "@"), (1, "  |-"), (2, "--."), (0, "         ")],
        [(0, "   "), (2, "(   "), (4, "\\"), (1, "  \\___/  "), (4, "/"), (2, "   )"), (0, "        ")],
        [(0, "    "), (2, "`---"), (4, "\\_______/"), (2, "---'"), (0, "        ")],
        [(0, "        "), (2, "\\"), (1, "         "), (2, "/"), (0, "     "), (3, "*"), (0, "       ")],
        [(0, "         "), (2, "`--===--'"), (0, "               ")],
        [(0, "     ·            "), (1, "apogee 408km"), (0, "   ")],
        [(0, "          "), (0, "───────────────"), (0, "        ")],
        [(0, "       "), (1, "inclination 51.6°"), (0, "         ")],
        [(0, "     "), (2, "ORBIT"), (0, " · "), (1, "TELEMETRY"), (0, " · "), (2, "OK")],
    ],
}

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    createdAt
    followers {
      totalCount
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      isFork: false
      privacy: PUBLIC
      orderBy: {field: STARGAZERS, direction: DESC}
    ) {
      totalCount
      nodes {
        name
        description
        stargazerCount
        forkCount
        primaryLanguage {
          name
        }
      }
    }
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          description
          stargazerCount
          forkCount
          primaryLanguage {
            name
          }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            contributionLevel
          }
        }
      }
    }
  }
}
"""

LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def char_width(ch: str) -> int:
    """Return terminal display width of a single Unicode character."""
    if unicodedata.combining(ch):
        return 0
    ea = unicodedata.east_asian_width(ch)
    return 2 if ea in ("W", "F") else 1


def display_width(text: str) -> int:
    """Return total terminal display column width of a string."""
    return sum(char_width(ch) for ch in text)


def truncate_width(text: str, max_cols: int) -> str:
    """Truncate text cleanly with ellipsis so its display width <= max_cols.

    For space-separated text, prefers breaking on a word boundary when doing so
    retains most of the available line width, avoiding awkward mid-word cuts.
    """
    clean = " ".join((text or "").split())
    if display_width(clean) <= max_cols:
        return clean
    if max_cols <= 1:
        return "…"[:max_cols]

    limit = max_cols - 1
    words = clean.split(" ")
    if len(words) > 1:
        kept: List[str] = []
        cols = 0
        for word in words:
            w = display_width(word)
            needed = w if not kept else cols + 1 + w
            if needed <= limit:
                kept.append(word)
                cols = needed
            else:
                break
        if kept and cols >= limit * 0.6:
            trimmed = " ".join(kept).rstrip(" ,;:-·/")
            if trimmed:
                return trimmed + "…"

    out: List[str] = []
    cols = 0
    for ch in clean:
        w = char_width(ch)
        if cols + w > limit:
            break
        out.append(ch)
        cols += w
    return "".join(out).rstrip(" ,;:-·/") + "…"


def wrap_two_lines(text: str, max_cols: int) -> Tuple[str, str]:
    """Wrap text into at most two lines bounded by max_cols each."""
    clean = " ".join((text or "No description provided.").split())
    if display_width(clean) <= max_cols:
        return clean, ""

    # Break first line at word boundary when possible, unless next token is a long CJK/unspaced run.
    words = clean.split(" ")
    if len(words) > 1:
        line1 = ""
        idx = 0
        for i, word in enumerate(words):
            candidate = word if not line1 else line1 + " " + word
            if display_width(candidate) <= max_cols:
                line1 = candidate
                idx = i + 1
            else:
                break
        if line1 and (idx >= len(words) or display_width(line1) >= max_cols * 0.65 or display_width(words[idx]) <= max_cols * 0.4):
            rest = " ".join(words[idx:])
            return line1, truncate_width(rest, max_cols)

    # Fallback character-level split (e.g. CJK or very long single token).
    buf: List[str] = []
    cols = 0
    split_at = 0
    for i, ch in enumerate(clean):
        w = char_width(ch)
        if cols + w > max_cols:
            split_at = i
            break
        buf.append(ch)
        cols += w
    else:
        return clean, ""
    return "".join(buf), truncate_width(clean[split_at:].lstrip(), max_cols)


def format_number(n: int) -> str:
    """Format integers compactly above 10k or with commas below."""
    if n >= 10000:
        return "{:.1f}k".format(n / 1000.0)
    return "{:,}".format(n)


def compute_tenure(created_iso: str) -> str:
    """Compute account tenure in years from ISO-8601 timestamp."""
    if not created_iso:
        return "1.0 yrs"
    try:
        dt = datetime.datetime.strptime(created_iso[:10], "%Y-%m-%d").date()
        days = max(0, (datetime.date.today() - dt).days)
        years = days / 365.25
        if years < 1.0:
            months = max(1, int(days / 30))
            return "{} mos".format(months)
        return "{:.1f} yrs".format(years)
    except ValueError:
        return "1.0 yrs"


def build_demo_data() -> Dict[str, Any]:
    """Generate deterministic realistic demo profile and 53x7 heatmap."""
    weeks: List[List[int]] = []
    total_contribs = 0
    for w in range(53):
        col: List[int] = []
        for d in range(7):
            # Deterministic organic rhythm: weekday bursts, calmer weekends, active recent months.
            wave = math.sin(w * 0.42 + d * 0.9) + math.cos(w * 0.19 - d * 0.5)
            recency = 0.55 if w > 34 else 0.15
            weekend_penalty = -0.75 if d in (0, 6) else 0.35
            score = wave + recency + weekend_penalty
            if score < 0.15:
                lvl = 0
                cnt = 0
            elif score < 0.75:
                lvl = 1
                cnt = 2
            elif score < 1.35:
                lvl = 2
                cnt = 5
            elif score < 1.95:
                lvl = 3
                cnt = 9
            else:
                lvl = 4
                cnt = 14
            col.append(lvl)
            total_contribs += cnt
        weeks.append(col)

    return {
        "commits_1y": 1482,
        "total_stars": 642,
        "repo_count": 38,
        "tenure": "4.6 yrs",
        "total_contributions": total_contribs,
        "synced_date": datetime.date.today().isoformat(),
        "has_pinned": True,
        "repos": [
            {
                "name": "kestrel-kv",
                "description": "Raft-backed embedded key-value store written in Go with snapshot streaming.",
                "stars": 318,
                "forks": 29,
                "language": "Go",
            },
            {
                "name": "tracepane",
                "description": "Minimalist TUI log & OpenTelemetry span inspector for terminal workflows.",
                "stars": 204,
                "forks": 18,
                "language": "Rust",
            },
            {
                "name": "monolith-ui",
                "description": "Zero-runtime design tokens and accessible primitives for TypeScript apps.",
                "stars": 120,
                "forks": 11,
                "language": "TypeScript",
            },
        ],
        "weeks": weeks,
    }


def fetch_github_data(username: str, token: str, pinned_count: int) -> Dict[str, Any]:
    """Fetch user statistics, pinned repos, and contribution calendar via GraphQL."""
    payload = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json",
            "User-Agent": "github-profile-terminal-generator",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError("GitHub API HTTP {}: {}".format(err.code, detail))
    except urllib.error.URLError as err:
        raise RuntimeError("GitHub API connection error: {}".format(err.reason))

    if body.get("errors"):
        raise RuntimeError("GitHub GraphQL errors: {}".format(json.dumps(body["errors"])))

    user = (body.get("data") or {}).get("user")
    if not user:
        raise RuntimeError("GitHub user '{}' not found.".format(username))

    owned_nodes = (user.get("repositories") or {}).get("nodes") or []
    repo_count = int((user.get("repositories") or {}).get("totalCount") or len(owned_nodes))
    total_stars = sum(int(r.get("stargazerCount") or 0) for r in owned_nodes)

    pinned_nodes = [
        r for r in ((user.get("pinnedItems") or {}).get("nodes") or []) if r and r.get("name")
    ]
    has_pinned = len(pinned_nodes) > 0
    seen = {r["name"] for r in pinned_nodes}
    combined = list(pinned_nodes)
    for r in owned_nodes:
        if len(combined) >= pinned_count:
            break
        r_name = (r or {}).get("name") or ""
        if r_name and r_name.lower() != username.lower() and r_name not in seen:
            combined.append(r)
            seen.add(r_name)

    repos: List[Dict[str, Any]] = []
    for r in combined[:pinned_count]:
        lang = (r.get("primaryLanguage") or {}).get("name") or "Markdown"
        repos.append(
            {
                "name": r.get("name") or "untitled",
                "description": r.get("description") or "No description provided.",
                "stars": int(r.get("stargazerCount") or 0),
                "forks": int(r.get("forkCount") or 0),
                "language": lang,
            }
        )

    contrib = user.get("contributionsCollection") or {}
    commits_1y = int(contrib.get("totalCommitContributions") or 0) + int(
        contrib.get("restrictedContributionsCount") or 0
    )
    calendar = contrib.get("contributionCalendar") or {}
    total_contributions = int(calendar.get("totalContributions") or 0)

    raw_weeks = calendar.get("weeks") or []
    weeks: List[List[int]] = []
    for wk in raw_weeks[-53:]:
        days = wk.get("contributionDays") or []
        col = [LEVEL_MAP.get(d.get("contributionLevel") or "NONE", 0) for d in days]
        while len(col) < 7:
            col.append(0)
        weeks.append(col[:7])
    while len(weeks) < 53:
        weeks.insert(0, [0] * 7)

    return {
        "commits_1y": commits_1y,
        "total_stars": total_stars,
        "repo_count": repo_count,
        "tenure": compute_tenure(user.get("createdAt") or ""),
        "total_contributions": total_contributions,
        "synced_date": datetime.date.today().isoformat(),
        "has_pinned": has_pinned,
        "repos": repos,
        "weeks": weeks,
    }


def render_ascii_lines(config: Dict[str, Any], t: Dict[str, Any], x: int, y_start: float) -> List[str]:
    """Render the left-column multi-tone ASCII art block."""
    art_name = str(config.get("ascii_art") or "alpine").lower()
    custom_lines = config.get("custom_ascii") or []
    tones = t["ascii_tones"]
    out: List[str] = []

    if art_name == "custom" and custom_lines:
        for idx, raw_line in enumerate(custom_lines[:13]):
            y = y_start + idx * 15.5
            color = tones[2] if idx == 0 else tones[4]
            out.append(
                '  <text x="{x}" y="{y:.1f}" fill="{color}" font-size="11.5" '
                'xml:space="preserve">{txt}</text>'.format(
                    x=x, y=y, color=color, txt=escape(str(raw_line))
                )
            )
        return out

    preset = ASCII_PRESETS.get(art_name, ASCII_PRESETS["alpine"])
    for idx, segments in enumerate(preset[:13]):
        y = y_start + idx * 15.5
        tspans = "".join(
            '<tspan fill="{color}">{txt}</tspan>'.format(
                color=tones[min(max(tone, 0), len(tones) - 1)],
                txt=escape(seg),
            )
            for tone, seg in segments
        )
        out.append(
            '  <text x="{x}" y="{y:.1f}" font-size="11.5" xml:space="preserve">{inner}</text>'.format(
                x=x, y=y, inner=tspans
            )
        )
    return out


def render_svg(config: Dict[str, Any], data: Dict[str, Any], mode: str) -> str:
    """Render a complete standalone terminal SVG for the requested theme mode."""
    t = THEMES[mode]
    display_name = truncate_width(str(config.get("display_name") or config.get("username") or "dev"), 24)
    tagline = truncate_width(str(config.get("tagline") or "Building quiet, fast software."), 64)
    synced_date = str(data.get("synced_date") or datetime.date.today().isoformat())

    lines: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'.format(
            w=WIDTH,
            h=HEIGHT,
            label=escape("{} GitHub Terminal Profile".format(display_name)),
        ),
        "  <defs>",
        '    <clipPath id="window-clip">',
        '      <rect x="0.5" y="0.5" width="{w}" height="{h}" rx="12" />'.format(
            w=WIDTH - 1, h=HEIGHT - 1
        ),
        "    </clipPath>",
        "    <style>",
        "      text {{ font-family: {font}; }}".format(font=FONT_MONO),
        "    </style>",
        "  </defs>",
        "",
        "  <!-- Terminal window shell -->",
        '  <g clip-path="url(#window-clip)">',
        '    <rect x="0.5" y="0.5" width="{w}" height="{h}" rx="12" fill="{bg}" />'.format(
            w=WIDTH - 1, h=HEIGHT - 1, bg=t["window_bg"]
        ),
        '    <rect x="0" y="0" width="{w}" height="38" fill="{tb}" />'.format(
            w=WIDTH, tb=t["titlebar_bg"]
        ),
        '    <line x1="0" y1="38.5" x2="{w}" y2="38.5" stroke="{bd}" stroke-width="1" />'.format(
            w=WIDTH, bd=t["border"]
        ),
        '    <rect x="0" y="588" width="{w}" height="36" fill="{tb}" />'.format(
            w=WIDTH, tb=t["titlebar_bg"]
        ),
        '    <line x1="0" y1="588.5" x2="{w}" y2="588.5" stroke="{bd}" stroke-width="1" />'.format(
            w=WIDTH, bd=t["border"]
        ),
        "  </g>",
        '  <rect x="0.5" y="0.5" width="{w}" height="{h}" rx="12" fill="none" stroke="{bd}" stroke-width="1" />'.format(
            w=WIDTH - 1, h=HEIGHT - 1, bd=t["border"]
        ),
        "",
        "  <!-- Titlebar controls & session metadata -->",
        '  <circle cx="22" cy="19" r="5" fill="{dot}" />'.format(dot=t["dot"]),
        '  <circle cx="38" cy="19" r="5" fill="{dot}" />'.format(dot=t["dot"]),
        '  <circle cx="54" cy="19" r="5" fill="{dot}" />'.format(dot=t["dot"]),
        '  <text x="428" y="23" text-anchor="middle" fill="{sec}" font-size="11.5" font-weight="500">{title}</text>'.format(
            sec=t["text_secondary"],
            title=escape("{}@github — zsh — 108×34".format(display_name)),
        ),
        '  <text x="824" y="23" text-anchor="end" fill="{dim}" font-size="10.5">{meta}</text>'.format(
            dim=t["text_dim"],
            meta=escape("UTF-8 · SYNCED {}".format(synced_date)),
        ),
        "",
        "  <!-- Section 1: Neofetch hero -->",
        '  <text x="32" y="64" font-size="12">'
        '<tspan fill="{acc}" font-weight="600">❯ </tspan>'
        '<tspan fill="{pri}" font-weight="600">neofetch</tspan>'
        '<tspan fill="{dim}"> --profile</tspan>'
        "</text>".format(acc=t["accent"], pri=t["text_primary"], dim=t["text_dim"]),
    ]

    lines.extend(render_ascii_lines(config, t, x=32, y_start=92.0))

    # Right column identity header
    lines.extend(
        [
            '  <text x="324" y="90" font-size="15" font-weight="700">'
            '<tspan fill="{acc}">{name}</tspan>'
            '<tspan fill="{dim}" font-weight="400">@</tspan>'
            '<tspan fill="{pri}">github</tspan>'
            "</text>".format(
                acc=t["accent"],
                name=escape(display_name),
                dim=t["text_dim"],
                pri=t["text_primary"],
            ),
            '  <line x1="324" y1="100" x2="824" y2="100" stroke="{div}" stroke-width="1" />'.format(
                div=t["divider"]
            ),
            '  <line x1="324" y1="100" x2="432" y2="100" stroke="{acc}" stroke-width="1.5" />'.format(
                acc=t["accent"]
            ),
            '  <text x="324" y="119" fill="{sec}" font-size="11.5">{tag}</text>'.format(
                sec=t["text_secondary"], tag=escape(tagline)
            ),
        ]
    )

    spec_rows = [
        ("Role", config.get("role") or "Software Engineer"),
        ("Stack", config.get("stack") or "TypeScript · Go · Python"),
        ("Focus", config.get("focus") or "Systems & Developer Tools"),
        ("Location", config.get("location") or "Earth"),
        ("Links", config.get("links") or "github.com"),
    ]
    for idx, (label, raw_val) in enumerate(spec_rows):
        y = 143.0 + idx * 17.5
        val = truncate_width(str(raw_val), 57)
        lines.extend(
            [
                '  <text x="324" y="{y:.1f}" fill="{acc}" font-size="11.5" font-weight="600">{lbl}</text>'.format(
                    y=y, acc=t["accent"], lbl=escape(label)
                ),
                '  <text x="398" y="{y:.1f}" fill="{dim}" font-size="11.5">:</text>'.format(
                    y=y, dim=t["text_dim"]
                ),
                '  <text x="414" y="{y:.1f}" fill="{pri}" font-size="11.5">{val}</text>'.format(
                    y=y, pri=t["text_primary"], val=escape(val)
                ),
            ]
        )

    # Telemetry box (4 equal 125px columns inside x=324..824)
    metrics = [
        ("COMMITS (1Y)", format_number(int(data["commits_1y"]))),
        ("STARS", format_number(int(data["total_stars"]))),
        ("REPOS", format_number(int(data["repo_count"]))),
        ("TENURE", str(data["tenure"])),
    ]
    lines.append(
        '  <rect x="324" y="234" width="500" height="52" rx="7" fill="{surf}" stroke="{sbd}" stroke-width="1" />'.format(
            surf=t["surface"], sbd=t["surface_border"]
        )
    )
    for idx, (m_label, m_val) in enumerate(metrics):
        cx = 324 + idx * 125 + 16
        if idx > 0:
            vx = 324 + idx * 125
            lines.append(
                '  <line x1="{vx}" y1="244" x2="{vx}" y2="276" stroke="{div}" stroke-width="1" />'.format(
                    vx=vx, div=t["divider"]
                )
            )
        lines.append(
            '  <text x="{cx}" y="252" fill="{dim}" font-size="9.5" letter-spacing="0.6">{lbl}</text>'.format(
                cx=cx, dim=t["text_dim"], lbl=escape(m_label)
            )
        )
        lines.append(
            '  <text x="{cx}" y="274" fill="{pri}" font-size="14.5" font-weight="700">{val}</text>'.format(
                cx=cx, pri=t["text_primary"], val=escape(m_val)
            )
        )

    # Divider 1
    lines.append(
        '  <line x1="32" y1="304" x2="824" y2="304" stroke="{div}" stroke-width="1" />'.format(
            div=t["divider"]
        )
    )

    # Section 2: Featured Repositories
    repos = list(data["repos"])[:3]
    n_repos = len(repos)
    has_pinned = bool(data.get("has_pinned", True))
    repo_cmd = " repo list --pinned --limit {}".format(max(1, n_repos)) if has_pinned else " repo list --source --limit {}".format(max(1, n_repos))
    repo_badge = "PUBLIC · PINNED" if has_pinned else "PUBLIC · FEATURED"

    lines.extend(
        [
            "",
            "  <!-- Section 2: Featured repositories -->",
            '  <text x="32" y="325" font-size="12">'
            '<tspan fill="{acc}" font-weight="600">❯ </tspan>'
            '<tspan fill="{pri}" font-weight="600">gh</tspan>'
            '<tspan fill="{dim}">{cmd}</tspan>'
            "</text>".format(acc=t["accent"], pri=t["text_primary"], dim=t["text_dim"], cmd=escape(repo_cmd)),
            '  <text x="824" y="325" text-anchor="end" fill="{dim}" font-size="10" letter-spacing="0.6">{badge}</text>'.format(
                dim=t["text_dim"], badge=escape(repo_badge)
            ),
        ]
    )

    card_h = 84
    card_gap = 12
    card_y = 338
    if n_repos == 0:
        lines.extend(
            [
                '  <rect x="32" y="{cy}" width="792" height="{ch}" rx="7" fill="{surf}" stroke="{sbd}" stroke-width="1" />'.format(
                    cy=card_y, ch=card_h, surf=t["surface"], sbd=t["surface_border"]
                ),
                '  <text x="428" y="{ty}" text-anchor="middle" fill="{dim}" font-size="11.5">No public repositories yet.</text>'.format(
                    ty=card_y + 46, dim=t["text_dim"]
                ),
            ]
        )
    else:
        layout_specs = {
            3: (256, 21, 32),
            2: (390, 34, 52),
            1: (792, 64, 104),
        }
        card_w, name_cols, desc_cols = layout_specs.get(n_repos, (256, 21, 32))
        for idx, repo in enumerate(repos):
            cx = 32 + idx * (card_w + card_gap)
            name = truncate_width(str(repo["name"]), name_cols)
            stars = "★ {}".format(format_number(int(repo["stars"])))
            d1, d2 = wrap_two_lines(str(repo["description"]), desc_cols)
            lang = truncate_width(str(repo["language"]), 18)
            forks = "⑂ {}".format(format_number(int(repo["forks"])))

            lines.extend(
                [
                    '  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="7" fill="{surf}" stroke="{sbd}" stroke-width="1" />'.format(
                        cx=cx, cy=card_y, cw=card_w, ch=card_h, surf=t["surface"], sbd=t["surface_border"]
                    ),
                    '  <text x="{tx}" y="{ty}" fill="{acc}" font-size="12" font-weight="600">{name}</text>'.format(
                        tx=cx + 14, ty=card_y + 22, acc=t["accent"], name=escape(name)
                    ),
                    '  <text x="{sx}" y="{ty}" text-anchor="end" fill="{sec}" font-size="11">{stars}</text>'.format(
                        sx=cx + card_w - 14, ty=card_y + 22, sec=t["text_secondary"], stars=escape(stars)
                    ),
                    '  <text x="{tx}" y="{dy}" fill="{sec}" font-size="10.5">{d1}</text>'.format(
                        tx=cx + 14, dy=card_y + 41, sec=t["text_secondary"], d1=escape(d1)
                    ),
                ]
            )
            if d2:
                lines.append(
                    '  <text x="{tx}" y="{dy}" fill="{sec}" font-size="10.5">{d2}</text>'.format(
                        tx=cx + 14, dy=card_y + 56, sec=t["text_secondary"], d2=escape(d2)
                    )
                )
            lines.extend(
                [
                    '  <circle cx="{dx}" cy="{dcy}" r="3.5" fill="{acc}" />'.format(
                        dx=cx + 18, dcy=card_y + 70, acc=t["accent"]
                    ),
                    '  <text x="{lx}" y="{ly}" fill="{dim}" font-size="10.5">{lang}</text>'.format(
                        lx=cx + 27, ly=card_y + 73.5, dim=t["text_dim"], lang=escape(lang)
                    ),
                    '  <text x="{fx}" y="{ly}" text-anchor="end" fill="{dim}" font-size="10.5">{forks}</text>'.format(
                        fx=cx + card_w - 14, ly=card_y + 73.5, dim=t["text_dim"], forks=escape(forks)
                    ),
                ]
            )

    # Divider 2
    lines.append(
        '  <line x1="32" y1="438" x2="824" y2="438" stroke="{div}" stroke-width="1" />'.format(
            div=t["divider"]
        )
    )

    # Section 3: Contribution Matrix
    total_contribs = format_number(int(data["total_contributions"]))
    lines.extend(
        [
            "",
            "  <!-- Section 3: Contribution matrix -->",
            '  <text x="32" y="458" font-size="12">'
            '<tspan fill="{acc}" font-weight="600">❯ </tspan>'
            '<tspan fill="{pri}" font-weight="600">git</tspan>'
            '<tspan fill="{dim}"> log --graph --since="1 year"</tspan>'
            "</text>".format(acc=t["accent"], pri=t["text_primary"], dim=t["text_dim"]),
            '  <text x="698" y="458" text-anchor="end" fill="{sec}" font-size="10.5">{cnt} contributions in the last year</text>'.format(
                sec=t["text_secondary"], cnt=escape(total_contribs)
            ),
            '  <text x="734" y="458" text-anchor="end" fill="{dim}" font-size="9.5">Less</text>'.format(
                dim=t["text_dim"]
            ),
        ]
    )

    # 5-level legend swatches between x=740 and x=791
    for lvl_idx, hex_color in enumerate(t["heatmap"]):
        sx = 740 + lvl_idx * 11
        lines.append(
            '  <rect x="{sx}" y="450" width="8" height="8" rx="2" fill="{col}" />'.format(
                sx=sx, col=hex_color
            )
        )
    lines.append(
        '  <text x="824" y="458" text-anchor="end" fill="{dim}" font-size="9.5">More</text>'.format(
            dim=t["text_dim"]
        )
    )

    # 53 x 7 heatmap cells
    grid_x = 32
    grid_y = 472
    step = 15
    for w_idx, col_levels in enumerate(data["weeks"][:53]):
        rx_pos = grid_x + w_idx * step
        for d_idx, lvl in enumerate(col_levels[:7]):
            ry_pos = grid_y + d_idx * step
            fill = t["heatmap"][min(max(int(lvl), 0), 4)]
            lines.append(
                '  <rect x="{x}" y="{y}" width="11" height="11" rx="2.5" fill="{fill}" />'.format(
                    x=rx_pos, y=ry_pos, fill=fill
                )
            )

    # Bottom status bar
    lines.extend(
        [
            "",
            "  <!-- Bottom status bar -->",
            '  <circle cx="36" cy="606" r="3.5" fill="{dot}" />'.format(dot=t["status_dot"]),
            '  <text x="46" y="610" fill="{dim}" font-size="10.5">online · github-actions · {mode}</text>'.format(
                dim=t["text_dim"], mode=mode
            ),
        ]
    )

    for p_idx, p_col in enumerate(t["palette"]):
        px = 738 + p_idx * 14
        lines.append(
            '  <rect x="{px}" y="602" width="10" height="8" rx="2" fill="{col}" />'.format(
                px=px, col=p_col
            )
        )
    lines.append(
        '  <rect x="816" y="599" width="7" height="13" rx="1.5" fill="{acc}" />'.format(
            acc=t["accent"]
        )
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def load_config(path: str) -> Dict[str, Any]:
    """Load profile.config.json with sensible defaults."""
    if not os.path.exists(path):
        raise FileNotFoundError("Config file not found: {}".format(path))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Neofetch-style GitHub profile SVGs.")
    parser.add_argument(
        "--config",
        default="profile.config.json",
        help="Path to profile configuration JSON (default: profile.config.json)",
    )
    parser.add_argument(
        "--out-dir",
        default="assets",
        help="Output directory for generated SVGs (default: assets)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Render with deterministic offline demo data instead of calling GitHub API.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    pinned_count = max(1, min(3, int(config.get("pinned_count") or 3)))

    if args.demo:
        data = build_demo_data()
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        if not token:
            print("Error: GITHUB_TOKEN or GH_TOKEN is required unless --demo is passed.", file=sys.stderr)
            return 1

        cfg_user = str(config.get("username") or "").strip()
        env_user = os.environ.get("GITHUB_USERNAME", "").strip()
        if cfg_user and cfg_user != "your-username":
            username = cfg_user
        elif env_user:
            username = env_user
        else:
            print("Error: Set 'username' in profile.config.json or GITHUB_USERNAME env var.", file=sys.stderr)
            return 1

        data = fetch_github_data(username=username, token=token, pinned_count=pinned_count)

    os.makedirs(args.out_dir, exist_ok=True)
    for mode in ("dark", "light"):
        svg_text = render_svg(config=config, data=data, mode=mode)
        out_path = os.path.join(args.out_dir, "terminal-{}.svg".format(mode))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_text)
        print("Generated {}".format(out_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
