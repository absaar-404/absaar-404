"""Drawing symbols: walls, checkpoints, tags, keynotes, dimensions, clouds.

Every symbol here has a drafting meaning and appears in the legend on
A-100. Nothing is decorative.
"""

from __future__ import annotations

import math

from .sheet import Sheet, cloud_path, hexagon_path
from .svg import fmt
from .theme import HAIR, HEAVY, MEDIUM

TAG_W, TAG_H = 58, 24


# -- walls and openings --------------------------------------------------------

def wall_band(s: Sheet, x: float, y: float, w: float, h: float, t: float) -> None:
    """Cut trust boundary: two heavy lines with poché between."""
    d, p = s.doc, s.pal
    d.path(
        f"M{fmt(x)},{fmt(y)}h{fmt(w)}v{fmt(h)}h{fmt(-w)}z "
        f"M{fmt(x+t)},{fmt(y+t)}v{fmt(h-2*t)}h{fmt(w-2*t)}v{fmt(-(h-2*t))}z",
        fill="url(#poche)", fill_rule="evenodd",
    )
    d.rect(x, y, w, h, stroke=p.ink, width=HEAVY)
    d.rect(x + t, y + t, w - 2 * t, h - 2 * t, stroke=p.ink, width=HEAVY)


def partition(s: Sheet, x1: float, y1: float, x2: float, y2: float) -> None:
    s.doc.line(x1, y1, x2, y2, stroke=s.pal.ink, width=MEDIUM)


def checkpoint(s: Sheet, x: float, y: float, length: float, orient: str, swing: int = 1,
               label: str = "CHK", thick: float = MEDIUM, gap_pad: float = 3.0) -> None:
    """Door symbol read as an access checkpoint: an opening in a boundary with
    a hairline leaf and quarter-arc swing. `orient` is 'h' for an opening in
    a horizontal wall at (x..x+length, y) or 'v' for a vertical wall."""
    d, p = s.doc, s.pal
    # knock out the wall
    if orient == "h":
        d.rect(x, y - thick - gap_pad, length, 2 * (thick + gap_pad), fill=p.paper)
        # leaf from hinge at x, swinging to the +swing side
        lx, ly = x, y + swing * length
        d.line(x, y, lx, ly, stroke=p.ink, width=HAIR)
        d.path(f"M{fmt(lx)},{fmt(ly)} A{fmt(length)},{fmt(length)} 0 0 {1 if swing<0 else 0} {fmt(x+length)},{fmt(y)}",
               stroke=p.ink, width=HAIR)
        tx, ty = x + length / 2, y + swing * (length + 12) + (4 if swing > 0 else 0)
    else:
        d.rect(x - thick - gap_pad, y, 2 * (thick + gap_pad), length, fill=p.paper)
        lx, ly = x + swing * length, y
        d.line(x, y, lx, ly, stroke=p.ink, width=HAIR)
        d.path(f"M{fmt(lx)},{fmt(ly)} A{fmt(length)},{fmt(length)} 0 0 {0 if swing<0 else 1} {fmt(x)},{fmt(y+length)}",
               stroke=p.ink, width=HAIR)
        tx, ty = x + swing * (length + 14), y + length / 2 + 4
    if label:
        s.text(label, tx, ty, 9, anchor="middle", color=p.grey, tracking=0.1)


# -- tags and notes ------------------------------------------------------------

def tag(s: Sheet, x: float, y: float, no: str, clouded: bool = False, w: float = TAG_W, h: float = TAG_H) -> None:
    """System tag: numbered rectangle, see Schedule S-001."""
    d, p = s.doc, s.pal
    d.rect(x, y, w, h, stroke=p.ink, width=MEDIUM, fill=p.paper)
    s.text(no, x + w / 2, y + h / 2 + 4.5, 13, anchor="middle", tracking=0.04)
    if clouded:
        cloud(s, x - 7, y - 7, w + 14, h + 14)


def cloud(s: Sheet, x: float, y: float, w: float, h: float, r: float = 8.0) -> None:
    """Revision cloud — the only red on the sheet."""
    s.doc.path(cloud_path(x, y, w, h, r), stroke=s.pal.red, width=HAIR * 1.8)


def room_tag(s: Sheet, cx: float, cy: float, name: str, zid: str, size: float = 15) -> None:
    s.text(name, cx, cy, size, anchor="middle", tracking=0.16)
    bw, bh = 38, 18
    s.doc.rect(cx - bw / 2, cy + 8, bw, bh, stroke=s.pal.ink, width=HAIR)
    s.text(zid, cx, cy + 8 + bh - 5, 11, anchor="middle")


