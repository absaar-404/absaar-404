"""Sheet frame: border, grid bubbles, title block, key plan, notes.

Every sheet in the set shares this frame so the set reads as bound, not
stacked. Coordinates are in sheet units on an 1800 x 1200 landscape sheet.
"""

from __future__ import annotations

import math
from pathlib import Path

from .svg import Doc, fmt
from .text import Face
from .theme import HAIR, HEAVY, MEDIUM, Palette

W, H = 1800, 1200

# Drawing area (inside grid bubbles, above title block)
DX0, DY0, DX1, DY1 = 100, 100, 1700, 1030
# Title block strip
TB_Y0, TB_Y1 = 1046, 1164
TB_X0, TB_X1 = 36, 1764

GRID_COLS = "ABCDEFGH"
GRID_ROWS = 6


class Lettering:
    """Shared lettering helpers for anything that carries a Doc."""

    faces: dict[str, Face]
    face: Face
    pal: Palette
    doc: Doc

    def text(self, s: str, x: float, y: float, size: float, anchor: str = "start",
             color: str | None = None, tracking: float = 0.0, weight: str = "regular") -> float:
        """Place outlined lettering. Returns the string's advance width."""
        if not s:
            return 0.0
        face = self.faces[weight]
        d = face.path(s, x, y, size, anchor=anchor, tracking=tracking)
        self.doc.path(d, fill=color or self.pal.ink)
        return face.width(s, size, tracking)

    def width(self, s: str, size: float, tracking: float = 0.0, weight: str = "regular") -> float:
        return self.faces[weight].width(s, size, tracking)

    def lines(self, items: list[str], x: float, y: float, size: float, leading: float,
              color: str | None = None, tracking: float = 0.0, anchor: str = "start") -> float:
        for s in items:
            self.text(s, x, y, size, anchor=anchor, color=color, tracking=tracking)
            y += leading
        return y

    def wrap(self, s: str, size: float, max_w: float, tracking: float = 0.0) -> list[str]:
        words, out, cur = s.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.width(t, size, tracking) <= max_w or not cur:
                cur = t
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out

    # -- motion (SMIL; subtle, drafting-appropriate) -------------------------

    def packet(self, x1: float, y1: float, x2: float, y2: float, dur: float = 2.4,
               r: float = 3.0, begin: float = 0.0, color: str | None = None) -> None:
        """A dot travelling along a line — data moving through the drawing."""
        self.doc.add(f'<circle r="{fmt(r)}" fill="{color or self.pal.ink}"><animateMotion dur="{dur:.2f}s" '
                     f'begin="{begin:.2f}s" repeatCount="indefinite" path="M{fmt(x1)},{fmt(y1)} L{fmt(x2)},{fmt(y2)}"/></circle>')

    def blink(self, x: float, y: float, r: float, dur: float = 2.0, begin: float = 0.0, color: str | None = None) -> None:
        self.doc.add(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{color or self.pal.ink}">'
                     f'<animate attributeName="opacity" values="1;0.15;1" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')

    def sweep(self, x: float, y0: float, w: float, y1: float, dur: float = 5.0, thickness: float = 2.0,
              color: str | None = None, opacity: float = 0.7) -> None:
        """A horizontal line travelling from y0 to y1 and back — a scan."""
        self.doc.add(f'<rect x="{fmt(x)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(thickness)}" fill="{color or self.pal.ink}" opacity="{opacity}">'
                     f'<animate attributeName="y" values="{fmt(y0)};{fmt(y1)};{fmt(y0)}" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>')

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.doc.render(), encoding="utf-8")


class Canvas(Lettering):
    """A frameless drawing surface (used for the mobile key plan)."""

    def __init__(self, faces: dict[str, Face], pal: Palette, w: float, h: float, title: str, desc: str):
        self.faces = faces
        self.face = faces["regular"]
        self.pal = pal
        self.w, self.h = w, h
        self.doc = Doc(w, h, pal.paper, title, desc)
        _defs(self.doc, pal)


