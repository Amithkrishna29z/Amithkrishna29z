# -*- coding: utf-8 -*-
import io, os

W = 900
TITLEBAR = 40
PAD_X = 26
LINE_H = 30
FONT = 17.0
CHW = FONT * 0.601          # monospace advance
TOP = TITLEBAR + 30

GREEN="#3fb950"; WHITE="#e6edf3"; DIM="#8b949e"; CYAN="#22d3ee"; PINK="#f75c7e"; YELLOW="#fbbf24"

# (kind, text, colour)  kind: cmd | out
LINES = [
    ("cmd", "whoami", None),
    ("out", "Amith Krishnan — software developer", DIM),
    ("cmd", "cat ~/.config/interests", None),
    ("out", "compilers · concurrency · developer tooling", CYAN),
    ("cmd", "git log --oneline -1", None),
    ("out", "01ab9fe  Hope this works", DIM),
    ("cmd", "./build.sh --everything", None),
    ("out", "[ OK ]  98 repos · 12 languages · 174 tests green", GREEN),
]

# ---- build a timeline -------------------------------------------------------
t = 0.6
sched = []          # (start, end) for the reveal of each line
for kind, text, _ in LINES:
    n = len(("$ " + text) if kind == "cmd" else text)
    dur = max(0.45, n * 0.042) if kind == "cmd" else 0.28
    sched.append((t, t + dur))
    t += dur + (0.28 if kind == "cmd" else 0.65)
PROMPT_AT = t
TOTAL = t + 5.6                      # final blinking prompt, then loop

H = TOP + LINE_H * (len(LINES) + 1) + 24

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def kt(x):
    return round(max(0.0, min(1.0, x / TOTAL)), 5)

def type_anim(attr, start, end, n, full, is_x=False):
    """discrete per-character animation of `attr` from 0..full over [start,end]"""
    vals, times = ["0" if not is_x else str(PAD_X)], [0.0]
    vals.append(vals[0]); times.append(kt(start))
    for i in range(1, n + 1):
        v = CHW * i
        vals.append(str(round(PAD_X + v, 2) if is_x else round(v, 2)))
        times.append(kt(start + (end - start) * i / n))
    vals.append(str(round(full, 2))); times.append(1.0)
    # keyTimes must be non-decreasing and unique-enough
    out_v, out_t = [vals[0]], [0.0]
    for v, tt in zip(vals[1:], times[1:]):
        if tt <= out_t[-1]:
            tt = out_t[-1] + 1e-5
        out_v.append(v); out_t.append(min(tt, 1.0))
    out_t[-1] = 1.0
    return ('<animate attributeName="%s" dur="%ss" repeatCount="indefinite" calcMode="discrete" '
            'values="%s" keyTimes="%s"/>' % (attr, TOTAL, ";".join(out_v),
                                             ";".join(str(round(x, 5)) for x in out_t)))

o = io.StringIO()
o.write('<?xml version="1.0" encoding="UTF-8"?>\n')
o.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'font-family="ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace" '
        'role="img" aria-label="Animated terminal: whoami, interests, git log, build output">\n' % (W, H, W, H))

o.write('''<defs>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#f75c7e"/><stop offset="50%" stop-color="#8a2be2"/><stop offset="100%" stop-color="#22d3ee"/>
  </linearGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#010409"/>
  </linearGradient>
''')
for i, (start, end) in enumerate(sched):
    o.write('  <clipPath id="c%d"><rect x="%d" y="%d" width="0" height="%d">%s</rect></clipPath>\n'
            % (i, PAD_X, TOP + i * LINE_H - FONT, LINE_H,
               type_anim("width", start, end,
                         len(("$ " + LINES[i][1]) if LINES[i][0] == "cmd" else LINES[i][1]),
                         W - PAD_X * 2)))
o.write('</defs>\n')

# window chrome
o.write('<rect x="1" y="1" width="%d" height="%d" rx="12" fill="url(#bg)" stroke="url(#glow)" stroke-width="2"/>\n' % (W - 2, H - 2))
o.write('<path d="M1 13a12 12 0 0 1 12-12h874a12 12 0 0 1 12 12v27H1z" fill="#161b22"/>\n')
o.write('<line x1="1" y1="40" x2="899" y2="40" stroke="#30363d"/>\n')
for j, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    o.write('<circle cx="%d" cy="20" r="6" fill="%s"/>\n' % (24 + j * 22, c))
o.write('<text x="450" y="26" text-anchor="middle" font-size="13" fill="#7d8590">amith@github: ~/profile</text>\n')

# lines
for i, (kind, text, colour) in enumerate(LINES):
    y = TOP + i * LINE_H
    o.write('<g clip-path="url(#c%d)">' % i)
    if kind == "cmd":
        o.write('<text x="%d" y="%d" font-size="%s" fill="%s">$ <tspan fill="%s">%s</tspan></text>'
                % (PAD_X, y, FONT, GREEN, WHITE, esc(text)))
    else:
        o.write('<text x="%d" y="%d" font-size="%s" fill="%s">%s</text>'
                % (PAD_X, y, FONT, colour, esc(text)))
    o.write('</g>\n')

    if kind == "cmd":  # cursor that rides along with the typing
        s, e = sched[i]
        o.write('<rect y="%d" width="10" height="20" fill="%s" opacity="0">%s%s</rect>\n'
                % (y - FONT + 3, PINK,
                   type_anim("x", s, e, len("$ " + text), PAD_X + CHW * len("$ " + text), is_x=True),
                   '<animate attributeName="opacity" dur="%ss" repeatCount="indefinite" calcMode="discrete" '
                   'values="0;1;0;0" keyTimes="0;%s;%s;1"/>' % (TOTAL, kt(s), kt(e + 0.12))))

# final blinking prompt
fy = TOP + len(LINES) * LINE_H
o.write('<g opacity="0"><animate attributeName="opacity" dur="%ss" repeatCount="indefinite" calcMode="discrete" values="0;1;1" keyTimes="0;%s;1"/>'
        % (TOTAL, kt(PROMPT_AT)))
o.write('<text x="%d" y="%d" font-size="%s" fill="%s">$</text>' % (PAD_X, fy, FONT, GREEN))
o.write('<rect x="%d" y="%d" width="10" height="20" fill="%s"><animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;0.5;1"/></rect>'
        % (PAD_X + int(CHW * 2), fy - FONT + 3, PINK))
o.write('</g>\n</svg>\n')

dest = os.path.join(os.getcwd(), "assets", "terminal.svg")
with open(dest, "w", encoding="utf-8") as f:
    f.write(o.getvalue())
print("wrote", dest, os.path.getsize(dest), "bytes | loop", round(TOTAL,2), "s | canvas", W, "x", H)
