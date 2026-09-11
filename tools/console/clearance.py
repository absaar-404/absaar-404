"""CLEARANCE — light-theme story flow.

The visitor is walked through a command centre in daylight: boot, identity
check, mission briefing, live operations, threat classes, architecture,
automation, arsenal, ecosystem, certification vault, timeline and lab,
telemetry, comms. Each card carries its own section colour; motion is SMIL.
"""

from __future__ import annotations

import math

from common import C, Card, Fonts, P, fmt
import cards as dark_cards


def _hue(name: str) -> str:
    return getattr(P, name)


def _typewriter(c: Card, lines: list[str], x: float, y: float, size: float, color: str,
                start: float, per_char: float = 0.035, gap: float = 0.35, prompt: str = "> ") -> float:
    """Reveal outlined text left-to-right with an animated clip — a typing effect
    that needs no font on the viewer's machine. Returns the time when done."""
    d = c.doc
    t = start
    for i, ln in enumerate(lines):
        text = prompt + ln
        w = c.f.term.width(text, size, 0.04) + 6
        dur = max(0.4, len(text) * per_char)
        cid = f"tw{abs(hash((x, y, i, ln))) % 10**8}"
        d.def_(f'<clipPath id="{cid}"><rect x="{fmt(x-2)}" y="{fmt(y-size)}" width="0" height="{fmt(size*1.5)}">'
               f'<animate attributeName="width" from="0" to="{fmt(w)}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        d.add(f'<g clip-path="url(#{cid})">')
        c.term(text, x, y, size, color)
        d.add("</g>")
        t += dur + gap
        y += size * 2.1
    # cursor
    d.add(f'<rect x="{fmt(x)}" y="{fmt(y - size)}" width="{fmt(size*0.6)}" height="{fmt(size*1.2)}" fill="{color}" opacity="0">'
          f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0;1" keyTimes="0;{min(0.99, t/(t+6)):.3f};0.6;0.7;0.8;0.85;0.9;0.95;1" dur="{t+6:.2f}s" repeatCount="indefinite"/></rect>')
    return t


def _torus_frames(n: int = 24, cols: int = 48, rows: int = 22) -> list[list[str]]:
    """ASCII torus, Lambert-shaded. Own implementation of the classic rotating
    solid; frames are rendered once at build time and loop seamlessly."""
    chars = " .,-~:;=!*#$@"
    frames = []
    R1, R2, K2 = 1.0, 2.0, 5.0
    K1 = cols * K2 * 3 / (8 * (R1 + R2))
    for k in range(n):
        A, B = 2 * math.pi * k / n, 4 * math.pi * k / n
        z = [[0.0] * cols for _ in range(rows)]
        out = [[" "] * cols for _ in range(rows)]
        cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
        th = 0.0
        while th < 2 * math.pi:
            ct, st = math.cos(th), math.sin(th)
            ph = 0.0
            while ph < 2 * math.pi:
                cp, sp = math.cos(ph), math.sin(ph)
                cx = R2 + R1 * ct
                cy = R1 * st
                x = cx * (cB * cp + sA * sB * sp) - cy * cA * sB
                y = cx * (sB * cp - sA * cB * sp) + cy * cA * cB
                zz = K2 + cA * cx * sp + cy * sA
                ooz = 1 / zz
                xp = int(cols / 2 + K1 * ooz * x)
                yp = int(rows / 2 - K1 * ooz * y * 0.5)
                L = cp * ct * sB - cA * ct * sp - sA * st + cB * (cA * st - ct * sA * sp)
                if 0 <= xp < cols and 0 <= yp < rows and ooz > z[yp][xp]:
                    z[yp][xp] = ooz
                    out[yp][xp] = chars[max(0, min(len(chars) - 1, int((L + 0.2) * 7)))]
                ph += 0.02
            th += 0.07
        frames.append(["".join(r).rstrip() for r in out])
    return frames


ASCII_DIR = __import__("pathlib").Path(__file__).resolve().parent / "data" / "ascii"


def _image_frames(path, cols: int = 60, rows: int = 26, n: int = 16) -> list[list[str]]:
    """Turn any picture into ASCII frames with a band of light sweeping across it.
    Drop a PNG/JPG at tools/console/data/ascii/source.* and it replaces the torus.
    Dark or transparent background becomes empty space; the subject is cropped
    to its bounding box first so it fills the frame."""
    from PIL import Image, ImageOps
    img = Image.open(path).convert("RGBA")
    # flatten transparency onto black, then to luminance
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    img = Image.alpha_composite(bg, img).convert("L")
    # crop to the subject: anything brighter than the floor
    mask = img.point(lambda v: 255 if v > 40 else 0)
    box = mask.getbbox()
    if box:
        img = img.crop(box)
    img = ImageOps.autocontrast(img, cutoff=1)
    iw, ih = img.size
    scale = min(cols / iw, (rows * 2) / ih)
    tw, th = max(1, int(iw * scale)), max(1, int(ih * scale / 2))
    img = img.resize((tw, th), Image.LANCZOS)
    px = img.load()
    ramp = " .:-=+*#%@"
    frames = []
    for k in range(n):
        band = -0.3 + 1.6 * k / n            # band centre sweeps left to right
        out = []
        for yy in range(th):
            row = []
            for xx in range(tw):
                v = px[xx, yy] / 255.0
                if v < 0.12:
                    row.append(" ")           # background stays empty
                    continue
                d = abs(xx / tw - band)
                v = min(1.0, v + max(0.0, 0.22 - d) * 1.6)
                row.append(ramp[int(v * (len(ramp) - 1))])
            out.append("".join(row).rstrip())
        frames.append(out)
    return frames


def _text_frames() -> list[list[str]] | None:
    """User-drawn frames: tools/console/data/ascii/frame-01.txt, frame-02.txt ...
    Each file is one frame; all frames should have the same width."""
    files = sorted(ASCII_DIR.glob("frame-*.txt"))
    if not files:
        return None
    return [f.read_text(encoding="utf-8").rstrip("\n").split("\n") for f in files]


def _pick_frames() -> tuple[list[list[str]], str]:
    tf = _text_frames()
    if tf:
        return tf, f"CUSTOM · {len(tf)} FRAMES"
    for ext in ("png", "jpg", "jpeg", "gif", "webp"):
        src = ASCII_DIR / f"source.{ext}"
        if src.exists():
            return _image_frames(src), "FROM IMAGE · LIGHT SWEEP"
    return _torus_frames(), "PROCEDURAL · 24 FRAMES · NO IMAGES"


def _ascii_animation(c: Card, x: float, y: float, w: float, h: float, color: str, cycle: float = 3.6) -> None:
    """Frame-flip ASCII animation using system monospace text (any monospace
    aligns identically, so this is the one place plain <text> is acceptable)."""
    frames, _ = _pick_frames()
    n = len(frames)
    rows = max(len(fr) for fr in frames)
    cols = max(len(line) for fr in frames for line in fr) or 48
    fs = min(h / (rows * 1.05), w / (cols * 0.62))
    lh = fs * 1.05
    for i, fr in enumerate(frames):
        s0, s1 = i / n, (i + 1) / n
        kt = f"0;{s0:.4f};{s0:.4f};{s1:.4f};{s1:.4f};1" if i < n - 1 else f"0;{s0:.4f};{s0:.4f};1"
        vals = "0;0;1;1;0;0" if i < n - 1 else "0;0;1;1"
        c.doc.add(f'<g opacity="0"><animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite" calcMode="discrete"/>')
        for r, line in enumerate(fr):
            if not line.strip():
                continue
            safe = line.replace("&", "&amp;").replace("<", "&lt;")
            c.doc.add(f'<text x="{fmt(x)}" y="{fmt(y + (r+1)*lh)}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
                      f'font-size="{fmt(fs)}" fill="{color}" xml:space="preserve">{safe}</text>')
        c.doc.add("</g>")


# =============================================================== 01 · BOOT
def boot(f: Fonts, data: dict) -> Card:
    profile = data["profile"]
    c = Card(f, 720, "System boot", "Boot sequence terminal with a typewriter log and an ASCII rendering of a rotating core.",
             code="SEQ · 01", heading="SYSTEM BOOT", status=("POWER ON", P.ok), accent=P.blue)
    d = c.doc
    # terminal window (light chrome)
    tx, ty, tw, th = 72, 156, 1040, 470
    c.panel(tx, ty, tw, th)
    d.rect(tx, ty, tw, 40, fill="#EEF2F7", rx=10)
    d.rect(tx, ty + 30, tw, 10, fill="#EEF2F7")
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        d.circle(tx + 22 + i * 20, ty + 20, 6, fill=col)
    c.mono("absaar@root-sector: ~", tx + tw / 2, ty + 25, 11, P.muted, anchor="middle", tracking=0.1)
    _typewriter(c, profile["brief"]["boot"], tx + 28, ty + 84, 14.5, P.text, start=0.4)
    # progress bar
    d.rect(tx + 28, ty + th - 40, tw - 56, 8, fill=P.line, rx=4)
    d.add(f'<rect x="{tx+28}" y="{ty+th-40}" width="0" height="8" rx="4" fill="{P.blue}">'
          f'<animate attributeName="width" from="0" to="{tw-56}" begin="0.4s" dur="9s" fill="freeze"/></rect>')
    c.mono("BOOT", tx + 28, ty + th - 52, 9.5, P.dim, tracking=0.2)
    c.mono("v0404", tx + tw - 28, ty + th - 52, 9.5, P.dim, anchor="end", tracking=0.2)

    # ASCII core
    ax, ay, aw, ah = 1150, 156, 578, 470
    c.panel(ax, ay, aw, ah, "RENDER · ASCII CORE")
    _ascii_animation(c, ax + 40, ay + 60, aw - 80, ah - 120, P.blue)
    c.mono(_pick_frames()[1], ax + aw / 2, ay + ah - 20, 9.5, P.dim, anchor="middle", tracking=0.2)

    c.logo(72, 652, 48)
    c.display(profile["name"], 136, 690, 30, P.text)
    c.mono(profile["role"], 372, 690, 12.5, P.muted, tracking=0.18)
    c.mono(f"{profile['brief']['location']}   ·   {profile['site']}", 1728, 690, 12, P.muted, anchor="end", tracking=0.14)
    return c


# ======================================================== 02 · AUTHENTICATION
def auth(f: Fonts, data: dict) -> Card:
    profile, brief = data["profile"], data["profile"]["brief"]
    c = Card(f, 560, "Identity authentication", "A clearance badge being scanned: handle, role, clearance level and location, "
             "with verification checks completing in sequence.",
             code="SEQ · 02", heading="IDENTITY AUTHENTICATION", status=("VERIFIED", P.ok), accent=P.ok)
    d = c.doc
    # badge
    bx, by, bw, bh = 72, 156, 720, 340
    c.panel(bx, by, bw, bh)
    d.rect(bx, by, 10, bh, fill=P.ok, rx=5)
    # avatar hex with initial
    c.logo(bx + 40, by + 60, 140, shape="hex")
    d.path(c.hexagon(bx + 110, by + 130, 70), fill="none", stroke=P.ok, width=2)
    c.mono("CLEARANCE", bx + 220, by + 62, 10.5, P.dim, tracking=0.24)
    c.display(profile["name"], bx + 220, by + 100, 36)
    c.mono(profile["role"], bx + 220, by + 128, 11.5, P.muted, tracking=0.14)
    rows = [("HANDLE", profile["handle"]), ("LEVEL", "PRINCIPAL"), ("LOCATION", brief["location"]), ("ID", "404 // 0404")]
    for i, (k, v) in enumerate(rows):
        y = by + 176 + i * 30
        c.mono(k, bx + 220, y, 9.5, P.dim, tracking=0.22)
        c.mono(v, bx + 330, y, 12, P.text, tracking=0.12, medium=True)
    # scan line
    d.add(f'<rect x="{bx+12}" y="{by}" width="{bw-14}" height="3" fill="{P.ok}" opacity="0.7">'
          f'<animate attributeName="y" values="{by};{by+bh-3};{by}" dur="4s" repeatCount="indefinite"/></rect>')
    d.add(f'<rect x="{bx+12}" y="{by}" width="{bw-14}" height="40" fill="{P.ok}" opacity="0.06">'
          f'<animate attributeName="y" values="{by-40};{by+bh};{by-40}" dur="4s" repeatCount="indefinite"/></rect>')
    # fingerprint arcs
    fx, fy = bx + bw - 110, by + bh - 100
    for i in range(6):
        r = 14 + i * 12
        d.add(f'<path d="M{fmt(fx-r)},{fmt(fy)} A{r},{r} 0 0 1 {fmt(fx+r)},{fmt(fy)}" fill="none" stroke="{P.ok}" stroke-width="2" stroke-opacity="0.25">'
              f'<animate attributeName="stroke-opacity" values="0.25;0.9;0.25" begin="{i*0.25}s" dur="2.4s" repeatCount="indefinite"/></path>')
    # checks
    kx, ky = 840, 156
    c.panel(kx, ky, 888, 340, "VERIFICATION SEQUENCE")
    checks = [("IDENTITY", "GitHub handle matches profile owner"), ("ROLE", "Principal DevSecOps & Systems Architect"),
              ("MISSION", f"{brief['employer']} · {brief['users']} users · Dubai"), ("SYSTEMS", "26 systems on record · 17 operational"),
              ("POSTURE", "Zero trust · every edge is a checkpoint"), ("ACCESS", "Granted · continue to briefing")]
    for i, (k, v) in enumerate(checks):
        y = ky + 76 + i * 42
        d.circle(kx + 30, y - 5, 9, fill="none", stroke=P.line, width=1.5)
        d.add(f'<circle cx="{kx+30}" cy="{y-5}" r="9" fill="{P.ok}" opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{0.08+i*0.13:.2f};{0.14+i*0.13:.2f};1" dur="9s" repeatCount="indefinite"/></circle>')
        d.add(f'<path d="M{kx+25},{y-5} l4,4 l7,-8" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{0.1+i*0.13:.2f};{0.15+i*0.13:.2f};1" dur="9s" repeatCount="indefinite"/></path>')
        c.mono(k, kx + 56, y, 11, P.text, tracking=0.2, medium=True)
        c.body(v, kx + 220, y, 14, P.muted)
    c.footer("AUTHENTICATION COMPLETE  ·  PROCEED TO MISSION BRIEFING", "NO CREDENTIALS ARE TRANSMITTED — THIS IS A PROFILE")
    return c


# =========================================================== 03 · MISSION
def mission(f: Fonts, data: dict) -> Card:
    profile, brief = data["profile"], data["profile"]["brief"]
    c = Card(f, 600, "Mission briefing", "Current mission at AHS Properties in Dubai — zero-trust network architectures "
             "and automated compliance pipelines for more than 300 enterprise users.",
             code="SEQ · 03", heading="MISSION BRIEFING", status=("ACTIVE", P.purple), accent=P.purple)
    d = c.doc
    c.mono("CURRENT MISSION", 72, 172, 10.5, P.purple, tracking=0.24)
    yy = 214
    for ln in c.wrap(f.display, brief["mission"], 30, 1060):
        c.display(ln, 72, yy, 30, P.text)
        yy += 40
    objs = [("ZERO-TRUST NETWORK", "Every segment a checkpoint; identity before access.", P.purple),
            ("AUTOMATED COMPLIANCE", "Baseline pipelines that enforce and prove policy.", P.blue),
            (f"{brief['users']} USERS", "Enterprise users supported across Dubai.", P.ok)]
    for i, (t, sub, col) in enumerate(objs):
        x = 72 + i * 360
        y = 360
        c.panel(x, y, 340, 130)
        d.rect(x, y, 340, 5, fill=col, rx=2)
        c.display(t, x + 22, y + 56, 22, col)
        for j, ln in enumerate(c.wrap(f.body, sub, 13.5, 296)[:2]):
            c.body(ln, x + 22, y + 84 + j * 19, 13.5, P.muted)
    # identity block right
    c.panel(1200, 156, 528, 334, "IDENTITY MATRIX")
    c.display("404", 1224, 262, 78, P.purple)
    c.mono("//", 1394, 262, 44, P.dim, tracking=0)
    c.display("0404", 1458, 262, 78, P.text)
    for i, ln in enumerate(["HTTP 404: RESOURCE NOT FOUND.", "04.04: THE DAY THE RESOURCE WAS BORN.", "THE ONLY THING NOT FOUND HERE IS A LICENCE FEE."]):
        c.mono(ln, 1224, 318 + i * 24, 11, P.muted if i < 2 else P.purple, tracking=0.14)
    d.line(1224, 400, 1704, 400, stroke=P.line, width=1)
    c.mono(f"{brief['employer']}   ·   {brief['location']}", 1224, 434, 11.5, P.text, tracking=0.16, medium=True)
    for i, ln in enumerate(c.wrap(f.mono, profile["statement"].upper(), 9.5, 460, 0.08)[:2]):
        c.mono(ln, 1224, 460 + i * 16, 9.5, P.dim, tracking=0.08)
    c.footer("BRIEFING ACKNOWLEDGED  ·  NEXT: CURRENT OPERATIONS", "ROLE  PRINCIPAL DEVSECOPS & SYSTEMS ARCHITECT")
    return c


# ========================================================= 04 · OPERATIONS
def operations(f: Fonts, data: dict) -> Card:
    systems, brief = data["systems"], data["profile"]["brief"]
    active = [s for s in systems["systems"] if s["status"] != "BUILT"]
    c = Card(f, 800, "Current operations", "Systems in development or test with progress indicators, plus collaboration "
             "interests, learning track and expertise.",
             code="SEQ · 04", heading="CURRENT OPERATIONS", status=(f"{len(active)} ACTIVE WORKSTREAMS", P.warn), accent=P.warn)
    d = c.doc
    c.panel(72, 156, 1000, 560, "WORKSTREAMS · IN DEVELOPMENT / IN TEST")
    for i, s in enumerate(active):
        y = 208 + i * 48
        col = P.warn if s["status"] == "IN DEV" else P.blue
        c.mono(s["no"], 96, y, 10, P.dim, tracking=0.16)
        c.mono(s.get("short", s["name"]).upper(), 150, y, 11.5, P.text, tracking=0.1, medium=True)
        c.mono(s["status"], 470, y, 9.5, col, tracking=0.2)
        frac = 0.35 + (i * 0.11) % 0.5
        d.rect(560, y - 9, 460, 8, fill=P.line, rx=4)
        d.add(f'<rect x="560" y="{y-9}" width="{460*frac:.0f}" height="8" rx="4" fill="{col}">'
              f'<animate attributeName="width" values="{460*frac*0.9:.0f};{460*frac:.0f};{460*frac*0.9:.0f}" dur="{3+i*0.4:.1f}s" repeatCount="indefinite"/></rect>')
        c.mono(s["verb"], 1040, y, 9.5, P.muted, anchor="end", tracking=0.18)
    c.mono("BARS SHOW ACTIVITY, NOT COMPLETION — STATUS IS THE RECORD.", 96, 696, 9.5, P.dim, tracking=0.12)
    # right column
    blocks = [("OPEN TO COLLABORATE", brief["collaboration"], P.ok), ("LEARNING TRACK", brief["learning"], P.blue), ("ASK ME ABOUT", brief["expertise"], P.purple)]
    y = 156
    for title, items, col in blocks:
        h = 44 + 24 * len(items)
        c.panel(1120, y, 608, h - 8, title)
        for j, it in enumerate(items):
            d.rect(1142, y + 46 + j * 24, 6, 6, fill=col, rx=1)
            c.body(it, 1160, y + 52 + j * 24, 13.5, P.text)
        y += h + 4
    return c


# ============================================================ 05 · THREATS
def threats(f: Fonts, data: dict) -> Card:
    brief = data["profile"]["brief"]
    c = Card(f, 620, "Threat intelligence feed", "Detection classes on watch with severity mapping and the responding control; "
             "a scanner sweeps the table.", code="SEQ · 05", heading="THREAT INTELLIGENCE FEED", status=("WATCHING", P.red), accent=P.red)
    d = c.doc
    tx, ty, tw = 72, 156, 1160
    c.panel(tx, ty, tw, 420, "DETECTION CLASSES ON WATCH  ·  SEVERITY MAPPING")
    cols = [("SEV", 24), ("CLASS", 190), ("RESPONDING CONTROL", 720), ("STATE", 1020)]
    for k, x in cols:
        c.mono(k, tx + x, ty + 66, 9.5, P.dim, tracking=0.22)
    d.line(tx + 18, ty + 76, tx + tw - 18, ty + 76, stroke=P.line, width=1)
    rows = brief["threat_classes"]
    for i, (sev, hue, cls, ctrl) in enumerate(rows):
        y = ty + 108 + i * 44
        col = _hue(hue)
        d.rect(tx + 24, y - 16, 80, 22, fill=col, rx=11, fill_opacity=0.14)
        c.mono(sev, tx + 64, y - 1, 9.5, col, anchor="middle", tracking=0.18, medium=True)
        c.mono(cls, tx + 190, y - 1, 11.5, P.text, tracking=0.08)
        c.mono(ctrl, tx + 720, y - 1, 10.5, P.muted, tracking=0.1)
        c.led(tx + 1030, y - 6, P.ok, r=3.5, dur=2 + i * 0.3)
        c.mono("ARMED", tx + 1046, y - 1, 9.5, P.ok, tracking=0.2)
        d.line(tx + 18, y + 14, tx + tw - 18, y + 14, stroke=P.line, width=1, stroke_opacity=0.6)
    # scanner
    d.add(f'<rect x="{tx+18}" y="{ty+84}" width="{tw-36}" height="30" fill="{P.red}" opacity="0.07">'
          f'<animate attributeName="y" values="{ty+84};{ty+84+44*(len(rows)-1)};{ty+84}" dur="6s" repeatCount="indefinite" calcMode="discrete" '
          f'keyTimes="0;0.5;1"/></rect>')
    d.add(f'<rect x="{tx+18}" y="{ty+84}" width="{tw-36}" height="2" fill="{P.red}" opacity="0.6">'
          f'<animate attributeName="y" values="{ty+84};{ty+84+44*len(rows)};{ty+84}" dur="6s" repeatCount="indefinite"/></rect>')
    # radar
    rx, ry, rr = 1500, 350, 150
    for k in (1, 0.66, 0.33):
        d.circle(rx, ry, rr * k, fill="none", stroke=P.red, width=1, stroke_opacity=0.3)
    d.line(rx - rr, ry, rx + rr, ry, stroke=P.red, width=1, stroke_opacity=0.2)
    d.line(rx, ry - rr, rx, ry + rr, stroke=P.red, width=1, stroke_opacity=0.2)
    d.def_(f'<linearGradient id="rsweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{P.red}" stop-opacity="0"/><stop offset="1" stop-color="{P.red}" stop-opacity="0.6"/></linearGradient>')
    d.add(f'<g><path d="M{rx},{ry} L{rx+rr},{ry} A{rr},{rr} 0 0 0 {fmt(rx+rr*math.cos(-0.6))},{fmt(ry+rr*math.sin(-0.6))} Z" fill="url(#rsweep)" opacity="0.5"/>'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {rx} {ry}" to="360 {rx} {ry}" dur="5s" repeatCount="indefinite"/></g>')
    for (ang, rad, col, dl) in ((0.7, 0.8, P.red, 0), (2.4, 0.5, P.warn, 1.6), (4.2, 0.9, P.gold, 3.1)):
        px, py = rx + rr * rad * math.cos(ang), ry + rr * rad * math.sin(ang)
        d.add(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="4" fill="{col}"><animate attributeName="opacity" values="1;0.2;1" begin="{dl}s" dur="5s" repeatCount="indefinite"/></circle>')
    c.mono("SOC · 22 ENGINES  ·  IAS · 8 LAYERS", rx, ry + rr + 34, 10, P.muted, anchor="middle", tracking=0.18)
    c.footer("CLASSES ARE WHAT THE STACK WATCHES FOR — NOT A LIVE INCIDENT LOG.", "SEVERITY  CRITICAL · HIGH · MEDIUM · LOW · INFO")
    return c


# ========================================================== 09 · ECOSYSTEM
def ecosystem(f: Fonts, data: dict) -> Card:
    brief = data["profile"]["brief"]
    eco = brief["ecosystem"]
    c = Card(f, 640, "Technology ecosystem", "Nine connected layers from identity to AI, each a coloured node with the "
             "tools beneath it; packets travel the chain.", code="SEQ · 10", heading="CLOUD & TECHNOLOGY ECOSYSTEM",
             status=(f"{len(eco)} LAYERS CONNECTED", P.cyan), accent=P.cyan)
    d = c.doc
    n = len(eco)
    gap = (1728 - 72) / n
    y0 = 300
    pts = []
    for i, (name, hue, tools) in enumerate(eco):
        x = 72 + gap * (i + 0.5)
        col = _hue(hue)
        pts.append((x, y0, col))
        if i:
            px, _, pcol = pts[i - 1]
            d.line(px + 40, y0, x - 40, y0, stroke=P.line, width=2)
            c.packet(px + 40, y0, x - 40, y0, 1.6, color=col, begin=i * 0.2, r=3.5)
        d.circle(x, y0, 40, fill="#FFFFFF", stroke=col, width=2.5, filter="url(#shadow)")
        d.circle(x, y0, 40, fill=col, fill_opacity=0.08)
        d.add(f'<circle cx="{fmt(x)}" cy="{y0}" r="40" fill="none" stroke="{col}" stroke-width="2" opacity="0.6">'
              f'<animate attributeName="r" values="40;58" begin="{i*0.3}s" dur="2.8s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0.6;0" begin="{i*0.3}s" dur="2.8s" repeatCount="indefinite"/></circle>')
        c.mono(f"{i+1:02d}", x, y0 + 5, 16, col, anchor="middle", tracking=0.1, medium=True)
        c.mono(name, x, y0 - 62, 11.5, P.text, anchor="middle", tracking=0.2, medium=True)
        for j, t in enumerate(tools):
            d.rect(x - 78, y0 + 70 + j * 30, 156, 24, fill="#FFFFFF", stroke=P.line, width=1, rx=12)
            d.rect(x - 78, y0 + 70 + j * 30, 4, 24, fill=col, rx=2)
            c.mono(t.upper(), x + 2, y0 + 86 + j * 30, 9, P.text, anchor="middle", tracking=0.08)
    c.mono("IDENTITY FIRST. EVERYTHING DOWNSTREAM INHERITS THE CHECKPOINT.", 72, 210, 11, P.muted, tracking=0.14)
    c.footer("RELATIONSHIPS, NOT LOGOS  ·  READ LEFT TO RIGHT", "ZERO TRUST FLOWS THROUGH EVERY LAYER")
    return c


# ============================================================== 10 · VAULT
def vault(f: Fonts, data: dict) -> Card:
    brief = data["profile"]["brief"]
    c = Card(f, 680, "Certification vault", "More than one hundred professional certifications and credentials, organised "
             "by vendor and by category.", code="SEQ · 10", heading="CERTIFICATION VAULT",
             status=(f"{brief['cert_count']} CREDENTIALS", P.gold), accent=P.gold)
    d = c.doc
    c.display(brief["cert_count"], 72, 268, 120, P.gold)
    c.mono("PROFESSIONAL CERTIFICATIONS", 72, 300, 12.5, P.text, tracking=0.24, medium=True)
    c.mono("& CREDENTIALS · EARNED WHILE WORKING FULL-TIME", 72, 322, 10.5, P.muted, tracking=0.16)
    for i, ln in enumerate(c.wrap(f.body, brief["journey"], 13.5, 420)):
        c.body(ln, 72, 366 + i * 20, 13.5, P.muted)
    # vendor drawers
    vx, vy = 540, 156
    c.panel(vx, vy, 1188, 300, "VAULT · BY VENDOR")
    vendors = brief["vendors"]
    cols = 4
    cw, ch = (1188 - 60) / cols, 60
    for i, v in enumerate(vendors):
        x = vx + 30 + (i % cols) * cw
        y = vy + 56 + (i // cols) * (ch + 14)
        d.rect(x, y, cw - 14, ch, fill="#FFFFFF", stroke=P.line, width=1, rx=8, filter="url(#shadow)")
        d.rect(x, y, 5, ch, fill=P.gold, rx=2)
        # lock glyph
        lx, ly = x + 26, y + 30
        d.rect(lx - 8, ly - 2, 16, 12, fill="none", stroke=P.gold, width=1.6, rx=2)
        d.add(f'<path d="M{lx-5},{ly-2} v-5 a5,5 0 0 1 10,0 v5" fill="none" stroke="{P.gold}" stroke-width="1.6">'
              f'<animateTransform attributeName="transform" type="rotate" values="0 {lx+5} {ly-7};-40 {lx+5} {ly-7};0 {lx+5} {ly-7}" begin="{i*0.4}s" dur="4.4s" repeatCount="indefinite"/></path>')
        c.mono(v, x + 50, y + 34, 12.5, P.text, tracking=0.16, medium=True)
        c.led(x + cw - 32, y + 30, P.gold, r=3, dur=2 + i * 0.3)
    # categories
    c.panel(vx, 476, 1188, 130, "CATEGORIES")
    x, yy = vx + 30, 516
    for cat in brief["cert_categories"]:
        w = f.mono.width(cat.upper(), 10.5, 0.12) + 28
        if x + w > vx + 1188 - 30:
            x, yy = vx + 30, yy + 38
        d.rect(x, yy, w, 30, fill=P.gold, fill_opacity=0.1, stroke=P.gold, width=1, rx=15)
        c.mono(cat.upper(), x + 14, yy + 20, 10.5, P.text, tracking=0.12)
        x += w + 10
    c.footer("COUNTS PER VENDOR ARE NOT SHOWN  ·  INDIVIDUAL CREDENTIALS AVAILABLE ON REQUEST", "AWS · AZURE · ORACLE · CISCO · RED HAT · FORTINET · IBM · GOOGLE · ISC2")
    return c


# ====================================================== 11 · TIMELINE + LAB
def timeline(f: Fonts, data: dict) -> Card:
    systems, brief = data["systems"], data["profile"]["brief"]
    c = Card(f, 690, "Mission timeline and innovation lab", "Career stages on a travelling timeline, and the spatial and AI "
             "experiments in the lab.", code="SEQ · 11", heading="MISSION TIMELINE  ·  INNOVATION LAB",
             status=("IN MOTION", P.teal), accent=P.teal)
    d = c.doc
    stages = brief["timeline"]
    x0, x1, y = 120, 1680, 250
    d.line(x0, y, x1, y, stroke=P.line, width=3)
    d.add(f'<line x1="{x0}" y1="{y}" x2="{x0}" y2="{y}" stroke="{P.teal}" stroke-width="3"><animate attributeName="x2" from="{x0}" to="{x1}" dur="8s" repeatCount="indefinite"/></line>')
    d.add(f'<circle cx="{x0}" cy="{y}" r="7" fill="{P.teal}"><animate attributeName="cx" from="{x0}" to="{x1}" dur="8s" repeatCount="indefinite"/></circle>')
    n = len(stages)
    for i, (t, sub) in enumerate(stages):
        x = x0 + (x1 - x0) * i / (n - 1)
        d.circle(x, y, 11, fill="#FFFFFF", stroke=P.teal, width=2.5)
        c.mono(f"{i+1:02d}", x, y + 4, 9, P.teal, anchor="middle", tracking=0.1, medium=True)
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        lines = c.wrap(f.body, sub, 12.5, 300)[:3]
        if i % 2 == 0:
            c.mono(t, x, y + 42, 11, P.text, anchor=anchor, tracking=0.16, medium=True)
            for j, ln in enumerate(lines):
                c.body(ln, x, y + 64 + j * 17, 12.5, P.muted, anchor=anchor)
        else:
            top = y - 40 - 17 * len(lines)
            c.mono(t, x, top, 11, P.text, anchor=anchor, tracking=0.16, medium=True)
            for j, ln in enumerate(lines):
                c.body(ln, x, top + 22 + j * 17, 12.5, P.muted, anchor=anchor)
    # lab
    lab = [s for s in systems["systems"] if s["zone"] == "05"]
    ly = 392
    c.mono("INNOVATION LAB  ·  SPATIAL / AI EXPERIMENTS", 72, ly, 10.5, P.magenta, tracking=0.24)
    cw = (1728 - 72 - 5 * 16) / 6
    for i, s in enumerate(lab[:6]):
        x = 72 + i * (cw + 16)
        yy = ly + 24
        col = P.ok if s["status"] == "BUILT" else P.magenta
        d.rect(x, yy, cw, 180, fill="#FFFFFF", stroke=P.line, width=1, rx=10, filter="url(#shadow)")
        d.rect(x, yy, cw, 5, fill=col, rx=2)
        c.mono(s["no"], x + 16, yy + 34, 9.5, P.dim, tracking=0.2)
        c.led(x + cw - 20, yy + 28, col, r=3, dur=2 + i * 0.3)
        for j, ln in enumerate(c.wrap(f.mono_m, s.get("short", s["name"]).upper(), 11, cw - 32, 0.1)[:2]):
            c.mono(ln, x + 16, yy + 62 + j * 16, 11, P.text, tracking=0.1, medium=True)
        c.mono(s["verb"], x + 16, yy + 104, 10, col, tracking=0.22)
        for j, ln in enumerate(c.wrap(f.body, s["output"], 11.5, cw - 32)[:3]):
            c.body(ln, x + 16, yy + 126 + j * 16, 11.5, P.muted)
    c.footer("THE LAB IS WHERE THE NEXT OPERATIONAL SYSTEM COMES FROM.", "STATUS  GREEN OPERATIONAL · MAGENTA IN DEVELOPMENT")
    return c


# ============================================================== 13 · COMMS
def comms(f: Fonts, data: dict) -> Card:
    profile, brief = data["profile"], data["profile"]["brief"]
    c = Card(f, 420, "Communication terminal", "Contact terminal: website and GitHub, with a blinking prompt.",
             code="SEQ · 13", heading="COMMUNICATION TERMINAL", status=("CHANNEL OPEN", P.ok), accent=P.text)
    d = c.doc
    tx, ty, tw, th = 72, 150, 1656, 190
    c.panel(tx, ty, tw, th)
    d.rect(tx, ty, tw, 34, fill="#EEF2F7", rx=10)
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        d.circle(tx + 22 + i * 20, ty + 17, 6, fill=col)
    lines = [f"contact --web      {profile['site']}", f"contact --github   github.com/{profile['handle']}",
             f"status             OPEN TO COLLABORATE · {brief['location']}"]
    _typewriter(c, lines, tx + 28, ty + 70, 14, P.text, start=0.3, prompt="$ ")
    c.footer("END OF SEQUENCE  ·  THANK YOU FOR VISITING THE CONTROL PLANE", f"{profile['name']} · {profile['role']}")
    return c


# -- reused dark cards, re-tinted ------------------------------------------------
def _tinted(fn, accent_name: str):
    def make(f: Fonts, data: dict) -> Card:
        old = P.accent
        P.accent = getattr(P, accent_name)
        try:
            return fn(f, data)
        finally:
            P.accent = old
    return make




# ================================================== 07 · ENTERPRISE NETWORK
def network(f: Fonts, data: dict) -> Card:
    brief = data["profile"]["brief"]
    c = Card(f, 820, "Enterprise network — site-to-site architecture",
             "Two sites joined by an encrypted site-to-site tunnel, each with an edge firewall, core switch and "
             "segmented VLANs behind zero-trust checkpoints; hybrid cloud above; SOC telemetry from both sites.",
             code="SEQ · 07", heading="ENTERPRISE NETWORK — SITE-TO-SITE ARCHITECTURE",
             status=("TUNNEL UP · ENCRYPTED", P.ok), accent=P.teal)
    d = c.doc
    T, I = P.teal, P.blue

    def box(x, y, w, h, title, sub="", col=T, led=True, r=8):
        d.rect(x, y, w, h, fill="#FFFFFF", stroke=col, width=1.6, rx=r, filter="url(#shadow)")
        d.rect(x, y, 5, h, fill=col, rx=2)
        c.mono(title, x + 18, y + 24, 11, P.text, tracking=0.16, medium=True)
        if sub:
            c.mono(sub, x + 18, y + 42, 9.5, P.muted, tracking=0.08)
        if led:
            c.led(x + w - 16, y + 16, P.ok, r=3)

    def link(x1, y1, x2, y2, col=P.line, w=1.5, dash=None, pk=True, dur=2.0, begin=0.0):
        d.line(x1, y1, x2, y2, stroke=col, width=w, stroke_dasharray=dash)
        if pk:
            c.packet(x1, y1, x2, y2, dur, color=T, r=3, begin=begin)

    # ---- cloud band
    cx0, cy0, cw, ch = 560, 150, 680, 64
    d.rect(cx0, cy0, cw, ch, fill="#FFFFFF", stroke=I, width=1.6, rx=32, filter="url(#shadow)")
    c.mono("HYBRID CLOUD", cx0 + 28, cy0 + 28, 11, I, tracking=0.22, medium=True)
    c.mono("AWS  ·  AZURE  ·  ORACLE CLOUD  ·  GOOGLE CLOUD  —  IDENTITY-FEDERATED, PRIVATE ENDPOINTS", cx0 + 28, cy0 + 47, 9.5, P.muted, tracking=0.08)
    c.led(cx0 + cw - 30, cy0 + 32, P.ok, r=4)

    # ---- sites
    sites = [
        (72, "SITE A", f"DUBAI HQ  ·  {brief['users']} USERS", True),
        (980, "SITE B", "REMOTE SITE  ·  BRANCH / DR", False),
    ]
    for sx, name, sub, hq in sites:
        sw = 748
        d.rect(sx, 250, sw, 470, fill=P.panel2, stroke=P.line, width=1, rx=14, fill_opacity=0.6)
        c.mono(name, sx + 22, 282, 13, P.text, tracking=0.24, medium=True)
        c.mono(sub, sx + 22, 302, 10, P.muted, tracking=0.12)
        # edge firewall
        fx, fy = sx + 40, 330
        box(fx, fy, 250, 58, "NGFW  ·  EDGE FIREWALL", "FORTINET · IPS · WEB FILTER · SSL INSPECTION", col=P.red)
        # core switch
        kx, ky = sx + 40, 420
        box(kx, ky, 250, 58, "CORE SWITCH  ·  L3", "VLAN ROUTING · ACL · 802.1X", col=T)
        link(fx + 125, fy + 58, kx + 125, ky, dur=1.4)
        # identity / DC
        ix_, iy_ = sx + 330, 330
        if hq:
            box(ix_, iy_, 380, 58, "IDENTITY  ·  ACTIVE DIRECTORY / ENTRA ID", "GPO · MFA · CONDITIONAL ACCESS · PRIVILEGED ACCESS", col=I)
            box(ix_, 420, 380, 58, "DATA CENTRE  ·  SERVERS", "FILE · APPS · VIRTUALISATION · BACKUP", col=T)
            box(ix_, 510, 380, 58, "SOC  ·  22 ENGINES", "WAZUH · VELOCIRAPTOR · SYSMON · TACTICAL RMM", col=P.purple)
            link(kx + 250, ky + 29, ix_, ky + 29, dur=1.8)
            link(ix_ + 190, iy_ + 58, ix_ + 190, 420, pk=False)
            link(ix_ + 190, 478, ix_ + 190, 510, pk=False)
        else:
            box(ix_, iy_, 380, 58, "IDENTITY  ·  READ-ONLY DOMAIN CONTROLLER", "CACHED CREDENTIALS · LOCAL AUTH · SYNCED POLICY", col=I)
            box(ix_, 420, 380, 58, "DR REPLICA  ·  SERVERS", "REPLICATED DATA · FAILOVER · BACKUP", col=T)
            box(ix_, 510, 380, 58, "SOC AGENTS  ·  TELEMETRY FORWARDING", "ENDPOINT AGENTS → SITE A SOC OVER THE TUNNEL", col=P.purple)
            link(kx + 250, ky + 29, ix_, ky + 29, dur=1.8)
            link(ix_ + 190, iy_ + 58, ix_ + 190, 420, pk=False)
            link(ix_ + 190, 478, ix_ + 190, 510, pk=False)
        # segments
        segs = [("USERS", P.ok), ("SERVERS", T), ("OT / IOT", P.warn), ("GUEST", P.dim)] if hq else [("USERS", P.ok), ("SERVERS", T), ("GUEST", P.dim)]
        segw = 250 / len(segs) - 8
        for i, (nm, col) in enumerate(segs):
            gx = sx + 40 + i * (segw + 8)
            gy = 600
            d.rect(gx, gy, segw, 88, fill="#FFFFFF", stroke=col, width=1.4, rx=8)
            c.mono(nm, gx + segw / 2, gy + 30, 9.5, P.text, anchor="middle", tracking=0.14, medium=True)
            c.mono("VLAN", gx + segw / 2, gy + 48, 9, P.dim, anchor="middle", tracking=0.2)
            # checkpoint at the segment boundary
            d.circle(gx + segw / 2, gy, 6, fill="#FFFFFF", stroke=col, width=1.6)
            d.line(gx + segw / 2, ky + 58, gx + segw / 2, gy - 6, stroke=P.line, width=1.2)
            c.packet(gx + segw / 2, ky + 58, gx + segw / 2, gy - 6, 1.6 + i * 0.3, color=col, r=2.4, begin=i * 0.4)
            c.led(gx + segw / 2, gy + 70, col, r=2.5, dur=2 + i * 0.4)
        c.mono("EVERY SEGMENT BOUNDARY IS A CHECKPOINT  ·  EAST-WEST INSPECTED", sx + 40, 708, 9.5, P.muted, tracking=0.1)
        # cloud link from firewall
        d.line(fx + 125, fy, fx + 125, cy0 + ch, stroke=I, width=1.2, stroke_dasharray="6 5", stroke_opacity=0.6) if not hq else None
        d.line(fx + 125, fy, fx + 125, cy0 + ch, stroke=I, width=1.2, stroke_dasharray="6 5", stroke_opacity=0.6) if hq else None
        c.packet(fx + 125, cy0 + ch, fx + 125, fy, 2.6, color=I, r=2.6, begin=0.8 if hq else 1.9)

    # ---- tunnel between the two edge firewalls
    ax, ay = 72 + 40 + 250, 359          # site A firewall right edge
    bx = 980 + 40                         # site B firewall left edge
    d.line(ax, ay - 6, bx, ay - 6, stroke=T, width=2)
    d.line(ax, ay + 6, bx, ay + 6, stroke=T, width=2)
    d.rect(ax, ay - 6, bx - ax, 12, fill=T, fill_opacity=0.08)
    c.packet(ax, ay - 6, bx, ay - 6, 1.8, color=T, r=3.2)
    c.packet(bx, ay + 6, ax, ay + 6, 1.8, color=T, r=3.2, begin=0.9)
    mx = (ax + bx) / 2
    d.rect(mx - 118, ay - 34, 236, 26, fill="#FFFFFF", stroke=T, width=1.2, rx=13)
    # lock glyph
    d.rect(mx - 104, ay - 25, 10, 8, fill="none", stroke=T, width=1.4, rx=1.5)
    d.path(f"M{mx-102},{ay-25} v-3 a3,3 0 0 1 6,0 v3", fill="none", stroke=T, width=1.4)
    c.mono("SITE-TO-SITE VPN  ·  WIREGUARD / IPSEC", mx + 4, ay - 16, 9.5, T, anchor="middle", tracking=0.14, medium=True)
    c.mono("WAN  ·  ENCRYPTED  ·  MUTUAL AUTH  ·  IDENTITY BEFORE ROUTE", mx, ay + 34, 9.5, P.muted, anchor="middle", tracking=0.12)

    c.footer("SEGMENTED · INSPECTED · REPLICATED  —  ONE ARCHITECTURE, TWO CITIES", "ZERO TRUST · HYBRID CLOUD · SOC TELEMETRY FROM BOTH SITES")
    return c


CARDS = {
    "01-boot": boot,
    "02-auth": auth,
    "03-mission": mission,
    "04-operations": operations,
    "05-threats": threats,
    "06-architecture": _tinted(dark_cards.hero, "cyan"),
    "07-network": network,
    "08-automation": _tinted(dark_cards.pipeline, "warn"),
    "09-arsenal": _tinted(dark_cards.security, "red"),
    "10-ecosystem": ecosystem,
    "11-timeline-lab": timeline,
    "12-telemetry": _tinted(dark_cards.telemetry, "blue"),
    "13-comms": comms,
}