def _defs(doc: Doc, p: Palette) -> None:
    # Poché: 45° hatch for cut trust boundaries.
    doc.def_(
        '<pattern id="poche" patternUnits="userSpaceOnUse" width="8" height="8">'
        f'<path d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4" stroke="{p.ink}" stroke-width="0.9" fill="none"/></pattern>'
    )
    # Secured zone tone: light diagonal hatch, wider spacing.
    doc.def_(
        '<pattern id="secure" patternUnits="userSpaceOnUse" width="16" height="16">'
        f'<path d="M-4,4 l8,-8 M0,16 l16,-16 M12,20 l8,-8" stroke="{p.light}" stroke-width="0.8" fill="none"/></pattern>'
    )
    # Document tone: dot field.
    doc.def_(
        '<pattern id="dots" patternUnits="userSpaceOnUse" width="10" height="10">'
        f'<circle cx="5" cy="5" r="0.9" fill="{p.grey}"/></pattern>'
    )


class Sheet(Lettering):
    def __init__(self, faces: dict[str, Face], pal: Palette, project: dict, number: str, title: str,
                 subtitle: str, desc: str, zones_active: tuple[str, ...] = ()):
        self.faces = faces
        self.face = faces["regular"]
        self.pal = pal
        self.project = project
        self.number = number
        self.title = title
        self.subtitle = subtitle
        self.zones_active = zones_active
        self.doc = Doc(W, H, pal.paper, f"Sheet {number} — {title}", desc)
        _defs(self.doc, pal)
        self._frame()

    # -- frame --------------------------------------------------------------

    def _frame(self) -> None:
        d, p = self.doc, self.pal
        d.rect(24, 24, W - 48, H - 48, stroke=p.ink, width=HEAVY)
        d.rect(36, 36, W - 72, H - 72, stroke=p.ink, width=HAIR)
        # Grid bubbles: columns across the top, rows down the left.
        n = len(GRID_COLS)
        for i, c in enumerate(GRID_COLS):
            x = DX0 + (DX1 - DX0) * (i + 0.5) / n
            d.circle(x, 66, 13, stroke=p.ink, width=HAIR)
            self.text(c, x, 71, 14, anchor="middle")
            d.line(x, 79, x, 96, stroke=p.ink, width=HAIR)
        for j in range(GRID_ROWS):
            y = DY0 + (DY1 - DY0) * (j + 0.5) / GRID_ROWS
            d.circle(66, y, 13, stroke=p.ink, width=HAIR)
            self.text(str(j + 1), 66, y + 5, 14, anchor="middle")
            d.line(79, y, 96, y, stroke=p.ink, width=HAIR)
        self._title_block()

    def _title_block(self) -> None:
        d, p, pr = self.doc, self.pal, self.project
        d.line(TB_X0, TB_Y0, TB_X1, TB_Y0, stroke=p.ink, width=MEDIUM)
        cells = [TB_X0, 430, 930, 1250, 1490, 1636, TB_X1]
        for x in cells[1:-1]:
            d.line(x, TB_Y0, x, TB_Y1, stroke=p.ink, width=HAIR)
        lab = 10.5
        top = TB_Y0 + 20

        # 1 — Project
        x = cells[0] + 16
        self.text("PROJECT", x, top, lab, color=p.grey, tracking=0.12)
        self.text(pr["name"], x, top + 34, 28, tracking=0.04, weight="medium")
        self.text(pr["sector"], x, top + 58, 15, color=p.grey, tracking=0.14)
        self.text(f"PROJECT NO. {pr['number']}", x, top + 84, 11.5, color=p.grey, tracking=0.08)

        # 2 — Sheet title
        x = cells[1] + 16
        self.text("SHEET TITLE", x, top, lab, color=p.grey, tracking=0.12)
        self.text(self.title, x, top + 34, 28, tracking=0.04)
        for i, ln in enumerate(self.wrap(self.subtitle, 13, cells[2] - x - 20)[:2]):
            self.text(ln, x, top + 58 + i * 17, 13, color=p.grey)

        # 3 — Drawn by
        x = cells[2] + 16
        self.text("DRAWN BY", x, top, lab, color=p.grey, tracking=0.12)
        self.text(pr["drawn_by"], x, top + 34, 28, tracking=0.06)
        self.text(pr["role"], x, top + 58, 11.5, color=p.grey, tracking=0.06)
        self.text(f"{pr['site']}   ·   github.com/{pr['github']}", x, top + 84, 11.5, color=p.grey)

        # 4 — Issue / rev / scale: three mini-columns
        total = cells[4] - cells[3]
        widths = (total * 0.44, total * 0.24, total * 0.32)
        x = cells[3]
        for i, ((k, v), cw) in enumerate(zip((("ISSUE", pr["issue"]), ("REV", pr["revision"]), ("SCALE", pr["scale"])), widths)):
            self.text(k, x + 14, top, lab, color=p.grey, tracking=0.12)
            self.text(v, x + 14, top + 40, 18)
            if i:
                d.line(x, TB_Y0 + 8, x, TB_Y1 - 8, stroke=p.light, width=HAIR)
            x += cw

        # 5 — Key plan
        self.text("KEY PLAN", cells[4] + 12, top, lab, color=p.grey, tracking=0.12)
        self.key_plan(cells[4] + 14, TB_Y0 + 30, cells[5] - cells[4] - 28, TB_Y1 - TB_Y0 - 42)

        # 6 — Sheet number
        x = cells[5] + 12
        self.text("SHEET", x, top, lab, color=p.grey, tracking=0.12)
        self.text(self.number, (cells[5] + cells[6]) / 2, TB_Y1 - 30, 46, anchor="middle", weight="medium")

    # -- key plan -----------------------------------------------------------

    def key_plan(self, x: float, y: float, w: float, h: float) -> None:
        """Miniature of the site plan with the active zone(s) toned. Fits the
        plan's aspect ratio inside the cell."""
        from .site import LAYOUT, PH, PW
        d, p = self.doc, self.pal
        act = set(self.zones_active)
        every = act >= {"01", "02", "03", "04", "05"}
        k = min(w / PW, h / PH)
        pw, ph = PW * k, PH * k
        x += (w - pw) / 2
        y += (h - ph) / 2

        def R(r):
            rx, ry, rw, rh = r
            return (x + rx * pw, y + ry * ph, rw * pw, rh * ph)

        ox, oy, ow, oh = R(LAYOUT["outer"])
        ix, iy, iw, ih = R(LAYOUT["inner"])
        if "02" in act and not every:
            d.path(f"M{fmt(ox)},{fmt(oy)}h{fmt(ow)}v{fmt(oh)}h{fmt(-ow)}z M{fmt(ix)},{fmt(iy)}v{fmt(ih)}h{fmt(iw)}v{fmt(-ih)}z",
                   fill=p.ink, fill_rule="evenodd")
        d.rect(ox, oy, ow, oh, stroke=p.ink, width=1.6)
        d.rect(ix, iy, iw, ih, stroke=p.ink, width=0.8)
        for zid, r in LAYOUT["rooms"].items():
            rx, ry, rw, rh = R(r)
            on = zid in act and not every
            d.rect(rx, ry, rw, rh, stroke=p.ink, width=0.8, fill=p.ink if on else "none")


# -- geometry helpers used by several sheets -----------------------------------

def cloud_path(x: float, y: float, w: float, h: float, r: float = 9.0) -> str:
    """Revision cloud: scalloped arcs around a rectangle, bulging outward."""
    pts: list[tuple[float, float]] = []
    step = r * 1.7
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        (ax, ay), (bx, by) = corners[i], corners[(i + 1) % 4]
        seg = math.hypot(bx - ax, by - ay)
        n = max(1, round(seg / step))
        for k in range(n):
            t = k / n
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    d = [f"M{fmt(pts[0][0])},{fmt(pts[0][1])}"]
    for i in range(1, len(pts) + 1):
        px, py = pts[i % len(pts)]
        d.append(f"A{fmt(r)},{fmt(r)} 0 0 1 {fmt(px)},{fmt(py)}")
    return " ".join(d)


def hexagon_path(cx: float, cy: float, r: float) -> str:
    pts = [(cx + r * math.cos(math.radians(60 * i + 30)), cy + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    return "M" + " L".join(f"{fmt(px)},{fmt(py)}" for px, py in pts) + " Z"
