"""Minimal SVG document builder.

Emits plain, dependency-free SVG. Everything GitHub's image proxy needs and
nothing it strips: no scripts, no external references, no fonts.
"""

from __future__ import annotations

from typing import Iterable
from xml.sax.saxutils import escape


def fmt(v: float) -> str:
    """Compact numeric formatting: 12.0 -> '12', 12.345 -> '12.35'."""
    if isinstance(v, int):
        return str(v)
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def attrs(**kw) -> str:
    parts = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        k = k.rstrip("_").replace("_", "-")
        if isinstance(v, float):
            v = fmt(v)
        parts.append(f'{k}="{escape(str(v), {chr(34): "&quot;"})}"')
    return (" " + " ".join(parts)) if parts else ""


class Doc:
    def __init__(self, width: float, height: float, background: str, title: str, desc: str):
        self.w = width
        self.h = height
        self.background = background
        self.title = title
        self.desc = desc
        self.defs: list[str] = []
        self.body: list[str] = []

    # --- primitives -------------------------------------------------------

    def add(self, s: str) -> None:
        self.body.append(s)

    def def_(self, s: str) -> None:
        self.defs.append(s)

    def line(self, x1, y1, x2, y2, stroke, width, **kw) -> None:
        self.add(f"<line{attrs(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=width, **kw)}/>")

    def rect(self, x, y, w, h, stroke=None, width=None, fill="none", **kw) -> None:
        self.add(f"<rect{attrs(x=x, y=y, width=w, height=h, stroke=stroke, stroke_width=width, fill=fill, **kw)}/>")

    def circle(self, cx, cy, r, stroke=None, width=None, fill="none", **kw) -> None:
        self.add(f"<circle{attrs(cx=cx, cy=cy, r=r, stroke=stroke, stroke_width=width, fill=fill, **kw)}/>")

    def path(self, d: str, stroke=None, width=None, fill="none", **kw) -> None:
        self.add(f"<path{attrs(d=d, stroke=stroke, stroke_width=width, fill=fill, **kw)}/>")

    def polyline(self, pts: Iterable[tuple[float, float]], stroke, width, fill="none", **kw) -> None:
        p = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)
        self.add(f"<polyline{attrs(points=p, stroke=stroke, stroke_width=width, fill=fill, **kw)}/>")

    def group(self, inner: Iterable[str], **kw) -> None:
        self.add(f"<g{attrs(**kw)}>" + "".join(inner) + "</g>")

    # --- output -----------------------------------------------------------

    def render(self) -> str:
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" '
            f'width="{fmt(self.w)}" height="{fmt(self.h)}" role="img" aria-labelledby="t d">'
            f"<title id=\"t\">{escape(self.title)}</title>"
            f"<desc id=\"d\">{escape(self.desc)}</desc>"
            f"{defs}"
            f'<rect width="{fmt(self.w)}" height="{fmt(self.h)}" fill="{self.background}"/>'
            + "".join(self.body)
            + "</svg>"
        )
