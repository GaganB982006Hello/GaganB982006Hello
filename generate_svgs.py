import json
import os
import random
from datetime import datetime
from urllib.request import urlopen, Request

USERNAME = "GaganB982006Hello"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

random.seed(42)

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
# Shine peak: near-white tinted green flash for the glint moment
GLOW   = ["#21262d", "#3dffa0", "#57ffb0", "#8dffcc", "#c8ffe8"]

def pick_level():
    r = random.random()
    if r < 0.35: return 0
    if r < 0.55: return 1
    if r < 0.72: return 2
    if r < 0.87: return 3
    return 4


def fetch_real_contributions(username):
    """Fetch last-year contribution grid for username; return (grid_53x7, months_list) or None."""
    try:
        req = Request(
            f"https://github-contributions-api.jogruber.de/v4/{username}?y=last",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        data = json.loads(urlopen(req, timeout=12).read().decode("utf-8"))
        contribs = data.get("contributions", [])
        if not contribs:
            return None

        start_dt = datetime.strptime(contribs[0]["date"], "%Y-%m-%d")
        # GitHub grid starts on Sunday (python weekday(): Mon=0..Sun=6 -> Sun=0)
        start_dow = (start_dt.weekday() + 1) % 7
        cells = [None] * start_dow + contribs

        # Pad to full weeks and keep the most recent 53 weeks
        while len(cells) % 7 != 0:
            cells.append(None)
        weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]
        if len(weeks) > 53:
            weeks = weeks[-53:]
        while len(weeks) < 53:
            weeks.insert(0, [None] * 7)

        grid = []
        month_positions = []
        last_month = None
        for col_idx, week in enumerate(weeks):
            col_levels = []
            for day in week:
                if day is None:
                    col_levels.append(0)
                else:
                    col_levels.append(min(int(day.get("level", 0)), 4))
                    dt = datetime.strptime(day["date"], "%Y-%m-%d")
                    if dt.day <= 7 and dt.month != last_month:
                        last_month = dt.month
                        month_positions.append((col_idx, dt.strftime("%b")))
            grid.append(col_levels)

        return grid, month_positions
    except Exception as e:
        print(f"[WARN] Could not fetch live contributions ({e}); using fallback pattern")
        return None


