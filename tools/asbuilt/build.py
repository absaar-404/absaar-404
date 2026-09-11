#!/usr/bin/env python3
"""AS-BUILT sheet generator for the absaar-404 profile.

    python3 tools/asbuilt/build.py            # build every sheet, light + dark
    python3 tools/asbuilt/build.py A-100      # build one sheet
    python3 tools/asbuilt/build.py --png      # also rasterise previews (ImageMagick)
    python3 tools/asbuilt/build.py --readme   # (legacy) standalone drawing-set README — not used by the profile

Data in, sheets out. Deterministic: the same data produces byte-identical
SVG. Never hand-edit files in assets/sheets/.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

from lib.text import load_faces          # noqa: E402
from lib.theme import PALETTES           # noqa: E402
from sheets import REGISTRY              # noqa: E402

OUT = ROOT / "assets" / "sheets"
PREVIEW = HERE / "_preview"


def write_readme(data: dict) -> None:
    """Fill the README template. The schedule, index and notes come from the
    same data file as the sheets, so the README can never disagree with them."""
    from sheets.g000 import INDEX
    from sheets import a100, a200, a300, a400, a500, d501

    pr = data["project"]
    zones = {z["id"]: z["name"].title() for z in data["zones"]}
    rows = []
    for sy in data["systems"]:
        io = f"{sy['input']} → {sy['output']}".replace("|", "/")
        note = sy.get("note", "").replace("|", "/")
        rows.append(f"| {sy['no']} | {sy['name']} | {zones[sy['zone']]} | {sy['status']} | {io} | {note} |")
    index = []
    for no, title, note in INDEX:
        link = {"S-001": "#s-001--schedule", "R-001": "#r-001--revision-log"}.get(no)
        if link is None:
            link = f"assets/sheets/{no}-light.svg"
        index.append(f"| [{no}]({link}) | {title.title().replace(' · ', ' · ')} | {note} |")
    def sentence_case(text: str) -> str:
        parts = [x.strip() for x in text.split(". ") if x.strip()]
        out = ". ".join(x[:1].upper() + x[1:].lower() for x in parts)
        return out.replace("s-001", "S-001")

    notes = "\n".join(f"{i+1}. {sentence_case(n)}" for i, n in enumerate(data["general_notes"]))
    clouded = sum(1 for sy in data["systems"] if data["statuses"][sy["status"]]["cloud"])
    count = len(data["systems"])
    stats = (f"{count} systems. {count - clouded} built and in service; {clouded} in test or in development "
             f"(clouded on the sheets). Confidential work is not listed. Figures that have not been "
             f"characterised are not shown.")
    tpl = (HERE / "readme_template.md").read_text(encoding="utf-8")
    out = (tpl.replace("{{NUMBER}}", pr["number"]).replace("{{ISSUE}}", pr["issue"]).replace("{{REV}}", pr["revision"])
           .replace("{{INDEX}}", "\n".join(index)).replace("{{NOTES}}", notes)
           .replace("{{SCHEDULE}}", "\n".join(rows)).replace("{{STATS}}", stats)
           .replace("{{COUNT}}", str(count)).replace("{{CLOUDED}}", str(clouded))
           .replace("{{ALT_A100}}", a100.DESC).replace("{{ALT_A200}}", a200.DESC).replace("{{ALT_A300}}", a300.DESC)
           .replace("{{ALT_A400}}", a400.DESC).replace("{{ALT_A500}}", a500.DESC).replace("{{ALT_D501}}", d501.DESC))
    (ROOT / "README.md").write_text(out, encoding="utf-8")
    print(f"  README.md  {len(out)/1024:.0f} KB")


def main(argv: list[str]) -> int:
    want_png = "--png" in argv
    only = [a for a in argv if not a.startswith("--")]
    data = json.loads((HERE / "data" / "systems.json").read_text(encoding="utf-8"))
    faces, final = load_faces(HERE / "fonts")
    if not final:
        print("WARNING: lettering face missing — rendering with a system stand-in. Do not commit.", file=sys.stderr)

    built: list[Path] = []
    for number, make in REGISTRY.items():
        if only and number not in only:
            continue
        for pname, pal in PALETTES.items():
            for variant, sheet in make(faces, pal, data).items():
                suffix = "" if variant == "main" else f"-{variant}"
                path = OUT / f"{number}{suffix}-{pname}.svg"
                sheet.save(path)
                built.append(path)
                print(f"  {path.relative_to(ROOT)}  {path.stat().st_size/1024:.0f} KB")

    if "--readme" in argv:
        write_readme(data)

    if want_png:
        PREVIEW.mkdir(exist_ok=True)
        for p in built:
            png = PREVIEW / (p.stem + ".png")
            subprocess.run(["convert", "-density", "72", str(p), "-resize", "1800x", str(png)], check=False)
        print(f"previews in {PREVIEW.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
