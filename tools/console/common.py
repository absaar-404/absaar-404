"""CONTROL PLANE — shared card framework.

Every card is a dark ops-console panel, 1800 units wide, rendered as a
self-contained SVG with all lettering converted to outlines. One structural
accent (cyan); status uses ops semantics only: green = operational,
amber = deploying / in test. Animation is SMIL, subtle and continuous.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "asbuilt"))

from lib.svg import Doc, fmt          # noqa: E402
from lib.text import Face             # noqa: E402

FONTS = ROOT / "tools" / "asbuilt" / "fonts"

W = 1800

class Palette:
    """All colour decisions live here. Two themes: DARK (console) and LIGHT (clearance)."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


DARK = Palette(
    name="dark", bg="#0B0F14", panel="#0F151C", panel2="#121A23", grid="#141C26", line="#22303F",
    text="#E6EDF3", muted="#8593A3", dim="#4B5866",
    accent="#22D3EE", ok="#22C55E", warn="#F59E0B", alert="#EF4444",
    blue="#3B82F6", purple="#8B5CF6", cyan="#22D3EE", red="#EF4444", gold="#EAB308", teal="#14B8A6", magenta="#EC4899",
    glass_opacity=0.75, shadow=False,
)

LIGHT = Palette(
    name="light", bg="#F6F8FB", panel="#FFFFFF", panel2="#FFFFFF", grid="#DCE3EC", line="#D5DDE7",
    text="#0F172A", muted="#5B6B7F", dim="#94A3B8",
    accent="#0EA5E9", ok="#059669", warn="#D97706", alert="#DC2626",
    blue="#2563EB", purple="#7C3AED", cyan="#0891B2", red="#DC2626", gold="#CA8A04", teal="#0D9488", magenta="#DB2777",
    glass_opacity=0.82, shadow=True,
)

P = DARK


def set_theme(name: str) -> Palette:
    global P
    P = LIGHT if name == "light" else DARK
    return P


class _Tok:
    """Module-level colour tokens that follow the active palette."""
    def __getattr__(self, k):
        return getattr(P, k)


# Backwards-compatible token names used by the cards.
class _Colors:
    @property
    def BG(self): return P.bg
    @property
    def PANEL(self): return P.panel
    @property
    def PANEL2(self): return P.panel2
    @property
    def GRID(self): return P.grid
    @property
    def LINE(self): return P.line
    @property
    def TEXT(self): return P.text
    @property
    def MUTED(self): return P.muted
    @property
    def DIM(self): return P.dim
    @property
    def ACCENT(self): return P.accent
    @property
    def OK(self): return P.ok
    @property
    def WARN(self): return P.warn
    @property
    def ALERT(self): return P.alert


C = _Colors()


class Fonts:
    def __init__(self) -> None:
        # Labels and small text use the same family as display/body (PetrumEX) so
        # nothing small looks like a different, thinner font. A monospace face is
        # kept only for terminal lines, where character alignment matters.
        req = {
            "display": "PetrumEX-Medium.otf",
            "body": "PetrumEX-Regular.otf",
            "mono": "PetrumEX-Regular.otf",
            "mono_m": "PetrumEX-Medium.otf",
            "term": "GCRobutoMono-Regular.otf",
            "term_m": "GCRobutoMono-Medium.otf",
        }
        missing = [f for f in req.values() if not (FONTS / f).exists()]
        if missing:
            raise SystemExit(f"Lettering faces missing in {FONTS}: {missing}. See tools/asbuilt/fonts/README.md.")
        self.display = Face(FONTS / req["display"])
        self.body = Face(FONTS / req["body"])
        self.mono = Face(FONTS / req["mono"])
        self.mono_m = Face(FONTS / req["mono_m"])
        self.term = Face(FONTS / req["term"])
        self.term_m = Face(FONTS / req["term_m"])


def load_data() -> dict:
    systems = json.loads((ROOT / "tools/asbuilt/data/systems.json").read_text(encoding="utf-8"))
    profile = json.loads((HERE / "data" / "profile.json").read_text(encoding="utf-8"))
    tpath = HERE / "data" / "telemetry.json"
    telemetry = json.loads(tpath.read_text(encoding="utf-8")) if tpath.exists() else {}
    return {"systems": systems, "profile": profile, "telemetry": telemetry}


