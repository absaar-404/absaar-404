"""A-300 — SECURITY PERIMETER, SECTION A-A.

Drawing 1 cuts through the perimeter and shows the Intrusion Alert System as
an enclosure: eight layers on either side of one server, drawn as a wall
assembly. Drawing 2 is an elevation of the SOC engine rack: twenty-two
engines in a single chase. Counts are the only numbers on the sheet.
"""

from __future__ import annotations

from lib.sheet import Sheet
from lib.symbols import arrow, dimension, drawing_title, section_marker, tag
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "SECURITY SECTION"
SUBTITLE = "Section A-A through the perimeter. IAS drawn as an 8-layer enclosure; SOC as a 22-engine rack."
DESC = ("Section drawing. Left: a server symbol enclosed by eight concentric layer bands on each side, "
        "labelled Layer 1 to Layer 8, standing on a ground line with hatched earth below; dimension reads "
        "8 layers. Right: an elevation of a rack with twenty-two engine slots labelled E01 to E22; "
        "dimension reads 22 engines; telemetry enters from the left, alerts and response leave to the right.")


def _sys(data, key):
    return next(s for s in data["systems"] if s["key"] == key)


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "A-300", TITLE, SUBTITLE, DESC, zones_active=("02",))
    p = s.pal
    ias, soc = _sys(data, "ias"), _sys(data, "soc")
    layers = ias["counts"]["layers"]
    engines = soc["counts"]["engines"]
    clouded = lambda sy: data["statuses"][sy["status"]]["cloud"]

    # Ground line and earth
    gy = 880
    s.doc.rect(120, gy, 1580, 56, fill="url(#secure)")
    s.doc.line(120, gy, 1700, gy, stroke=p.ink, width=HEAVY)
    s.doc.line(120, gy + 56, 1700, gy + 56, stroke=p.ink, width=HAIR)
    section_marker(s, 118, gy - 140, "A", "A-100", direction="right")
    section_marker(s, 1120, gy - 140, "A", "A-100", direction="left")
    s.text("EXTERIOR — UNTRUSTED", 150, gy - 22, 10.5, color=p.grey, tracking=0.14)

    # ------------------------------------------------- 1 IAS ENCLOSURE (SECTION)
    cx = 620                 # server centre line
    top, bot = 300, gy
    sw, sh = 110, 220
    band, gap = 22, 8
    inner = 90               # half-width of the innermost layer
    # layer bands: from innermost (1) to outermost (8)
    for i in range(layers):
        half = inner + i * (band + gap)
        for side in (-1, 1):
            x = cx + side * half - (band if side > 0 else 0)
            s.doc.rect(x, top - i * 10, band, bot - (top - i * 10), stroke=p.ink, width=MEDIUM,
                       fill="url(#poche)" if i == layers - 1 else "none")
            if side > 0:
                s.text(f"L{i+1}", x + band / 2, top - i * 10 - 8, 9.5, anchor="middle", color=p.grey)
        # ties between symmetrical bands
    # server
    s.doc.rect(cx - sw / 2, bot - sh, sw, sh, stroke=p.ink, width=HEAVY, fill=p.paper)
    for k in range(6):
        yy = bot - sh + 26 + k * 30
        s.doc.line(cx - sw / 2 + 14, yy, cx + sw / 2 - 14, yy, stroke=p.ink, width=HAIR)
    s.text("SERVER", cx, bot - sh - 14, 10.5, anchor="middle", tracking=0.14)
    tag(s, cx - 29, top - 130, ias["no"], clouded=clouded(ias))
    s.text(ias["name"].upper(), cx, top - 146, 12, anchor="middle", tracking=0.08)
    s.text("EIGHT LAYERS AROUND ONE SERVER. EVERY LAYER RAISES AN ALERT.", 1080, gy - 22, 10, anchor="end",
           color=p.grey, tracking=0.04)
    outer_half = inner + (layers - 1) * (band + gap)
    dimension(s, cx + inner, top - (layers - 1) * 10 - 34, cx + outer_half, top - (layers - 1) * 10 - 34,
              f"{layers} LAYERS", offset=0, size=11)
    dimension(s, cx - outer_half, top - (layers - 1) * 10 - 34, cx - inner, top - (layers - 1) * 10 - 34,
              f"{layers} LAYERS", offset=0, size=11)
    # protected side annotation
    s.text("PROTECTED", cx, bot - sh / 2 + 4, 9.5, anchor="middle", color=p.grey, tracking=0.16)
    drawing_title(s, 150, 1008, "1", "SECTION A-A — IAS ENCLOSURE", width=560)

    # ------------------------------------------------- 2 SOC ENGINE RACK (ELEVATION)
    rx, rw = 1240, 300
    slot_h = 22
    ry = gy - 40 - engines * slot_h
    s.doc.rect(rx, ry - 30, rw, engines * slot_h + 70, stroke=p.ink, width=HEAVY)
    for i in range(engines):
        y = ry + i * slot_h
        s.doc.rect(rx + 22, y, rw - 44, slot_h - 5, stroke=p.ink, width=MEDIUM)
        s.text(f"E{i+1:02d}", rx + 34, y + 12.5, 8.5, color=p.grey)
        s.doc.circle(rx + rw - 40, y + (slot_h - 5) / 2, 2.2, fill=p.ink)
    # rack feet
    s.doc.line(rx, gy, rx + rw, gy, stroke=p.ink, width=HEAVY)
    dimension(s, rx + rw + 22, ry, rx + rw + 22, ry + engines * slot_h - 5, f"{engines} ENGINES", offset=0, size=11)
    tag(s, rx + rw / 2 - 29, ry - 120, soc["no"], clouded=clouded(soc))
    s.text(soc["name"].upper(), rx + rw / 2, ry - 136, 12, anchor="middle", tracking=0.08)
    s.text("BUILT FROM FIRST PRINCIPLES. LAYERED ARCHITECTURE.", rx + rw / 2, ry - 76, 10, anchor="middle",
           color=p.grey, tracking=0.04)
    # in / out
    arrow(s, rx - 150, ry + 120, rx - 4, ry + 120)
    s.text("ENDPOINT TELEMETRY", rx - 150, ry + 108, 9.5, color=p.grey, tracking=0.1)
    arrow(s, rx + rw + 90, ry + 300, rx + rw + 196, ry + 300)
    s.text("ALERT · RESPONSE", rx + rw + 90, ry + 288, 9.5, color=p.grey, tracking=0.1)
    s.text("RMM", rx + rw + 90, ry + 322, 9.5, color=p.grey, tracking=0.1)
    for j, f in enumerate(["DETECTION", "MONITORING", "RESPONSE"]):
        s.text(f, rx - 150, ry + 160 + j * 18, 9.5, color=p.grey, tracking=0.1)
    drawing_title(s, 1240, 1008, "2", "ELEVATION — SOC ENGINE RACK", width=440)

    return {"main": s}
