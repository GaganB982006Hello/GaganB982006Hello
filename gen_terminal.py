"""
gen_terminal.py
===============
Generates TWO SVG files for Gagan B's GitHub profile:

  terminal-card.svg  (840 × 875)
    • Portrait / avatar converted to animated ASCII art
    • Each row sweeps left->right with cursor block
    • macOS chrome:  GaganB982006Hello@github: ~$ ./portrait.sh
    • Footer:        GaganB982006Hello@github:~$ whoami  Gagan B

  info-card.svg  (480 × 430)
    • neofetch-style info card
    • Staggered slide-up + fade-in per row
    • macOS chrome:  GaganB982006Hello@github: ~$ neofetch
    • Sections: identity header, About, Stack, Highlights

Run:
    pip install Pillow
    python3 gen_terminal.py
"""

import sys, os, html as _html
from urllib.request import urlopen, Request
from io import BytesIO

# ─── CONFIG ──────────────────────────────────────────────────────────────────
USERNAME     = "GaganB982006Hello"
DISPLAY_NAME = "Gagan B"
ROLE         = "CS Engineering Student · Full Stack & AI/ML"

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def xe(s): return _html.escape(str(s), quote=True)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1 — terminal-card.svg  (ASCII art portrait)
# ═══════════════════════════════════════════════════════════════════════════════

local_photo = next(
    (p for p in (os.path.join(OUT_DIR, "gagan-profile.png"), os.path.join(OUT_DIR, "gagan-profile.jpg")) if os.path.exists(p)),
    None,
)
img_bytes = None
if local_photo:
    with open(local_photo, "rb") as f:
        img_bytes = f.read()
    print(f"[OK] Loaded local portrait ({os.path.basename(local_photo)}, {len(img_bytes):,} bytes)")
else:
    print("[..] Fetching GitHub avatar …")
    try:
        req = Request(
            f"https://avatars.githubusercontent.com/{USERNAME}?size=400",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        img_bytes = urlopen(req, timeout=20).read()
        print(f"[OK] Avatar fetched  ({len(img_bytes):,} bytes)")
    except Exception as e:
        sys.exit(f"[ERR] Fetch failed: {e}")

try:
    from PIL import Image
except ImportError:
    sys.exit("[ERR] Pillow not installed.  Run: pip install Pillow")

# Density ramp: space = bright pixel, @ = dark pixel
ASCII_CHARS = "  `.-':=+*csS%#@"
ART_W, ART_H = 100, 53

img = Image.open(BytesIO(img_bytes)).convert("L")
img = img.resize((ART_W, ART_H), Image.LANCZOS)
pixels = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())

rows = []
for r in range(ART_H):
    row = ""
    for c in range(ART_W):
        px  = pixels[r * ART_W + c]
        idx = int((255 - px) / 255 * (len(ASCII_CHARS) - 1))
        row += ASCII_CHARS[idx]
    rows.append(row)

print(f"[OK] ASCII art generated ({ART_W}×{ART_H})")

W1      = 840
ROW_H   = 15
ROW_Y0  = 37
FONT_SZ = 12.9
ROW_DUR = 0.11
TEXT_W  = 800
TEXT_X  = 20

FOOTER_LINE_Y = ROW_Y0 + ART_H * ROW_H   # 832
FOOTER_TEXT_Y = FOOTER_LINE_Y + 19        # 851
H1            = FOOTER_LINE_Y + 43        # 875

WHOAMI_TEXT = f"{USERNAME}@github:~$ whoami "
CURSOR_X    = TEXT_X + len(WHOAMI_TEXT) * 7.73 + len(DISPLAY_NAME) * 7.73 + 6

