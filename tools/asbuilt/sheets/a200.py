"""A-200 — FLEET FLOOR. Service Core enlarged: the onboarding riser and the
operational systems that keep a fleet running.

Drawing 1 is the riser: one operator, three input fields, one packaged
process, one bus, twenty-five endpoints. Drawing 2 is the enlarged plan of
the Service Core with equipment notes.
"""

from __future__ import annotations

from lib.sheet import Sheet
from lib.symbols import arrow, checkpoint, dimension, drawing_title, tag
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "FLEET FLOOR"
SUBTITLE = "Service Core enlarged. Onboarding riser: one operator configures ~25 endpoints in one run."
DESC = ("Riser diagram: an administrator terminal and three input fields feed a packaged process, which "
        "feeds a distribution bus with twenty-five endpoint symbols in five rows. Beside it, an enlarged "
        "plan of the Service Core room with the policy automation, asset register, ticketing and "
        "e-commerce processing systems and their notes.")


def _sys(data, key):
    return next(s for s in data["systems"] if s["key"] == key)


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "A-200", TITLE, SUBTITLE, DESC, zones_active=("01",))
    p = s.pal
    onboarding = _sys(data, "onboarding")
    n_ep = onboarding["counts"]["endpoints_per_run"]
    clouded = lambda sy: data["statuses"][sy["status"]]["cloud"]

    # ------------------------------------------------------------------ 1 RISER
    # Input fields
    fx, fy = 150, 300
    fields = ["EMPLOYEE ID", "DEPARTMENT", "M365 EMAIL"]
    for i, f in enumerate(fields):
        y = fy + i * 54
        s.doc.rect(fx, y, 150, 34, stroke=p.ink, width=MEDIUM)
        s.text(f, fx + 12, y + 22, 11, tracking=0.08)
        s.doc.line(fx + 150, y + 17, fx + 190, y + 17, stroke=p.ink, width=HAIR)
    s.doc.line(fx + 190, fy + 17, fx + 190, fy + 2 * 54 + 17, stroke=p.ink, width=HAIR)
    dimension(s, fx, fy, fx, fy + 2 * 54 + 34, "3 FIELDS", offset=26, size=10.5, flip=True)

    # Operator
    ox, oy = 150, 520
    s.doc.rect(ox, oy, 150, 90, stroke=p.ink, width=MEDIUM)
    s.doc.rect(ox + 14, oy + 12, 122, 46, stroke=p.ink, width=HAIR)
    s.doc.line(ox + 40, oy + 76, ox + 110, oy + 76, stroke=p.ink, width=MEDIUM)
    s.text("ADMINISTRATOR", ox + 75, oy + 40, 10.5, anchor="middle", tracking=0.1)
    s.text("×1", ox + 75, oy + 108 + 14, 13, anchor="middle")
    s.doc.line(ox + 150, oy + 45, fx + 190, oy + 45, stroke=p.ink, width=HAIR)
    s.doc.line(fx + 190, fy + 17, fx + 190, oy + 45, stroke=p.ink, width=HAIR)

    # Packaged process (tag 101)
    px, py = 380, 380
    s.doc.rect(px, py, 170, 150, stroke=p.ink, width=HEAVY)
    tag(s, px + 56, py + 18, onboarding["no"], clouded=clouded(onboarding))
    for i, ln in enumerate(["PACKAGED", "PROCESS", "— ONE RUN —"]):
        s.text(ln, px + 85, py + 74 + i * 20, 12, anchor="middle", tracking=0.12)
    s.doc.line(fx + 190, py + 75, px, py + 75, stroke=p.ink, width=HAIR)
    arrow(s, fx + 190, py + 75, px - 2, py + 75, width=HAIR)
    for i in range(3):
        s.packet(fx + 150, fy + i * 54 + 17, fx + 190, fy + i * 54 + 17, dur=1.2, r=2.4, begin=i * 0.4)
    s.packet(fx + 190, py + 75, px - 2, py + 75, dur=1.4, r=2.6, begin=0.6)

    # Bus
    bx = 640
    top_y, bot_y = 236, 900
    s.doc.line(px + 170, py + 75, bx, py + 75, stroke=p.ink, width=HEAVY)
    s.packet(px + 170, py + 75, bx, py + 75, dur=1.0, r=3.2, begin=1.8)
    s.doc.line(bx, top_y, bx, bot_y, stroke=p.ink, width=HEAVY)
    s.text("DISTRIBUTION BUS", bx + 10, bot_y + 4, 10, tracking=0.12, color=p.grey)

    # Endpoints: 5 rows x 5
    rows, cols = 5, 5
    ex0, ey0, dx, dy = 720, 246, 78, 132
    ew, eh = 54, 34
    k = 0
    for r in range(rows):
        ry = ey0 + r * dy
        s.doc.line(bx, ry + eh / 2, ex0 + (cols - 1) * dx + ew / 2, ry + eh / 2, stroke=p.ink, width=HAIR)
        s.packet(bx, ry + eh / 2, ex0 + (cols - 1) * dx + ew / 2, ry + eh / 2, dur=3.0, r=2.6, begin=r * 0.5)
        for c in range(cols):
            k += 1
            x = ex0 + c * dx
            s.doc.rect(x, ry, ew, eh, stroke=p.ink, width=MEDIUM, fill=p.paper)
            s.doc.rect(x + 8, ry + 6, ew - 16, eh - 16, stroke=p.ink, width=HAIR)
            s.text(f"{k:02d}", x + ew / 2, ry + eh + 14, 9.5, anchor="middle", color=p.grey)
    last_x = ex0 + (cols - 1) * dx + ew
    dimension(s, ex0, ey0 - 26, last_x, ey0 - 26, f"{n_ep} EA. — CONFIGURED PER RUN", offset=0, size=11)

    # Notes under riser
    ny = 950
    s.text("EMPLOYEE PROVIDES THREE FIELDS. THE PROCESS DOES THE REST. MINIMAL MANUAL INTERACTION.",
           150, ny, 11, tracking=0.04, color=p.grey)
    drawing_title(s, 150, 1008, "1", "FLEET RISER — AUTO-ONBOARDING", width=560)

    # ------------------------------------------------------------ 2 ENLARGED PLAN
    rx, ry, rw, rh = 1150, 180, 520, 700
    s.doc.rect(rx, ry, rw, rh, stroke=p.ink, width=MEDIUM)
    checkpoint(s, rx, ry + rh - 52, 40, "v", swing=1)
    s.text("SERVICE CORE", rx + rw / 2, ry + 34, 15, anchor="middle", tracking=0.16)
    s.doc.rect(rx + rw / 2 - 19, ry + 42, 38, 18, stroke=p.ink, width=HAIR)
    s.text("01", rx + rw / 2, ry + 55, 11, anchor="middle")

    equipment = [
        ("policy",    ["USB CONTROLS · MONITORING · ENDPOINT POLICY", "BUNDLED, HEADLESS EXECUTION"]),
        ("assets",    ["ON-PREM ASSET REGISTER · TAILORED PLUGINS", "ZERO LICENCE COST"]),
        ("ticketing", ["STRUCTURED INTAKE → ROUTED TECHNICIAN CONTEXT", "OUTLETS: WEBHOOK · WHATSAPP · TELEGRAM"]),
        ("ecommerce", ["HIGH-VOLUME PRODUCT PROCESSING", "THROUGHPUT NOT CHARACTERISED"]),
    ]
    ey = ry + 96
    for i, (key, notes) in enumerate(equipment):
        sy = _sys(data, key)
        bx0, by0, bw, bh = rx + 40, ey + i * 150, rw - 80, 96
        s.doc.rect(bx0, by0, bw, bh, stroke=p.ink, width=MEDIUM)
        tag(s, bx0 + 14, by0 + 14, sy["no"], clouded=clouded(sy))
        s.text(sy["name"].upper(), bx0 + 86, by0 + 31, 12, tracking=0.06)
        for j, ln in enumerate(notes):
            s.text(ln.replace("→", "-"), bx0 + 14, by0 + 62 + j * 18, 10, color=p.grey, tracking=0.04)
        if key == "ticketing":
            # three notification outlets on the room wall
            for j, lab in enumerate(["WEBHOOK", "WHATSAPP", "TELEGRAM"]):
                cx = bx0 + 60 + j * 120
                s.doc.circle(cx, by0 + bh + 18, 6, stroke=p.ink, width=MEDIUM, fill=p.paper)
                s.doc.line(cx, by0 + bh, cx, by0 + bh + 12, stroke=p.ink, width=HAIR)
                s.text(lab, cx, by0 + bh + 36, 8.5, anchor="middle", color=p.grey, tracking=0.1)
    # riser tag reference inside room
    s.text("ONBOARDING RISER — SEE DRAWING 1", rx + rw - 16, ry + rh - 14, 9.5, anchor="end", color=p.grey, tracking=0.1)
    drawing_title(s, rx, 1008, "2", "SERVICE CORE — ENLARGED PLAN", width=520)

    return {"main": s}