def keynote(s: Sheet, x: float, y: float, n: str, r: float = 11.0) -> None:
    s.doc.path(hexagon_path(x, y, r), stroke=s.pal.ink, width=MEDIUM, fill=s.pal.paper)
    s.text(n, x, y + 4, 10.5, anchor="middle")


def leader(s: Sheet, pts: list[tuple[float, float]], text: str = "", size: float = 11,
           anchor: str = "start", color: str | None = None) -> None:
    d, p = s.doc, s.pal
    d.polyline(pts, stroke=p.ink, width=HAIR)
    x0, y0 = pts[0]
    d.circle(x0, y0, 1.6, fill=p.ink)
    if text:
        xe, ye = pts[-1]
        dx = 6 if anchor == "start" else -6
        s.text(text, xe + dx, ye + 4, size, anchor=anchor, color=color)


# -- dimensions ----------------------------------------------------------------

def dimension(s: Sheet, x1: float, y1: float, x2: float, y2: float, label: str,
              offset: float = 0.0, size: float = 11, flip: bool = False) -> None:
    """Dimension string with 45° tick terminators. Labels are counts, never
    lengths — the sheet is NTS."""
    d, p = s.doc, s.pal
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    ax, ay = x1 + nx * offset, y1 + ny * offset
    bx, by = x2 + nx * offset, y2 + ny * offset
    d.line(ax, ay, bx, by, stroke=p.ink, width=HAIR)
    # extension lines
    if offset:
        d.line(x1, y1, ax + nx * 6, ay + ny * 6, stroke=p.ink, width=HAIR)
        d.line(x2, y2, bx + nx * 6, by + ny * 6, stroke=p.ink, width=HAIR)
    # ticks
    for (tx, ty) in ((ax, ay), (bx, by)):
        t = 5
        d.line(tx - (ux - nx) * t, ty - (uy - ny) * t, tx + (ux - nx) * t, ty + (uy - ny) * t, stroke=p.ink, width=MEDIUM)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    if abs(ux) >= abs(uy):
        s.text(label, mx, my + (size + 6 if flip else -5), size, anchor="middle")
    else:
        # vertical string: label beside the line, on the side away from the object
        if flip:
            s.text(label, mx - 8, my + 4, size, anchor="end")
        else:
            s.text(label, mx + 8, my + 4, size, anchor="start")


# -- section reference -----------------------------------------------------------

def section_marker(s: Sheet, x: float, y: float, letter: str, sheet: str, direction: str = "right") -> None:
    """Section cut reference bubble: letter over sheet number, arrow shows view direction."""
    d, p = s.doc, s.pal
    r = 16
    d.circle(x, y, r, stroke=p.ink, width=MEDIUM, fill=p.paper)
    d.line(x - r, y, x + r, y, stroke=p.ink, width=HAIR)
    s.text(letter, x, y - 3, 11, anchor="middle")
    s.text(sheet, x, y + 12, 8.5, anchor="middle")
    if direction == "right":
        d.path(f"M{fmt(x+r)},{fmt(y-10)} l14,10 l-14,10 z", fill=p.ink)
    elif direction == "left":
        d.path(f"M{fmt(x-r)},{fmt(y-10)} l-14,10 l14,10 z", fill=p.ink)
    elif direction == "down":
        d.path(f"M{fmt(x-10)},{fmt(y+r)} l10,14 l10,-14 z", fill=p.ink)
    elif direction == "up":
        d.path(f"M{fmt(x-10)},{fmt(y-r)} l10,-14 l10,14 z", fill=p.ink)


def drawing_title(s: Sheet, x: float, y: float, no: str, title: str, width: float = 420) -> None:
    """Drawing title convention: number bubble, title, heavy underline, scale."""
    d, p = s.doc, s.pal
    d.circle(x + 16, y - 8, 16, stroke=p.ink, width=MEDIUM)
    s.text(no, x + 16, y - 3.5, 12, anchor="middle")
    s.text(title, x + 44, y - 2, 18, tracking=0.14)
    d.line(x + 40, y + 8, x + width, y + 8, stroke=p.ink, width=HEAVY)
    s.text("SCALE: NTS", x + 44, y + 24, 10.5, color=p.grey, tracking=0.12)


def arrow(s: Sheet, x1: float, y1: float, x2: float, y2: float, width: float = HAIR, head: float = 9) -> None:
    d, p = s.doc, s.pal
    d.line(x1, y1, x2, y2, stroke=p.ink, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + math.radians(160), ang - math.radians(160)
    d.path(
        f"M{fmt(x2)},{fmt(y2)} L{fmt(x2+head*math.cos(a1))},{fmt(y2+head*math.sin(a1))} "
        f"L{fmt(x2+head*math.cos(a2))},{fmt(y2+head*math.sin(a2))} z", fill=p.ink,
    )