class Card:
    """A console panel. `height` in sheet units. Provides text helpers."""

    def __init__(self, fonts: Fonts, height: float, title: str, desc: str, code: str = "",
                 heading: str = "", status: tuple[str, str] | None = None, accent: str | None = None):
        self.f = fonts
        self.p = P
        self.accent = accent or P.accent
        self.w, self.h = W, height
        self.doc = Doc(W, height, P.bg, title, desc)
        d = self.doc
        d.def_(f'<pattern id="dots" patternUnits="userSpaceOnUse" width="36" height="36"><circle cx="1" cy="1" r="1.1" fill="{P.grid}"/></pattern>')
        d.def_('<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>')
        d.def_('<filter id="glow2" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>')
        d.def_('<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#0F172A" flood-opacity="0.08"/></filter>')
        d.def_(f'<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="0" stop-color="{P.panel if P.name == "dark" else "#FFFFFF"}"/><stop offset="1" stop-color="{P.bg}"/></radialGradient>')
        d.def_(f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{self.accent}" stop-opacity="0"/><stop offset="1" stop-color="{self.accent}" stop-opacity="0.55"/></linearGradient>')
        d.def_(f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{self.accent}" stop-opacity="0.35"/><stop offset="1" stop-color="{self.accent}" stop-opacity="0"/></linearGradient>')
        d.def_(f'<linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{self.accent}"/><stop offset="1" stop-color="{self.accent}" stop-opacity="0.15"/></linearGradient>')
        hi = "#FFFFFF" if P.name == "dark" else self.accent
        d.def_(f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{hi}" stop-opacity="0"/>'
               f'<stop offset="0.5" stop-color="{hi}" stop-opacity="0.9"/><stop offset="1" stop-color="{hi}" stop-opacity="0"/></linearGradient>')
        d.rect(0, 0, W, height, fill="url(#vig)")
        d.rect(0, 0, W, height, fill="url(#dots)")
        d.rect(1, 1, W - 2, height - 2, stroke=P.line, width=2, rx=18)
        if P.name == "light":
            # accent band along the top edge — the light theme's section colour
            d.rect(1, 1, W - 2, 6, fill="url(#band)", rx=3)
        if heading:
            self.header(code, heading, status)

    # -- lettering ---------------------------------------------------------

    _shine_n = 0

    def t(self, face: Face, s: str, x: float, y: float, size: float, color: str | None = None,
          anchor: str = "start", tracking: float = 0.0, opacity: float | None = None, shine: bool = False) -> float:
        if not s:
            return 0.0
        d = face.path(s, x, y, size, anchor=anchor, tracking=tracking)
        self.doc.path(d, fill=color or P.text, opacity=opacity)
        w = face.width(s, size, tracking)
        if shine and w > 0:
            # a band of light passing over the letters, clipped to the glyphs
            Card._shine_n += 1
            cid = f"sh{Card._shine_n}"
            x0 = x - (w / 2 if anchor == "middle" else (w if anchor == "end" else 0))
            self.doc.def_(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
            band = max(60.0, w * 0.35)
            begin = (Card._shine_n * 0.7) % 5.0
            self.doc.add(f'<g clip-path="url(#{cid})"><rect x="{fmt(x0 - band)}" y="{fmt(y - size * 1.2)}" width="{fmt(band)}" '
                         f'height="{fmt(size * 1.6)}" fill="url(#shine)">'
                         f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{fmt(w + 2 * band)} 0" '
                         f'begin="{begin:.2f}s" dur="2.2s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1"/></rect></g>')
        return w

    def mono(self, s, x, y, size, color=None, anchor="start", tracking=0.12, opacity=None, medium=False, shine=False):
        # small text is set in the label face at a legible floor; tracking is
        # scaled down because the label face is proportional, not monospaced
        size = size * 1.18 if size < 14 else size
        size = max(size, 12.0)
        return self.t(self.f.mono_m if medium else self.f.mono, s, x, y, size, color or P.muted, anchor, tracking * 0.55, opacity, shine)

    def term(self, s, x, y, size, color=None, anchor="start", tracking=0.04, medium=False):
        """Terminal lines: the one place a monospace face is used."""
        return self.t(self.f.term_m if medium else self.f.term, s, x, y, max(size, 13.0), color or P.text, anchor, tracking)

    def display(self, s, x, y, size, color=None, anchor="start", tracking=0.02, shine=True):
        return self.t(self.f.display, s, x, y, size, color or P.text, anchor, tracking, None, shine)

    def body(self, s, x, y, size, color=None, anchor="start", tracking=0.0):
        return self.t(self.f.body, s, x, y, size, color or P.text, anchor, tracking)

    def wrap(self, face: Face, s: str, size: float, max_w: float, tracking: float = 0.0) -> list[str]:
        words, out, cur = s.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if face.width(trial, size, tracking) <= max_w or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out

    # -- furniture ---------------------------------------------------------

    def header(self, code: str, heading: str, status: tuple[str, str] | None) -> None:
        """Card header strip: code tag, heading, optional status pill on the right."""
        d = self.doc
        self.mono(code, 72, 66, 11.5, P.dim, tracking=0.24)
        self.mono(heading, 72, 96, 19, P.text, tracking=0.22, medium=True, shine=True)
        if status:
            label, color = status
            w = self.f.mono_m.width(label, 12.5, 0.14) + 58
            px, py = 1728 - w, 60
            d.rect(px, py, w, 34, stroke=color, width=1.2, fill=P.panel, rx=17, fill_opacity=0.9)
            self.led(px + 20, py + 17, color, r=4)
            self.mono(label, px + 36, py + 21.5, 12.5, color, tracking=0.14, medium=True)
        d.line(72, 122, 1728, 122, stroke=P.line, width=1)

    def led(self, x: float, y: float, color: str, r: float = 3.0, dur: float = 2.4) -> None:
        d = self.doc
        d.circle(x, y, r + 3, fill=color, filter="url(#glow)", opacity=0.55)
        d.add(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{color}">'
              f'<animate attributeName="opacity" values="1;0.35;1" dur="{dur}s" repeatCount="indefinite"/></circle>')

    def panel(self, x: float, y: float, w: float, h: float, title: str = "", rx: float = 10) -> None:
        d = self.doc
        d.rect(x, y, w, h, fill=P.panel2, stroke=P.line, width=1, rx=rx, fill_opacity=P.glass_opacity,
               filter="url(#shadow)" if P.shadow else None)
        if title:
            self.mono(title, x + 18, y + 26, 10.5, P.dim, tracking=0.22)
            d.line(x + 18, y + 36, x + w - 18, y + 36, stroke=P.line, width=1)

    def kpi(self, x: float, y: float, big: str, small: str, color: str | None = None, size: float = 34) -> None:
        self.display(big, x, y, size, color or P.text, shine=True)
        self.mono(small, x, y + 20, 9.5, P.muted, tracking=0.16)

    def bar(self, x: float, y: float, w: float, h: float, frac: float, color: str | None = None, track: str | None = None) -> None:
        d = self.doc
        color = color or self.accent
        track = track or P.line
        d.rect(x, y, w, h, fill=track, rx=h / 2)
        fw = max(h, w * max(0.0, min(1.0, frac)))
        d.rect(x, y, fw, h, fill=color, rx=h / 2)

    def packet(self, x1, y1, x2, y2, dur: float, color: str | None = None, r: float = 3.0, begin: float = 0.0) -> None:
        color = color or self.accent
        self.doc.add(f'<circle r="{fmt(r)}" fill="{color}"><animateMotion dur="{dur}s" begin="{begin}s" '
                     f'repeatCount="indefinite" path="M{fmt(x1)},{fmt(y1)} L{fmt(x2)},{fmt(y2)}"/></circle>')

    def hexagon(self, x: float, y: float, r: float) -> str:
        pts = [(x + r * math.cos(math.radians(60 * i + 30)), y + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
        return "M" + " L".join(f"{fmt(a)},{fmt(b)}" for a, b in pts) + " Z"

    def logo(self, x: float, y: float, size: float, shape: str = "round") -> None:
        """Embed the brand mark (small JPEG, base64) clipped to a rounded tile or hexagon."""
        import base64
        data = base64.b64encode((HERE / "data" / "mark.jpg").read_bytes()).decode()
        Card._shine_n += 1
        cid = f"lg{Card._shine_n}"
        if shape == "hex":
            self.doc.def_(f'<clipPath id="{cid}"><path d="{self.hexagon(x + size / 2, y + size / 2, size / 2)}"/></clipPath>')
        else:
            self.doc.def_(f'<clipPath id="{cid}"><rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" rx="{fmt(size * 0.22)}"/></clipPath>')
        self.doc.add(f'<image x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" clip-path="url(#{cid})" '
                     f'href="data:image/jpeg;base64,{data}" preserveAspectRatio="xMidYMid slice"/>')

    def footer(self, left: str, right: str = "") -> None:
        y = self.h - 34
        self.doc.line(72, y - 26, 1728, y - 26, stroke=P.line, width=1)
        self.mono(left, 72, y, 10, P.dim, tracking=0.18)
        if right:
            self.mono(right, 1728, y, 10, P.dim, anchor="end", tracking=0.18)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.doc.render(), encoding="utf-8")
