"""Lettering as outlines.

GitHub serves README images through a proxy that strips external
references, so an SVG cannot load a web font and cannot rely on the viewer's
installed fonts matching ours. Every piece of lettering on a sheet is
therefore converted to path geometry at build time with fontTools. The
result renders identically everywhere and is immune to font substitution.

One family is used on the sheets, in two weights: Regular for everything,
Medium only for the sheet number and project name in the title block.
Hierarchy otherwise comes from size, case and tracking — the way drawings
letter — not from mixing families.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from .svg import fmt


class Face:
    def __init__(self, path: str | Path):
        self.file = str(path)
        self.font = TTFont(self.file)
        self.upem = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]
        os2 = self.font["OS/2"] if "OS/2" in self.font else None
        self.cap_height = (getattr(os2, "sCapHeight", 0) or int(self.upem * 0.7)) / self.upem
        self.x_height = (getattr(os2, "sxHeight", 0) or int(self.upem * 0.5)) / self.upem
        self.kern = self._load_kern()

    # -- metrics -------------------------------------------------------------

    def _load_kern(self) -> dict[tuple[str, str], int]:
        """Flatten legacy `kern` and GPOS PairPos (formats 1 and 2) into a
        pair dictionary. Only the horizontal x-advance adjustment is used."""
        table: dict[tuple[str, str], int] = {}
        if "kern" in self.font:
            for sub in self.font["kern"].kernTables:
                if hasattr(sub, "kernTable"):
                    table.update(sub.kernTable)
        self._class_kern: list[tuple[dict, dict, list]] = []
        if "GPOS" in self.font:
            gpos = self.font["GPOS"].table
            lookups = []
            for feat in gpos.FeatureList.FeatureRecord:
                if feat.FeatureTag == "kern":
                    lookups.extend(feat.Feature.LookupListIndex)
            for li in sorted(set(lookups)):
                lookup = gpos.LookupList.Lookup[li]
                for st in lookup.SubTable:
                    if getattr(st, "LookupType", lookup.LookupType) == 9:
                        st = st.ExtSubTable
                    if getattr(st, "Format", 0) == 1 and hasattr(st, "PairSet"):
                        for first, ps in zip(st.Coverage.glyphs, st.PairSet):
                            for rec in ps.PairValueRecord:
                                v = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                                if v:
                                    table.setdefault((first, rec.SecondGlyph), v)
                    elif getattr(st, "Format", 0) == 2 and hasattr(st, "Class1Record"):
                        c1 = st.ClassDef1.classDefs if st.ClassDef1 else {}
                        c2 = st.ClassDef2.classDefs if st.ClassDef2 else {}
                        matrix = []
                        for r1 in st.Class1Record:
                            row = []
                            for r2 in r1.Class2Record:
                                row.append(getattr(r2.Value1, "XAdvance", 0) if r2.Value1 else 0)
                            matrix.append(row)
                        cov = set(st.Coverage.glyphs)
                        self._class_kern.append((c1, c2, matrix, cov))
        return table

    def kern_pair(self, a: str, b: str) -> int:
        v = self.kern.get((a, b))
        if v is not None:
            return v
        for c1, c2, matrix, cov in getattr(self, "_class_kern", []):
            if a not in cov:
                continue
            i, j = c1.get(a, 0), c2.get(b, 0)
            if i < len(matrix) and j < len(matrix[i]) and matrix[i][j]:
                return matrix[i][j]
        return 0

    def glyph_name(self, ch: str) -> str:
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?")) or ".notdef"

    def advance(self, ch: str, size: float) -> float:
        return self.hmtx[self.glyph_name(ch)][0] * size / self.upem

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        """Advance width of a string. `tracking` is extra space in em."""
        w = 0.0
        prev = None
        for ch in text:
            g = self.glyph_name(ch)
            if prev is not None:
                w += self.kern_pair(prev, g) * size / self.upem
                w += tracking * size
            w += self.hmtx[g][0] * size / self.upem
            prev = g
        return w

    # -- outlines ------------------------------------------------------------

    @lru_cache(maxsize=4096)
    def _glyph_commands(self, gname: str) -> str:
        pen = SVGPathPen(self.glyphs, ntos=lambda v: fmt(round(v, 1)))
        self.glyphs[gname].draw(pen)
        return pen.getCommands()

    def path(
        self,
        text: str,
        x: float,
        y: float,
        size: float,
        anchor: str = "start",
        tracking: float = 0.0,
    ) -> str:
        """Return an SVG path `d` for `text` with its baseline at (x, y).

        anchor: 'start' | 'middle' | 'end' — horizontal alignment about x.
        """
        total = self.width(text, size, tracking)
        if anchor == "middle":
            x -= total / 2
        elif anchor == "end":
            x -= total
        scale = size / self.upem
        parts: list[str] = []
        prev = None
        for ch in text:
            g = self.glyph_name(ch)
            if prev is not None:
                x += self.kern_pair(prev, g) * scale
                x += tracking * size
            pen = SVGPathPen(self.glyphs, ntos=lambda v: fmt(round(v, 1)))
            tpen = TransformPen(pen, (scale, 0, 0, -scale, x, y))
            self.glyphs[g].draw(tpen)
            d = pen.getCommands()
            if d:
                parts.append(d)
            x += self.hmtx[g][0] * scale
            prev = g
        return " ".join(parts)


REGULAR = "PetrumEX-Regular"
MEDIUM = "PetrumEX-Medium"

_STAND_INS = (
    "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
)


def load_faces(fonts_dir: Path) -> tuple[dict[str, Face], bool]:
    """Load the lettering faces.

    Returns ({'regular': Face, 'medium': Face}, is_final). `is_final` is
    False when falling back to a system stand-in for layout checks; the build
    prints a warning so a stand-in never ships silently.
    """
    files = {p.stem: p for p in list(fonts_dir.glob("*.otf")) + list(fonts_dir.glob("*.ttf"))}
    if REGULAR in files:
        reg = Face(files[REGULAR])
        med = Face(files[MEDIUM]) if MEDIUM in files else reg
        return {"regular": reg, "medium": med}, True
    for sys_path in _STAND_INS:
        if Path(sys_path).exists():
            f = Face(sys_path)
            return {"regular": f, "medium": f}, False
    raise SystemExit("No lettering face found. See tools/asbuilt/fonts/README.md.")
