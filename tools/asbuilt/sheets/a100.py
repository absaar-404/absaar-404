"""A-100 — SITE PLAN. The hero sheet: every system located in its zone.

The compound is read as a zero-trust site. The security perimeter is the
outer wall and the corridor inside it. Every opening between spaces is a
checkpoint. Systems are numbered tags; the keynote list on the right names
them; the Schedule (S-001, in the README) carries their status.
"""

from __future__ import annotations

from lib.sheet import Canvas, Sheet, cloud_path
from lib.site import CORRIDOR, INSET, PH, PW, PX0, PY0, ROOMS_PX, WALL_T
from lib.symbols import (TAG_H, TAG_W, checkpoint, cloud, drawing_title, keynote, partition,
                         room_tag, section_marker, tag, wall_band)
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "SITE PLAN"
SUBTITLE = "All systems located by zone. Openings between spaces are access checkpoints."
DESC = ("Architectural site plan of a secured compound. A hatched perimeter wall encloses a corridor "
        "labelled Security Perimeter, containing the SOC platform and the Intrusion Alert System. Inside, "
        "four rooms: Service Core, Document Room, Tool Workshop and Annex, each holding numbered system tags. "
        "Doors between rooms are labelled as checkpoints. A keynote list on the right names every tag.")


def _room(zid: str):
    x, y, w, h = ROOMS_PX[zid]
    return (PX0 + x, PY0 + y, w, h)


