"""D-501 — CAPTURE BOUNDARY DETAIL. HayaScope HyperSync.

The one rule that defines the product, drawn: the extension's interface
sits outside the capture boundary. Everything the tool does — modes,
annotation, export — is listed as schedule text around the detail.
"""

from __future__ import annotations

from lib.sheet import Sheet
from lib.svg import fmt
from lib.symbols import cloud, drawing_title, keynote, leader, tag
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "CAPTURE DETAIL"
SUBTITLE = "HayaScope HyperSync — capture boundary detail. Extension UI is never drawn onto the page being captured."
DESC = ("Detail drawing of a web page rectangle with content rules, a fixed header band marked suppressed, a "
        "scroll region, and corner capture brackets placed outside the page. Leaders name the parts. Side "
        "schedules list capture modes, annotation tools, export targets and processing notes. Everything "
        "processes locally in the browser.")

MODES = ["ENTIRE PAGE", "VISIBLE AREA", "SELECTION", "SCROLLABLE REGION", "WINDOW / CONTENT",
         "BATCH TABS", "URL LIST"]
TOOLS = ["BRUSH", "SHAPES", "ARROWS", "TEXT", "NUMBERED CALLOUTS", "BLUR / PIXELATE", "CROP", "ROTATE",
         "RESIZE", "HEADER · FOOTER · WATERMARK"]
EXPORTS = ["PNG", "JPG", "PDF", "CLIPBOARD", "PRINT", "EMAIL"]
STABILITY = ["STICKY / FIXED ELEMENT SUPPRESSION", "LAZY-LOAD STABILITY", "SAME-ORIGIN IFRAME EXPANSION",
             "captureVisibleTab TIMING CONTROL"]


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "D-501", TITLE, SUBTITLE, DESC, zones_active=("04",))
    p = s.pal
    sy = next(x for x in data["systems"] if x["key"] == "hayascope")
    clouded = data["statuses"][sy["status"]]["cloud"]

    # The page
    px, py, pw, ph = 360, 190, 640, 620
    s.doc.rect(px, py, pw, ph, stroke=p.ink, width=HEAVY, fill=p.paper)
    # fixed header (suppressed)
    s.doc.rect(px, py, pw, 54, fill="url(#poche)")
    s.doc.rect(px, py, pw, 54, stroke=p.ink, width=MEDIUM)
    # content rules
    for k in range(16):
        yy = py + 90 + k * 32
        w = pw - 120 if k % 5 else pw - 300
        s.doc.line(px + 60, yy, px + 60 + w, yy, stroke=p.light, width=HAIR * 2)
    # scroll region
    s.doc.rect(px + 60, py + 320, pw - 120, 200, stroke=p.ink, width=HAIR, stroke_dasharray="8 5")
    # viewport marker (visible area)
    s.doc.rect(px - 14, py + 120, pw + 28, 260, stroke=p.ink, width=HAIR, stroke_dasharray="3 5")

    # capture sweep
    s.sweep(px + 4, py + 56, pw - 8, py + ph - 6, dur=6.0, thickness=2.5, opacity=0.6)
    # Capture brackets — OUTSIDE the page, by a clear margin
    m, L = 26, 70
    for (cx, cy, sx, sy_) in ((px - m, py - m, 1, 1), (px + pw + m, py - m, -1, 1),
                              (px + pw + m, py + ph + m, -1, -1), (px - m, py + ph + m, 1, -1)):
        s.doc.path(f"M{fmt(cx)},{fmt(cy + sy_*L)} L{fmt(cx)},{fmt(cy)} L{fmt(cx + sx*L)},{fmt(cy)}",
                   stroke=p.ink, width=HEAVY)

    # Leaders
    leader(s, [(px - m, py + ph / 2), (px - 110, py + ph / 2)], "", anchor="end")
    s.text("CAPTURE BOUNDARY", px - 116, py + ph / 2 - 6, 10, anchor="end", tracking=0.12)
    s.text("BRACKETS SIT OUTSIDE THE PAGE", px - 116, py + ph / 2 + 10, 9, anchor="end", color=p.grey, tracking=0.06)
    leader(s, [(px + 200, py + 27), (px + 200, py - 70), (px + 236, py - 70)], "")
    s.text("FIXED HEADER — SUPPRESSED IN STITCH", px + 242, py - 66, 10, tracking=0.08)
    leader(s, [(px + pw - 60, py + 430), (px + pw + 60, py + 430), (px + pw + 96, py + 430)], "")
    s.text("SCROLL REGION — STITCHED", px + pw + 102, py + 434, 10, tracking=0.08)
    leader(s, [(px + pw + 14, py + 250), (px + pw + 96, py + 250)], "")
    s.text("VISIBLE AREA", px + pw + 102, py + 254, 10, tracking=0.08)
    leader(s, [(px + 40, py + ph - 40), (px - 60, py + ph + 50), (px - 100, py + ph + 50)], "", anchor="end")
    s.text("PAGE CONTENT — UNTOUCHED", px - 106, py + ph + 54, 10, anchor="end", tracking=0.08)

    # Tag and title
    tag(s, px + pw / 2 - 29, py + ph + 40, sy["no"], clouded=clouded)
    s.text(sy["name"].upper(), px + pw / 2, py + ph + 90, 13, anchor="middle", tracking=0.12)
    s.text("INFINITE CAPTURES. ZERO PAYWALLS.", px + pw / 2, py + ph + 110, 10.5, anchor="middle",
           color=p.grey, tracking=0.1)
    drawing_title(s, 140, 1008, "1", "CAPTURE BOUNDARY DETAIL", width=480)

    # Schedules on the right
    kx = 1270
    def block(title: str, items: list[str], y: float, cols: int = 1, size: float = 10.5) -> float:
        s.text(title, kx, y, 12, tracking=0.16)
        s.doc.line(kx, y + 9, 1700, y + 9, stroke=p.ink, width=HEAVY)
        y += 34
        colw = (1700 - kx) / cols
        for i, it in enumerate(items):
            cx = kx + (i % cols) * colw
            cy = y + (i // cols) * 20
            s.doc.rect(cx, cy - 9, 8, 8, stroke=p.ink, width=HAIR)
            s.text(it, cx + 18, cy, size, tracking=0.04)
        rows = (len(items) + cols - 1) // cols
        return y + rows * 20 + 26

    y = 176
    y = block("CAPTURE MODES", MODES, y, cols=2)
    y = block("ANNOTATION", TOOLS, y, cols=2)
    y = block("EXPORT", EXPORTS, y, cols=3)
    y = block("STABILITY", STABILITY, y, cols=1)
    # processing note
    s.doc.rect(kx, y - 6, 1700 - kx, 84, stroke=p.ink, width=MEDIUM)
    s.text("ALL PROCESSING LOCAL — IN THE BROWSER.", kx + 16, y + 24, 11.5, tracking=0.1)
    s.text("PROGRESS BELONGS IN THE POPUP, HISTORY AND STUDIO — NEVER ON THE PAGE.", kx + 16, y + 46, 9.5,
           color=p.grey, tracking=0.04)
    s.text("EDITABLE PROJECT SAVE · LOCAL CAPTURE HISTORY", kx + 16, y + 64, 9.5, color=p.grey, tracking=0.04)

    return {"main": s}
