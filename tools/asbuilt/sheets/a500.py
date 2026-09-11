"""A-500 — ANNEX. Spatial and creative systems, drawn as an enlarged plan
with a scroll-driven camera path and camera stations — the convention used on
architectural plans to mark rendered views. Every station is one system.
"""

from __future__ import annotations

import math

from lib.sheet import Sheet
from lib.svg import fmt
from lib.symbols import checkpoint, drawing_title, keynote, tag
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "ANNEX"
SUBTITLE = "Spatial and creative systems. Camera stations mark rendered views; the path is scroll-driven."
DESC = ("Enlarged plan of the Annex room. A dashed camera path runs through the room with numbered camera "
        "station symbols; each station carries a system tag: immersive 3D website, Haya-Tower-Garden, YOLO 3D "
        "scanning, Project Opus, local RAG orchestration, AI training mechanics, Huawei watch face. "
        "A keynote list on the right gives input, verb and output for each.")

# (key, station x, station y, view angle deg)
STATIONS = [
    ("immersive3d", 300, 300, 20),
    ("towergarden", 560, 240, 60),
    ("yolo3d",      820, 330, 150),
    ("opus",        1000, 560, 250),
    ("localrag",    760, 720, 200),
    ("aitrain",     480, 640, 300),
    ("watchface",   300, 820, 340),
]


def _sys(data, key):
    return next(s for s in data["systems"] if s["key"] == key)


def camera(s: Sheet, x: float, y: float, ang: float, n: str) -> None:
    p = s.pal
    a = math.radians(ang)
    L, spread = 74, math.radians(24)
    x1, y1 = x + L * math.cos(a - spread), y + L * math.sin(a - spread)
    x2, y2 = x + L * math.cos(a + spread), y + L * math.sin(a + spread)
    s.doc.path(f"M{fmt(x)},{fmt(y)} L{fmt(x1)},{fmt(y1)} L{fmt(x2)},{fmt(y2)} z", fill="url(#secure)")
    s.doc.path(f"M{fmt(x1)},{fmt(y1)} L{fmt(x)},{fmt(y)} L{fmt(x2)},{fmt(y2)}", stroke=p.ink, width=HAIR)
    s.doc.circle(x, y, 9, stroke=p.ink, width=MEDIUM, fill=p.paper)
    s.doc.circle(x, y, 3, fill=p.ink)
    s.text(f"C{n}", x - 14, y - 12, 9.5, anchor="end", color=p.grey)


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "A-500", TITLE, SUBTITLE, DESC, zones_active=("05",))
    p = s.pal
    clouded = lambda sy: data["statuses"][sy["status"]]["cloud"]

    # Room
    rx, ry, rw, rh = 160, 170, 1040, 740
    s.doc.rect(rx, ry, rw, rh, stroke=p.ink, width=MEDIUM)
    checkpoint(s, rx + 300, ry, 44, "h", swing=1)
    s.text("ANNEX", rx + rw / 2, ry + 36, 15, anchor="middle", tracking=0.16)
    s.doc.rect(rx + rw / 2 - 19, ry + 44, 38, 18, stroke=p.ink, width=HAIR)
    s.text("05", rx + rw / 2, ry + 57, 11, anchor="middle")

    # Camera path
    pts = [(x, y) for _, x, y, _ in STATIONS]
    d = "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)
    s.doc.path(d, stroke=p.ink, width=HAIR, stroke_dasharray="10 6")
    s.doc.add(f'<circle r="6" fill="none" stroke="{p.ink}" stroke-width="{MEDIUM}"><animateMotion dur="14s" repeatCount="indefinite" path="{d}"/></circle>')
    s.text("SCROLL-DRIVEN CAMERA PATH", pts[0][0] - 60, pts[0][1] - 60, 10, color=p.grey, tracking=0.14)
    s.doc.line(pts[0][0] - 60, pts[0][1] - 52, pts[0][0] - 6, pts[0][1] - 6, stroke=p.ink, width=HAIR)

    # Stations + tags
    for i, (key, x, y, ang) in enumerate(STATIONS):
        sy = _sys(data, key)
        camera(s, x, y, ang, str(i + 1))
        tag(s, x + 18, y + 14, sy["no"], clouded=clouded(sy))
        keynote(s, x + 18 + 58 + 22, y + 26, str(i + 1))

    s.text("ENLARGED FROM A-100", rx + rw - 16, ry + rh - 14, 9.5, anchor="end", color=p.grey, tracking=0.1)
    drawing_title(s, 160, 1008, "1", "ANNEX — ENLARGED PLAN WITH CAMERA STATIONS", width=640)

    # Keynotes: input -> verb -> output
    kx, ky = 1270, 176
    s.text("KEYNOTES — STATIONS", kx, ky, 13, tracking=0.16)
    s.doc.line(kx, ky + 10, 1700, ky + 10, stroke=p.ink, width=HEAVY)
    y = ky + 44
    for i, (key, *_r) in enumerate(STATIONS):
        sy = _sys(data, key)
        keynote(s, kx + 11, y - 5, str(i + 1))
        s.text(f"{sy['no']}   {sy['name'].upper()}", kx + 34, y, 11.5, tracking=0.04)
        st = sy["status"]
        if data["statuses"][st]["cloud"]:
            s.text(st, 1700, y, 9.5, anchor="end", color=p.red, tracking=0.1)
        y += 18
        s.text(sy["input"].upper(), kx + 34, y, 9.5, color=p.grey, tracking=0.04)
        y += 16
        s.text(f"{sy['verb']}", kx + 34, y, 10.5, tracking=0.2)
        vw = s.width(sy["verb"], 10.5, 0.2)
        s.doc.line(kx + 34 + vw + 10, y - 4, kx + 34 + vw + 34, y - 4, stroke=p.ink, width=HAIR)
        s.doc.path(f"M{fmt(kx+34+vw+34)},{fmt(y-4)} l-6,-3.5 v7 z", fill=p.ink)
        out = s.wrap(sy["output"].upper(), 9.5, 1700 - (kx + 34 + vw + 44))
        s.text(out[0], kx + 34 + vw + 44, y, 9.5, color=p.grey, tracking=0.04)
        y += 16
        for ln in out[1:2]:
            s.text(ln, kx + 34, y, 9.5, color=p.grey, tracking=0.04)
            y += 16
        y += 22

    return {"main": s}
