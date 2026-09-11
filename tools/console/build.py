#!/usr/bin/env python3
"""CONTROL PLANE builder.

    python3 tools/console/build.py              # all cards + README
    python3 tools/console/build.py hero stack   # selected cards only
    python3 tools/console/build.py --png        # also rasterise previews (ImageMagick)
    python3 tools/console/build.py --sync       # refresh telemetry from GitHub first
    python3 tools/console/build.py --light      # CLEARANCE light-theme story flow -> assets/clearance

Deterministic: same data, byte-identical SVG. Never hand-edit assets/console.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import common                               # noqa: E402
from common import Fonts, load_data        # noqa: E402

PREVIEW = HERE / "_preview"


def write_readme(data: dict, theme: str) -> None:
    profile, systems = data["profile"], data["systems"]
    zones = {z["id"]: z["name"].title() for z in systems["zones"]}
    rows = []
    for s in systems["systems"]:
        st = {"BUILT": "Operational", "IN TEST": "In test", "IN DEV": "Deploying"}[s["status"]]
        io = f"{s['input']} → {s['output']}".replace("|", "/")
        rows.append(f"| {s['no']} | {s['name']} | {zones[s['zone']]} | {st} | {io} |")
    tpl = (HERE / ("readme_clearance.md" if theme == "light" else "readme_template.md")).read_text(encoding="utf-8")
    out = (tpl.replace("{{REGISTER}}", "\n".join(rows))
              .replace("{{HANDLE}}", profile["handle"])
              .replace("{{SITE}}", profile["site"])
              .replace("{{COUNT}}", str(len(systems["systems"]))))
    target = ROOT / ("README.md" if theme == active_theme_for_readme() else f"README.{theme}.md")
    target.write_text(out, encoding="utf-8")
    print(f"  {target.name}  {len(out)/1024:.0f} KB")


def active_theme_for_readme() -> str:
    """Which theme owns README.md. Switch here once a direction is approved."""
    return (HERE / "data" / "ACTIVE_THEME").read_text().strip() if (HERE / "data" / "ACTIVE_THEME").exists() else "dark"


def main(argv: list[str]) -> int:
    if "--sync" in argv:
        import github_data
        github_data.sync()
    want_png = "--png" in argv
    theme = "light" if "--theme=light" in argv or "--light" in argv else "dark"
    common.set_theme(theme)
    if theme == "light":
        from clearance import CARDS
        OUT = ROOT / "assets" / "clearance"
    else:
        from cards import CARDS
        OUT = ROOT / "assets" / "console"
    only = [a for a in argv if not a.startswith("--")]
    fonts = Fonts()
    data = load_data()
    built = []
    for name, make in CARDS.items():
        if only and name not in only:
            continue
        card = make(fonts, data)
        path = OUT / f"{name}.svg"
        card.save(path)
        built.append(path)
        print(f"  {path.relative_to(ROOT)}  {path.stat().st_size/1024:.0f} KB  ({card.h:.0f} h)")
    if not only:
        write_readme(data, theme)
    if want_png:
        PREVIEW.mkdir(exist_ok=True)
        for p in built:
            subprocess.run(["convert", "-density", "72", str(p), "-resize", "1800x", str(PREVIEW / (theme + "-" + p.stem + ".png"))], check=False)
        print(f"previews in {PREVIEW.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
