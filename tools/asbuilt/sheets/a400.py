"""A-400 — DOCUMENT ROOM. Four intake lines: paper and drawings in,
structured data out. Everything inside the dashed boundary runs on a local
server, on premises.
"""

from __future__ import annotations

from lib.sheet import Sheet
from lib.symbols import arrow, drawing_title, tag
from lib.theme import HAIR, HEAVY, MEDIUM

TITLE = "DOCUMENT ROOM"
SUBTITLE = "Intake lines. Documents and drawings in; structured, usable data out. Processing stays on premises."
DESC = ("Process diagram with four horizontal lines. Each line shows an input symbol (a stack of documents, "
        "a CAD sheet, a PDF page), an arrow into a numbered process box carrying a verb (Extract, Document, "
        "Convert, Edit), and an arrow to an output symbol (a table grid or a page stack). A dashed boundary "
        "around the process boxes is labelled Local Server, On Premises.")

LINES = [
    ("agentflow", "AGENCY DOCUMENTS", "docs",  "EXTRACT (OCR)",   "SALESFORCE-READY EXCEL", "grid"),
    ("cadauto",   "CAD DRAWINGS · SPECS", "cad", "DOCUMENT (OCR)", "STRUCTURED DOCUMENTATION", "pages"),
    ("pdftools",  "EMPLOYEE DOCUMENTS", "page", "CONVERT",        "PDF · EDITED · CONVERTED", "page"),
    ("amsih",     "PDF", "page",               "EDIT",           "LIGHTWEIGHT PDF EDITING", "page"),
]


def _sys(data, key):
    return next(s for s in data["systems"] if s["key"] == key)


def _symbol(s: Sheet, kind: str, x: float, y: float) -> None:
    """Small input/output symbols, all line-drawn. (x, y) is the centre."""
    p = s.pal
    if kind == "docs":
        for k in range(3):
            s.doc.rect(x - 30 + k * 6, y - 40 + k * 6, 56, 72, stroke=p.ink, width=MEDIUM, fill=p.paper)
        for k in range(5):
            s.doc.line(x - 8, y - 14 + k * 11, x + 32, y - 14 + k * 11, stroke=p.light, width=HAIR)
    elif kind == "cad":
        s.doc.rect(x - 44, y - 32, 88, 64, stroke=p.ink, width=MEDIUM, fill=p.paper)
        s.doc.rect(x - 38, y - 26, 76, 52, stroke=p.ink, width=HAIR)
        s.doc.rect(x + 6, y + 12, 32, 14, stroke=p.ink, width=HAIR)
        s.doc.line(x - 30, y - 10, x - 2, y - 10, stroke=p.ink, width=HAIR)
        s.doc.line(x - 30, y - 10, x - 30, y + 14, stroke=p.ink, width=HAIR)
        s.doc.circle(x - 14, y + 2, 7, stroke=p.ink, width=HAIR)
    elif kind == "page":
        s.doc.path(f"M{x-26},{y-36} h38 l14,14 v58 h-52 z", stroke=p.ink, width=MEDIUM, fill=p.paper)
        s.doc.path(f"M{x+12},{y-36} v14 h14", stroke=p.ink, width=HAIR)
        for k in range(4):
            s.doc.line(x - 14, y - 6 + k * 11, x + 14, y - 6 + k * 11, stroke=p.light, width=HAIR)
    elif kind == "pages":
        for k in range(2):
            s.doc.path(f"M{x-26+k*8},{y-36+k*8} h38 l14,14 v58 h-52 z", stroke=p.ink, width=MEDIUM, fill=p.paper)
        for k in range(4):
            s.doc.line(x - 6, y + 2 + k * 11, x + 22, y + 2 + k * 11, stroke=p.light, width=HAIR)
    elif kind == "grid":
        gx, gy, cw, ch, cols, rows = x - 48, y - 30, 24, 12, 4, 5
        s.doc.rect(gx, gy, cw * cols, ch * rows, stroke=p.ink, width=MEDIUM, fill=p.paper)
        for c in range(1, cols):
            s.doc.line(gx + c * cw, gy, gx + c * cw, gy + ch * rows, stroke=p.ink, width=HAIR)
        for r in range(1, rows):
            s.doc.line(gx, gy + r * ch, gx + cw * cols, gy + r * ch, stroke=p.ink, width=HAIR)
        s.doc.rect(gx, gy, cw * cols, ch, fill=p.light)


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "A-400", TITLE, SUBTITLE, DESC, zones_active=("03",))
    p = s.pal
    clouded = lambda sy: data["statuses"][sy["status"]]["cloud"]

    in_x, box_x, box_w, out_x = 300, 640, 420, 1360
    y0, pitch = 250, 190

    # Local-server boundary around all process boxes
    bx0, by0 = box_x - 60, y0 - 90
    bw, bh = box_w + 120, pitch * (len(LINES) - 1) + 180
    s.doc.rect(bx0, by0, bw, bh, stroke=p.ink, width=MEDIUM, stroke_dasharray="16 8")
    s.text("LOCAL SERVER — ON PREMISES", bx0 + bw / 2, by0 + bh + 26, 12, anchor="middle", tracking=0.18)
    s.text("NO DOCUMENT LEAVES THE SITE FOR PROCESSING", bx0 + bw / 2, by0 + bh + 46, 10, anchor="middle",
           color=p.grey, tracking=0.06)

    for i, (key, in_label, in_kind, verb, out_label, out_kind) in enumerate(LINES):
        sy = _sys(data, key)
        y = y0 + i * pitch
        # input
        _symbol(s, in_kind, in_x, y)
        s.text(in_label, in_x, y + 66, 10, anchor="middle", color=p.grey, tracking=0.1)
        arrow(s, in_x + 70, y, box_x - 6, y, width=MEDIUM)
        # process
        s.doc.rect(box_x, y - 44, box_w, 88, stroke=p.ink, width=HEAVY, fill=p.paper)
        tag(s, box_x + 16, y - 30, sy["no"], clouded=clouded(sy))
        s.text(sy["name"].upper(), box_x + 90, y - 14, 12, tracking=0.06)
        s.text(verb, box_x + 90, y + 12, 15, tracking=0.2)
        note = sy.get("note", "")
        if note:
            s.text(note.upper(), box_x + 90, y + 32, 9, color=p.grey, tracking=0.04)
        arrow(s, box_x + box_w + 6, y, out_x - 70, y, width=MEDIUM)
        # output
        _symbol(s, out_kind, out_x, y)
        s.text(out_label, out_x, y + 66, 10, anchor="middle", color=p.grey, tracking=0.1)

    # column headers
    hy = y0 - 130
    for x, lab in ((in_x, "INPUT"), (box_x + box_w / 2, "PROCESS"), (out_x, "OUTPUT")):
        s.text(lab, x, hy, 11, anchor="middle", tracking=0.22)
        s.doc.line(x - 40, hy + 8, x + 40, hy + 8, stroke=p.ink, width=HAIR)

    drawing_title(s, 150, 1008, "1", "DOCUMENT INTAKE LINES — PLAN", width=560)
    return {"main": s}