WEEKS   = 53
DAYS    = 7
SQ      = 11
GAP     = 3
STEP    = SQ + GAP   # 14
GRAPH_X = 34
GRAPH_Y = 28
MONTHS  = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ==============================================================================
# github-contribution-animation.svg
# Diagonal (slant) reveal with bright glow flash on each square
# ==============================================================================
def build_contrib():
    W, H = 850, 165
    lines = []

    real_data = fetch_real_contributions(USERNAME)
    if real_data:
        grid, month_positions = real_data
        print(f"[OK] Loaded live GitHub contributions for {USERNAME}")
    else:
        grid = [[pick_level() for _ in range(DAYS)] for _ in range(WEEKS)]
        wpm = WEEKS / 12
        month_positions = [(round(i * wpm), m) for i, m in enumerate(MONTHS)]

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    lines.append('<defs>')
    lines.append(
        '<filter id="cellglow" x="-70%" y="-70%" width="240%" height="240%">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    lines.append('</defs>')

    # card background
    lines.append(f'<rect width="{W}" height="{H}" rx="16" fill="#0d1117" stroke="#30363d" stroke-width="1"/>')

    # month labels
    last_x = -100
    for col_idx, m in month_positions:
        x = GRAPH_X + col_idx * STEP
        if x - last_x >= 28:
            lines.append(f'<text x="{x}" y="18" fill="#8b949e" font-size="10" font-family="system-ui,sans-serif">{m}</text>')
            last_x = x

    # weekday labels
    for i, lbl in enumerate(["Mon", "", "Wed", "", "Fri", "", ""]):
        if lbl:
            y = GRAPH_Y + i * STEP + SQ - 1
            lines.append(f'<text x="8" y="{y}" fill="#8b949e" font-size="9" font-family="system-ui,sans-serif">{lbl}</text>')

    anim_dur = 4.5
    pause    = 2.5
    total    = anim_dur + pause

    SLANT    = 0.6
    max_diag = (WEEKS - 1) + (DAYS - 1) * SLANT

    for col in range(WEEKS):
        for row in range(DAYS):
            lvl   = grid[col][row]
            color = COLORS[lvl]
            glow  = GLOW[lvl]
            x     = GRAPH_X + col * STEP
            y     = GRAPH_Y + row * STEP
            sq_id = f"s{col}_{row}"

            diag  = col + row * SLANT
            t_rev = diag / max_diag * anim_dur

            t0 = t_rev / total
            t1 = min(t0 + 0.012, 0.97)
            t2 = min(t0 + 0.05,  0.99)

            fa = ' filter="url(#cellglow)"' if lvl >= 3 else ''

            lines.append(
                f'<rect id="{sq_id}" x="{x}" y="{y}" width="{SQ}" height="{SQ}" rx="2" fill="{color}" opacity="0"{fa}>'
            )
            lines.append(
                f'<animate attributeName="opacity" values="0;0;1;1" '
                f'keyTimes="0;{t0:.4f};{t1:.4f};1" '
                f'dur="{total}s" repeatCount="indefinite"/>'
            )

            if lvl > 0:
                lines.append(
                    f'<animate attributeName="fill" '
                    f'values="{color};{color};{glow};{color}" '
                    f'keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" '
                    f'dur="{total}s" repeatCount="indefinite" '
                    f'calcMode="spline" keySplines="0 0 1 1;0.1 0 0.2 1;0.4 0 0.6 1"/>'
                )

            lines.append('</rect>')

            if lvl > 0:
                hl_x = x + 2
                hl_y = y + 2
                lines.append(
                    f'<rect x="{hl_x}" y="{hl_y}" width="4" height="2" rx="1" '
                    f'fill="white" opacity="0" pointer-events="none">'
                )
                lines.append(
                    f'<animate attributeName="opacity" '
                    f'values="0;0;0.55;0" '
                    f'keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" '
                    f'dur="{total}s" repeatCount="indefinite" '
                    f'calcMode="spline" keySplines="0 0 1 1;0 0 0.3 1;0.5 0 1 1"/>'
                )
                lines.append('</rect>')

    lines.append(
        '<style>'
        'rect[id^="s"]{transition:filter .15s}'
        'rect[id^="s"]:hover{filter:brightness(1.65) drop-shadow(0 0 5px #39d353)}'
        '</style>'
    )

    lines.append('</svg>')
    return "\n".join(lines)


# ==============================================================================
# terminal-banner.svg (optional animated whoami terminal)
# ==============================================================================
def build_terminal():
    W, H = 900, 520
    lines = []

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    lines.append('<defs>')
    lines.append(
        '<radialGradient id="bg1" cx="20%" cy="30%" r="60%">'
        '<stop offset="0%" stop-color="#0d2137"/>'
        '<stop offset="100%" stop-color="#0d1117"/>'
        '<animate attributeName="cx" values="20%;80%;20%" dur="10s" repeatCount="indefinite"/>'
        '<animate attributeName="cy" values="30%;70%;30%" dur="12s" repeatCount="indefinite"/>'
        '</radialGradient>'
        '<radialGradient id="bg2" cx="80%" cy="70%" r="50%">'
        '<stop offset="0%" stop-color="#0a1a2e" stop-opacity="0.8"/>'
        '<stop offset="100%" stop-color="#0d1117" stop-opacity="0"/>'
        '</radialGradient>'
    )
    lines.append(
        '<linearGradient id="glass" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#161b22" stop-opacity="0.95"/>'
        '<stop offset="100%" stop-color="#0d1117" stop-opacity="0.98"/>'
        '</linearGradient>'
        '<linearGradient id="headerGrad" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#1c2128"/>'
        '<stop offset="100%" stop-color="#161b22"/>'
        '</linearGradient>'
        '<linearGradient id="borderGlow" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#00ffcc" stop-opacity="0.6"/>'
        '<stop offset="50%" stop-color="#0ea5e9" stop-opacity="0.3"/>'
        '<stop offset="100%" stop-color="#7c3aed" stop-opacity="0.6"/>'
        '<animate attributeName="x1" values="0%;100%;0%" dur="4s" repeatCount="indefinite"/>'
        '<animate attributeName="x2" values="100%;0%;100%" dur="4s" repeatCount="indefinite"/>'
        '</linearGradient>'
    )
    lines.append(
        '<pattern id="scanlines" x="0" y="0" width="900" height="3" patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="1" x2="900" y2="1" stroke="white" stroke-opacity="0.03" stroke-width="1"/>'
        '</pattern>'
        '<pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">'
        '<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ffffff" stroke-width="0.3" stroke-opacity="0.04"/>'
        '</pattern>'
    )
    lines.append('<clipPath id="termclip"><rect x="30" y="30" width="840" height="460" rx="14"/></clipPath>')
    lines.append('</defs>')

    lines.append(f'<rect width="{W}" height="{H}" fill="url(#bg1)"/>')
    lines.append(f'<rect width="{W}" height="{H}" fill="url(#bg2)"/>')
    lines.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')

    pts = [(random.randint(50, 850), random.randint(50, 470),
            round(random.uniform(0.3, 1.2), 1), round(random.uniform(3, 9), 1))
           for _ in range(28)]
    for px, py, pr, pdur in pts:
        dy = random.randint(-30, 30)
        lines.append(
            f'<circle cx="{px}" cy="{py}" r="{pr}" fill="#00ffcc" opacity="0.15">'
            f'<animate attributeName="cy" values="{py};{py+dy};{py}" dur="{pdur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.05;0.25;0.05" dur="{pdur}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    lines.append(
        '<rect x="28" y="28" width="844" height="464" rx="15" fill="none" stroke="url(#borderGlow)" stroke-width="2">'
        '<animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite"/>'
        '</rect>'
    )

    lines.append('<g>')
    lines.append(
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0;0 -4;0 0" dur="4s" repeatCount="indefinite" '
        'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
    )
    lines.append('<rect x="30" y="30" width="840" height="460" rx="14" fill="url(#glass)" stroke="#30363d" stroke-width="1"/>')
    lines.append('<rect x="30" y="30" width="840" height="80" rx="14" fill="white" fill-opacity="0.025" clip-path="url(#termclip)"/>')
    lines.append('<rect x="30" y="30" width="840" height="44" rx="14" fill="url(#headerGrad)"/>')
    lines.append('<rect x="30" y="58" width="840" height="16" fill="url(#headerGrad)"/>')
    lines.append('<line x1="30" y1="74" x2="870" y2="74" stroke="#30363d" stroke-width="1"/>')

    for fc, bx in [("#ff5f57", 55), ("#febc2e", 79), ("#28c840", 103)]:
        lines.append(f'<circle cx="{bx}" cy="52" r="7" fill="{fc}"/>')

    lines.append('<text x="450" y="57" text-anchor="middle" fill="#8b949e" font-size="13" font-family="ui-monospace,monospace">~/portfolio — gagan-b.vercel.app</text>')
    lines.append('<rect x="30" y="74" width="840" height="416" fill="url(#scanlines)" clip-path="url(#termclip)"/>')

    lines.append(
        '<rect x="30" y="74" width="840" height="2" fill="white" fill-opacity="0.04" clip-path="url(#termclip)">'
        '<animate attributeName="y" values="74;490;74" dur="5s" repeatCount="indefinite" '
        'calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
        '</rect>'
    )

    TX = 56
    prompt_chars = list("$ whoami")
    typing_dur = 8.0
    char_dur   = 0.12
    delete_start = 1.5

    lines.append('<text x="56" y="106" font-family="ui-monospace,Menlo,monospace" font-size="14" fill="#00ffcc">')
    for i, ch in enumerate(prompt_chars):
        a0 = i * char_dur / typing_dur
        a1 = min((len(prompt_chars) * char_dur + delete_start + (len(prompt_chars) - i - 1) * char_dur * 0.5) / typing_dur, 0.98)
        lines.append(
            f'<tspan opacity="0">{ch}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{a0:.3f};{min(a0+0.01,0.99):.3f};{a1:.3f};{min(a1+0.02,0.99):.3f};1" '
            f'dur="{typing_dur}s" repeatCount="indefinite"/>'
            f'</tspan>'
        )
    lines.append('</text>')

    lines.append(
        f'<rect x="56" y="92" width="8" height="14" fill="#00ffcc" rx="1">'
        f'<animate attributeName="x" values="{56};{56+len(prompt_chars)*8.5:.0f};{56}" '
        f'keyTimes="0;{len(prompt_chars)*char_dur/typing_dur:.3f};1" '
        f'dur="{typing_dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    reveal_start = len(prompt_chars) * char_dur + 0.3
    sections = [
        ("------------------------------------------------------", "#30363d", 122),
        ("Name:      Gagan B",                                    "#e6edf3", 140),
        ("Role:      CS Engineering Student · Full Stack &amp; AI/ML", "#00ffcc", 158),
        ("Stack:     Java  Python  C  C++  JS  TS  React  Node",  "#8b949e", 176),
        ("ML/Data:   NumPy  Pandas  Matplotlib  Streamlit",       "#8b949e", 194),
        ("GitHub:    25 repositories  |  900+ contributions/yr",  "#8b949e", 212),
        ("Stars:     150+",                                       "#febc2e", 230),
        ("Focus:     AI-driven web solutions &amp; automation",   "#39d353", 248),
        ("------------------------------------------------------", "#30363d", 266),
    ]

    for idx, (text, color, y_pos) in enumerate(sections):
        at = min((reveal_start + idx * 0.28) / typing_dur, 0.97)
        lines.append(
            f'<text x="{TX}" y="{y_pos}" font-family="ui-monospace,Menlo,monospace" '
            f'font-size="12.5" fill="{color}" opacity="0">'
            f'{text}'
            f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{at:.3f};{min(at+0.04,0.99):.3f};1" '
            f'dur="{typing_dur}s" repeatCount="indefinite"/>'
            f'</text>'
        )

    lines.append('</g>')
    lines.append('</svg>')
    return "\n".join(lines)


if __name__ == "__main__":
    contrib_path = os.path.join(OUT_DIR, "github-contribution-animation.svg")
    with open(contrib_path, "w", encoding="utf-8") as f:
        f.write(build_contrib())
    print(f"[OK] {contrib_path} written")
