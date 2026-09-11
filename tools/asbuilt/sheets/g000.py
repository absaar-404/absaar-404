"""G-000 — COVER AND SHEET INDEX.

The cover carries the project name, the key plan at reading size, the sheet
index and the general notes — the philosophy written as drawing notes.
"""

from __future__ import annotations

from lib.sheet import Sheet
from lib.site import PH, PW, PX0, PY0
from lib.theme import HAIR, HEAVY, MEDIUM
from sheets.a100 import draw_plan

TITLE = "COVER · INDEX"
SUBTITLE = "As-built drawing set. Sheet index and general notes."
DESC = ("Cover sheet. Large project title Nebula Core Cluster, Root Sector, As-Built Drawing Set, drawn by "
        "Absaar IT, Principal DevSecOps and Systems Architect. A key plan of the compound with five zones. "
        "A sheet index listing G-000, A-100, A-200, A-300, A-400, A-500, D-501, S-001, R-001. "
        "General notes numbered one to eight.")

INDEX = [
    ("G-000", "COVER · INDEX", "Sheet index, general notes"),
    ("A-100", "SITE PLAN", "All systems located by zone"),
    ("A-200", "FLEET FLOOR", "Onboarding riser; Service Core enlarged"),
    ("A-300", "SECURITY SECTION", "Section A-A: IAS enclosure; SOC rack"),
    ("A-400", "DOCUMENT ROOM", "Intake lines: documents in, data out"),
    ("A-500", "ANNEX", "Spatial and creative systems; camera stations"),
    ("D-501", "CAPTURE DETAIL", "HayaScope capture boundary"),
    ("S-001", "SCHEDULE", "All systems, status and notes (README)"),
    ("R-001", "REVISION LOG", "Issue history (README)"),
]


def make(faces, pal, data) -> dict:
    pr = data["project"]
    s = Sheet(faces, pal, pr, "G-000", TITLE, SUBTITLE, DESC, zones_active=())
    p = s.pal

    # Title block of the cover (large)
    x, y = 150, 250
    s.text("AS-BUILT DRAWING SET", x, y, 15, tracking=0.3, color=p.grey)
    s.text(pr["name"], x, y + 84, 62, tracking=0.02, weight="medium")
    s.text(pr["sector"], x, y + 126, 26, tracking=0.24)
    s.doc.line(x, y + 156, x + 640, y + 156, stroke=p.ink, width=HEAVY)
    s.text(f"DRAWN BY  {pr['drawn_by']}", x, y + 196, 17, tracking=0.12)
    s.text(pr["role"], x, y + 222, 12.5, tracking=0.1, color=p.grey)
    s.text(f"{pr['site']}   ·   github.com/{pr['github']}", x, y + 246, 12.5, color=p.grey)
    s.text(f"PROJECT NO. {pr['number']}   ·   ISSUE {pr['issue']}   ·   REV {pr['revision']}   ·   {pr['scale']}",
           x, y + 270, 11, color=p.grey, tracking=0.1)

    # Sheet index
    ix, iy = 150, 600
    s.text("SHEET INDEX", ix, iy, 13, tracking=0.16)
    s.doc.line(ix, iy + 10, ix + 640, iy + 10, stroke=p.ink, width=HEAVY)
    yy = iy + 40
    for no, title, note in INDEX:
        s.text(no, ix, yy, 13, weight="medium")
        s.text(title, ix + 90, yy, 12.5, tracking=0.08)
        s.text(note.upper(), ix + 300, yy, 10, color=p.grey, tracking=0.04)
        s.doc.line(ix, yy + 10, ix + 640, yy + 10, stroke=p.light, width=HAIR)
        yy += 30

    # Key plan at reading size
    kx, ky, kw = 960, 176, 740
    scale = kw / PW
    draw_plan(s, data, kx - PX0 * scale, ky - PY0 * scale, scale, dense=False)
    zones = {z["id"]: z for z in data["zones"]}
    s.text("KEY PLAN — ZONES", kx, ky - 14, 11, tracking=0.16, color=p.grey)

    # General notes
    nx, ny = 960, 810
    s.text("GENERAL NOTES", nx, ny, 13, tracking=0.16)
    s.doc.line(nx, ny + 10, 1700, ny + 10, stroke=p.ink, width=HEAVY)
    yy = ny + 36
    for i, note in enumerate(data["general_notes"]):
        s.text(f"{i+1}.", nx, yy, 10.5)
        s.text(note, nx + 26, yy, 10.5, tracking=0.03)
        yy += 20

    return {"main": s}