rows_svg = ""
for i, row in enumerate(rows):
    begin  = i * ROW_DUR
    y_top  = ROW_Y0 + i * ROW_H
    y_text = y_top + 11.1
    safe   = xe(row)

    rows_svg += (
        f'<clipPath id="r{i}">'
        f'<rect x="{TEXT_X}" y="{y_top:.1f}" height="{ROW_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{TEXT_W}" '
        f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
        f'</rect></clipPath>\n'
        f'<g clip-path="url(#r{i})">'
        f'<text xml:space="preserve" x="{TEXT_X}" y="{y_text:.1f}" '
        f'fill="#c9d1d9" font-size="{FONT_SZ}" '
        f'textLength="{TEXT_W}" lengthAdjust="spacing">{safe}</text>'
        f'</g>\n'
        f'<rect y="{y_top+1:.1f}" width="8" height="13" fill="#c9d1d9" opacity="0">'
        f'<animate attributeName="x" from="{TEXT_X}" to="{TEXT_X+TEXT_W}" '
        f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{begin:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{begin+ROW_DUR:.3f}s"/>'
        f'</rect>\n'
    )

svg1 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W1}" height="{H1}" viewBox="0 0 {W1} {H1}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#111722"/>
    <stop offset="1" stop-color="#0d1117"/>
  </linearGradient>