def _by_zone(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for sy in data["systems"]:
        out.setdefault(sy["zone"], []).append(sy)
    return out


def _clouded(data: dict, sy: dict) -> bool:
    return data["statuses"][sy["status"]]["cloud"]


def draw_plan(s, data: dict, ox: float, oy: float, scale: float, dense: bool) -> None:
    """Draw the compound at origin (ox, oy) with the given scale. `dense`
    adds system tags and checkpoints (A-100); False gives the key plan."""
    p = s.pal

    def X(v): return ox + v * scale
    def Y(v): return oy + v * scale
    def S(v): return v * scale

    # Outer wall (cut) and perimeter corridor
    wall_band(s, X(PX0), Y(PY0), S(PW), S(PH), S(WALL_T))
    ix, iy, iw, ih = PX0 + INSET, PY0 + INSET, PW - 2 * INSET, PH - 2 * INSET
    s.doc.rect(X(ix), Y(iy), S(iw), S(ih), stroke=p.ink, width=MEDIUM)
    # corridor floor tone (secured zone)
    s.doc.path(
        f"M{X(PX0+WALL_T)},{Y(PY0+WALL_T)}h{S(PW-2*WALL_T)}v{S(PH-2*WALL_T)}h{S(-(PW-2*WALL_T))}z "
        f"M{X(ix)},{Y(iy)}v{S(ih)}h{S(iw)}v{S(-ih)}z",
        fill="url(#secure)", fill_rule="evenodd",
    )

    # Partitions
    r01, r03, r04, r05 = _room("01"), _room("03"), _room("04"), _room("05")
    split_x = r03[0]
    partition(s, X(split_x), Y(iy), X(split_x), Y(iy + ih))
    partition(s, X(split_x), Y(r04[1]), X(split_x + r04[2]), Y(r04[1]))
    partition(s, X(split_x), Y(r05[1]), X(split_x + r05[2]), Y(r05[1]))

    # Room tags
    zones = {z["id"]: z for z in data["zones"]}
    size = 15 if dense else 26
    room_tag(s, X(r01[0] + r01[2] / 2), Y(r01[1] + 42), zones["01"]["name"], "01", size)
    room_tag(s, X(r03[0] + r03[2] / 2), Y(r03[1] + 42), zones["03"]["name"], "03", size)
    room_tag(s, X(r04[0] + r04[2] / 2), Y(r04[1] + 42), zones["04"]["name"], "04", size)
    room_tag(s, X(r05[0] + r05[2] / 2), Y(r05[1] + 42), zones["05"]["name"], "05", size)
    # perimeter label runs along the top corridor
    s.text(zones["02"]["name"], X(PX0 + PW / 2), Y(PY0 + WALL_T + CORRIDOR / 2 + 5), size, anchor="middle", tracking=0.22)
    bw_, bh_ = size * 2.5, size * 1.2
    bx_ = X(PX0 + PW / 2) + s.width(zones["02"]["name"], size, 0.22) / 2 + 14
    by_ = Y(PY0 + WALL_T + CORRIDOR / 2 + 5) - bh_ + size * 0.25
    s.doc.rect(bx_, by_, bw_, bh_, stroke=p.ink, width=HAIR)
    s.text("02", bx_ + bw_ / 2, by_ + bh_ - size * 0.28, size * 0.72, anchor="middle")

    if not dense:
        return

    # Checkpoints. Entry through the outer wall is the identity checkpoint.
    checkpoint(s, X(300), Y(PY0 + PH - WALL_T / 2), S(40), "h", swing=-1, label="ENTRY · IAM", thick=S(WALL_T / 2), gap_pad=S(4))
    checkpoint(s, X(ix), Y(600), S(40), "v", swing=1)                      # corridor -> service core
    checkpoint(s, X(split_x), Y(r03[1] + 70), S(40), "v", swing=1)          # service core -> document room
    checkpoint(s, X(split_x), Y(r04[1] + 90), S(40), "v", swing=1)          # service core -> tool workshop
    checkpoint(s, X(split_x + 360), Y(r04[1]), S(40), "h", swing=1)         # document room -> workshop
    checkpoint(s, X(split_x + 360), Y(r05[1]), S(40), "h", swing=1)         # workshop -> annex

    # System tags
    by = _by_zone(data)

    def grid(zone: str, x0: float, y0: float, cols: int, dx: float, dy: float):
        for i, sy in enumerate(by.get(zone, [])):
            cx, cy = x0 + (i % cols) * dx, y0 + (i // cols) * dy
            tag(s, X(cx), Y(cy), sy["no"], clouded=_clouded(data, sy), w=S(TAG_W), h=S(TAG_H))
            sy["_pos"] = (X(cx), Y(cy))

    grid("01", r01[0] + 84, r01[1] + 120, 2, 190, 118)
    grid("03", r03[0] + 60, r03[1] + 100, 4, 110, 60)
    grid("04", r04[0] + 60, r04[1] + 92, 4, 110, 62)
    grid("05", r05[0] + 60, r05[1] + 92, 4, 110, 62)
    # enlarged-plan references, one per room
    for zid, rr in (("01", r01), ("03", r03), ("04", r04), ("05", r05)):
        sheet_ref = zones[zid]["sheet"]
        if sheet_ref != "A-100":
            s.text(f"ENLARGED PLAN: {sheet_ref}", X(rr[0] + rr[2]) - S(14), Y(rr[1] + rr[3]) - S(12), 9.5,
                   anchor="end", color=p.grey, tracking=0.1)

    # perimeter systems sit in the corridor
    per = by.get("02", [])
    corridor_y = PY0 + PH - WALL_T - CORRIDOR / 2 - TAG_H / 2
    for i, sy in enumerate(per):
        cx = PX0 + PW - WALL_T - 120 - (len(per) - 1 - i) * 110
        tag(s, X(cx), Y(corridor_y), sy["no"], clouded=_clouded(data, sy), w=S(TAG_W), h=S(TAG_H))
        sy["_pos"] = (X(cx), Y(corridor_y))

    # Section reference through the perimeter (A-300) and detail reference (D-501)
    cut_y = Y(430)
    s.doc.add(f'<line x1="{X(PX0) - 26}" y1="{cut_y}" x2="{X(PX0 + INSET) + 10}" y2="{cut_y}" stroke="{p.ink}" stroke-width="{MEDIUM}" '
              f'stroke-dasharray="14 6 3 6"><animate attributeName="stroke-dashoffset" from="0" to="-29" dur="2.4s" repeatCount="indefinite"/></line>')
    section_marker(s, X(PX0) - 44, cut_y, "A", "A-300", direction="down")
    for sy in data["systems"]:
        if sy.get("detail_sheet") and "_pos" in sy:
            tx, ty = sy["_pos"]
            cx, cy = tx + S(TAG_W) / 2, ty + S(TAG_H) / 2
            s.doc.add(f'<circle cx="{cx}" cy="{cy}" r="{S(44)}" fill="none" stroke="{p.ink}" stroke-width="{HAIR}" stroke-dasharray="6 4">'
                      f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></circle>')
            s.doc.line(cx - S(31), cy - S(31), cx - S(48), cy - S(62), stroke=p.ink, width=HAIR)
            section_marker(s, cx - S(48), cy - S(80), "1", sy["detail_sheet"], direction="none")


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "A-100", TITLE, SUBTITLE, DESC, zones_active=("01", "02", "03", "04", "05"))
    draw_plan(s, data, 0, 0, 1.0, dense=True)
    p = s.pal

    # Drawing title
    drawing_title(s, PX0, 1008, "1", "SITE PLAN — AS BUILT", width=520)

    # Keynote list
    kx, ky = 1290, 166
    s.text("KEYNOTES — SYSTEMS", kx, ky, 13, tracking=0.16)
    s.doc.line(kx, ky + 10, 1700, ky + 10, stroke=p.ink, width=HEAVY)
    y = ky + 36
    for sy in data["systems"]:
        s.text(sy["no"], kx, y, 12)
        s.text(sy["name"].upper(), kx + 52, y, 11.5, tracking=0.03)
        st = sy["status"]
        if data["statuses"][st]["cloud"]:
            s.text(st, 1700, y, 9.5, anchor="end", color=p.red, tracking=0.1)
        y += 20.5

    # Legend — single column
    ly0 = y + 22
    s.text("LEGEND", kx, ly0, 13, tracking=0.16)
    s.doc.line(kx, ly0 + 10, 1700, ly0 + 10, stroke=p.ink, width=HEAVY)
    entries = [
        ("boundary", "TRUST BOUNDARY — CUT"), ("partition", "PARTITION"),
        ("checkpoint", "CHECKPOINT — ACCESS CONTROLLED OPENING"), ("secure", "SECURED CIRCULATION"),
        ("tag", "SYSTEM TAG — SEE SCHEDULE S-001"), ("cloud", "REVISION CLOUD — WORK IN PROGRESS"),
        ("keynote", "KEYNOTE"), ("section", "SECTION / DETAIL REFERENCE"),
    ]
    cy = ly0 + 40
    for e, label in entries:
        cx = kx
        if e == "boundary":
            s.doc.rect(cx, cy - 11, 56, 14, fill="url(#poche)")
            s.doc.rect(cx, cy - 11, 56, 14, stroke=p.ink, width=HEAVY)
        elif e == "partition":
            s.doc.line(cx, cy - 4, cx + 56, cy - 4, stroke=p.ink, width=MEDIUM)
        elif e == "checkpoint":
            s.doc.line(cx, cy - 4, cx + 56, cy - 4, stroke=p.ink, width=MEDIUM)
            checkpoint(s, cx + 15, cy - 4, 22, "h", swing=-1, label="")
        elif e == "secure":
            s.doc.rect(cx, cy - 11, 56, 14, fill="url(#secure)")
            s.doc.rect(cx, cy - 11, 56, 14, stroke=p.ink, width=HAIR)
        elif e == "tag":
            tag(s, cx, cy - 16, "000")
        elif e == "cloud":
            tag(s, cx, cy - 16, "000", clouded=True)
        elif e == "keynote":
            keynote(s, cx + 12, cy - 5, "1")
        elif e == "section":
            section_marker(s, cx + 16, cy - 5, "A", "A-300", direction="none")
        s.text(label, cx + 74, cy, 10.5, tracking=0.03)
        cy += 28

    # Mobile key plan (square, zones only)
    k = Canvas(faces, pal, 1200, 1200, "Key plan — site zones",
               "Simplified site plan showing five zones: Security Perimeter, Service Core, Document Room, Tool Workshop, Annex.")
    k.doc.rect(18, 18, 1164, 1164, stroke=pal.ink, width=HEAVY)
    scale = 1000 / PW
    draw_plan(k, data, 100 - PX0 * scale, 150 - PY0 * scale, scale, dense=False)
    k.text(pr["name"], 100, 90, 34, tracking=0.06, weight="medium")
    k.text(f"{pr['sector']}  ·  SITE PLAN  ·  KEY", 100, 122, 16, color=pal.grey, tracking=0.16)
    k.text("A-100", 1100, 1120, 54, anchor="end", weight="medium")
    k.text(f"DRAWN BY {pr['drawn_by']}  ·  PROJECT NO. {pr['number']}  ·  NTS", 100, 1120, 15, color=pal.grey, tracking=0.08)

    return {"main": s, "key": k}