</defs>
<rect width="{W1}" height="{H1}" rx="12" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="{W1-1}" height="{H1-1}" rx="12" fill="none" stroke="#30363d" stroke-width="1"/>
<line x1="0" y1="30" x2="{W1}" y2="30" stroke="#30363d"/>
<circle cx="20" cy="15.0" r="5" fill="#ff5f56"/>
<circle cx="36" cy="15.0" r="5" fill="#ffbd2e"/>
<circle cx="52" cy="15.0" r="5" fill="#27c93f"/>
<text x="{W1/2:.1f}" y="19.0" fill="#7d8590" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ ./portrait.sh</text>
{rows_svg}
<line x1="0" y1="{FOOTER_LINE_Y:.1f}" x2="{W1}" y2="{FOOTER_LINE_Y:.1f}" stroke="#30363d"/>
<text x="20" y="{FOOTER_TEXT_Y:.1f}" fill="#7d8590" font-size="13">{USERNAME}@github:~$ whoami <tspan fill="#c9d1d9">{DISPLAY_NAME}</tspan></text>
<rect x="{CURSOR_X:.0f}" y="{FOOTER_TEXT_Y-13:.1f}" width="8" height="14" fill="#c9d1d9">
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>
</rect>
</svg>"""

out1 = os.path.join(OUT_DIR, "terminal-card.svg")
with open(out1, "w", encoding="utf-8") as f:
    f.write(svg1)
print(f"[OK] terminal-card.svg written  ({W1}×{H1}px, {os.path.getsize(out1)//1024} KB)")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2 — info-card.svg  (neofetch-style info card)
# ═══════════════════════════════════════════════════════════════════════════════

W2, H2 = 480, 420

C_ORANGE = "#ffa657"
C_BLUE   = "#58a6ff"
C_GREEN  = "#3fb950"
C_CYAN   = "#22d3ee"
C_WHITE  = "#c9d1d9"
C_DIM    = "#30363d"
C_GRAY   = "#7d8590"

INFO_ROWS = [
    {"type": "header"},
    {"type": "section", "label": "— About"},
    {"type": "field", "label": "Role", "value": "CS Student · Full Stack & AI/ML"},
    {"type": "field", "label": "Focus", "value": "Web Apps, AI/ML & Automation"},
    {"type": "field", "label": "Education", "value": "B.E. CSE (CGPA 8.35) · VSBCETC"},
    {"type": "section", "label": "— Stack"},
    {"type": "field", "label": "Languages", "value": "Java, Python, C, C++, JS, TS"},
    {"type": "field", "label": "Frontend", "value": "HTML5, CSS3, Tailwind, React"},
    {"type": "field", "label": "Backend", "value": "Node.js, Streamlit, JavaFX"},
    {"type": "field", "label": "Data/ML", "value": "NumPy, Pandas, Matplotlib"},
    {"type": "field", "label": "Tools", "value": "Git, GitHub, VS Code, Jupyter"},
    {"type": "section", "label": "— Highlights"},
    {"type": "bullet", "value": "Built AI-driven web & ML applications"},
    {"type": "bullet", "value": "TechSaksham & IBM SkillsBuild AI/ML Intern"},
    {"type": "bullet", "value": "25+ GitHub repos · Active on LeetCode"},
]

SLIDE_DUR = 0.4
STEP      = 0.06
TOP_Y     = 60.0
LINE_H    = 20.5

parts = []
cur_t = 0.15
cur_y = TOP_Y

for row in INFO_ROWS:
    t  = cur_t
    ks = "0.2 0.8 0.2 1"

    if row["type"] == "header":
        ulen = len(USERNAME)
        rule_x1 = 20 + (ulen + 1 + 6) * 8.6 + 6
        parts.append(
            f'<g opacity="0" transform="translate(0,5)">'
            f'<text x="20" y="{cur_y}" font-size="14" font-weight="700">'
            f'<tspan fill="{C_GREEN}">{xe(USERNAME)}</tspan>'
            f'<tspan fill="{C_GRAY}">@</tspan>'
            f'<tspan fill="{C_CYAN}">github</tspan>'
            f'</text>'
            f'<line x1="{rule_x1:.0f}" y1="{cur_y-4:.1f}" x2="460" y2="{cur_y-4:.1f}" stroke="{C_DIM}" stroke-opacity="0.8"/>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze" calcMode="spline" keySplines="{ks}"/>'
            f'</g>'
        )
        cur_y += LINE_H * 1.1
        cur_t += STEP

    elif row["type"] == "section":
        label   = row["label"]
        rule_x1 = 20 + len(label) * 7.8
        parts.append(
            f'<g opacity="0" transform="translate(0,5)">'
            f'<text x="20" y="{cur_y}" fill="{C_BLUE}" font-size="12.5" font-weight="700">{xe(label)}</text>'
            f'<line x1="{rule_x1:.0f}" y1="{cur_y-4:.1f}" x2="460" y2="{cur_y-4:.1f}" stroke="{C_DIM}" stroke-opacity="0.8"/>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze" calcMode="spline" keySplines="{ks}"/>'
            f'</g>'
        )
        cur_y += LINE_H * 1.5
        cur_t += STEP * 2

    elif row["type"] == "field":
        parts.append(
            f'<g opacity="0" transform="translate(0,5)">'
            f'<text x="20" y="{cur_y}" fill="{C_ORANGE}" font-size="12.5" font-weight="700">{xe(row["label"])}</text>'
            f'<text x="112" y="{cur_y}" fill="{C_WHITE}" font-size="12.5">{xe(row["value"])}</text>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze" calcMode="spline" keySplines="{ks}"/>'
            f'</g>'
        )
        cur_y += LINE_H
        cur_t += STEP

    elif row["type"] == "bullet":
        dot_cy = cur_y - 4
        parts.append(
            f'<g opacity="0" transform="translate(0,5)">'
            f'<circle cx="23" cy="{dot_cy:.1f}" r="2.5" fill="{C_GREEN}"/>'
            f'<text x="34" y="{cur_y}" fill="{C_WHITE}" font-size="12.5">{xe(row["value"])}</text>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{t:.2f}s" dur="{SLIDE_DUR}s" fill="freeze" calcMode="spline" keySplines="{ks}"/>'
            f'</g>'
        )
        cur_y += LINE_H
        cur_t += STEP

H2 = max(420, int(cur_y) + 30)
info_parts_svg = "\n".join(parts)

svg2 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<defs>
  <linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#111722"/>
    <stop offset="1" stop-color="#0d1117"/>
  </linearGradient>
</defs>
<rect width="{W2}" height="{H2}" rx="12" fill="url(#ibg)"/>
<rect x="0.5" y="0.5" width="{W2-1}" height="{H2-1}" rx="12" fill="none" stroke="#30363d"/>
<line x1="0" y1="30" x2="{W2}" y2="30" stroke="#30363d"/>
<circle cx="20" cy="15.0" r="5" fill="#ff5f56"/>
<circle cx="36" cy="15.0" r="5" fill="#ffbd2e"/>
<circle cx="52" cy="15.0" r="5" fill="#27c93f"/>
<text x="{W2/2:.1f}" y="19.0" fill="{C_GRAY}" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ neofetch</text>
{info_parts_svg}
</svg>"""

out2 = os.path.join(OUT_DIR, "info-card.svg")
with open(out2, "w", encoding="utf-8") as f:
    f.write(svg2)
print(f"[OK] info-card.svg written       ({W2}×{H2}px, {os.path.getsize(out2)//1024} KB)")
