"""CONTROL PLANE — the seven cards."""

from __future__ import annotations

import math
import random

from common import C, Card, Fonts, fmt, P


def _by_zone(systems: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for s in systems["systems"]:
        out.setdefault(s["zone"], []).append(s)
    return out


def _sys(systems: dict, key: str) -> dict:
    return next(s for s in systems["systems"] if s["key"] == key)


def _status(s: dict) -> tuple[str, str]:
    if s["status"] == "BUILT":
        return "OPERATIONAL", C.OK
    if s["status"] == "IN TEST":
        return "IN TEST", C.WARN
    return "DEPLOYING", C.WARN


# =============================================================== 1 · HERO
def hero(f: Fonts, data: dict) -> Card:
    systems, profile, tlm = data["systems"], data["profile"], data["telemetry"]
    c = Card(f, 1000, "Absaar IT — control plane",
             "Service topology of Absaar IT's systems: root at the centre, a zero-trust perimeter ring, "
             "and five clusters of numbered services, each with an operational or deploying indicator.")
    d = c.doc
    n_total = len(systems["systems"])
    n_up = sum(1 for s in systems["systems"] if s["status"] == "BUILT")
    n_dep = n_total - n_up

    c.logo(72, 62, 96)
    c.display(profile["name"], 190, 118, 68)
    c.mono(profile["role"], 192, 154, 15, C.MUTED, tracking=0.16)
    c.mono(f"{profile['cluster']}  //  {profile['sector']}", 192, 182, 12.5, C.ACCENT, tracking=0.2)

    px, py, pw, ph = 1330, 78, 398, 46
    d.rect(px, py, pw, ph, stroke=C.OK, width=1.4, fill=C.PANEL, rx=23, fill_opacity=0.9)
    c.led(px + 28, py + 23, C.OK, r=5)
    c.mono("ALL SYSTEMS OPERATIONAL", px + 50, py + 29, 15, C.OK, tracking=0.14, medium=True)
    sync = tlm.get("synced_at", "PENDING FIRST SYNC")
    c.mono(f"LAST SYNC  {sync}", 1728, 154, 12.5, C.MUTED, anchor="end", tracking=0.1)
    c.mono(f"{n_total} SERVICES  ·  {n_up} UP  ·  {n_dep} DEPLOYING", 1728, 182, 12.5, C.MUTED, anchor="end", tracking=0.1)
    d.line(72, 214, 1728, 214, stroke=C.LINE, width=1)

    cx, cy = 900, 560
    rx, ry = 720, 330
    d.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{C.ACCENT}" stroke-width="1.2" stroke-opacity="0.45" stroke-dasharray="6 8"/>')
    d.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+10}" ry="{ry+10}" fill="none" stroke="{C.ACCENT}" stroke-width="0.8" stroke-opacity="0.18"/>')
    for k in range(24):
        a = 2 * math.pi * k / 24
        d.line(cx + rx * math.cos(a), cy + ry * math.sin(a), cx + (rx + 10) * math.cos(a), cy + (ry + 10) * math.sin(a),
               stroke=C.ACCENT, width=1, stroke_opacity=0.5)
    d.add(f'<g><rect x="{cx}" y="{cy-0.8}" width="{rx}" height="1.6" fill="url(#sweep)" opacity="0.5"/>'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="9s" repeatCount="indefinite"/></g>')
    c.mono("ZERO-TRUST PERIMETER  ·  EVERY EDGE IS A CHECKPOINT", cx, cy - ry + 34, 11.5, C.ACCENT, anchor="middle", tracking=0.22, opacity=0.9)

    d.path(c.hexagon(cx, cy, 46), fill=C.PANEL, stroke=C.ACCENT, width=2)
    d.path(c.hexagon(cx, cy, 34), fill="none", stroke=C.ACCENT, width=0.8, stroke_opacity=0.5)
    c.mono("ROOT", cx, cy + 5, 14, C.TEXT, anchor="middle", tracking=0.2, medium=True)
    c.mono("LINUX · KERNEL · IAM", cx, cy + 78, 10.5, C.MUTED, anchor="middle", tracking=0.16)

    clusters = {"01": ("SERVICE CORE", 470, 400), "03": ("DOCUMENT PIPELINE", 1330, 400),
                "04": ("TOOL WORKSHOP", 1330, 720), "05": ("ANNEX · SPATIAL / AI", 470, 720)}
    by = _by_zone(systems)

    def node(x, y, s, dy=4, anchor="middle", dx=0):
        ok = s["status"] == "BUILT"
        col = C.OK if ok else C.WARN
        d.circle(x, y, 9, fill=C.PANEL, stroke=C.ACCENT, width=1.4)
        d.circle(x, y, 3.5, fill=C.ACCENT, fill_opacity=0.9)
        c.led(x + 8, y - 8, col, r=3, dur=3.2 if ok else 1.6)
        c.mono(s.get("short", s["name"]).upper(), x + dx, y + dy, 9.5, C.MUTED, anchor=anchor, tracking=0.06)

    for zid, (label, hx, hy) in clusters.items():
        d.line(cx, cy, hx, hy, stroke=C.ACCENT, width=1.2, stroke_opacity=0.35)
        c.packet(cx, cy, hx, hy, 2.6 + 0.4 * int(zid))
        c.packet(hx, hy, cx, cy, 3.1 + 0.3 * int(zid), color=C.TEXT, r=2.2, begin=1.2)
        d.circle(hx, hy, 15, fill=C.PANEL, stroke=C.ACCENT, width=1.6)
        d.circle(hx, hy, 5, fill=C.ACCENT)
        top, left = hy < cy, hx < cx
        if top:
            c.mono(label, hx, hy - 34, 12, C.TEXT, anchor="middle", tracking=0.2, medium=True)
            c.mono(f"ZONE {zid}", hx, hy - 52, 9.5, C.DIM, anchor="middle", tracking=0.2)
        else:
            ax, an = (hx + 30, "start") if left else (hx - 30, "end")
            c.mono(label, ax, hy + 46, 12, C.TEXT, anchor=an, tracking=0.2, medium=True)
            c.mono(f"ZONE {zid}", ax, hy + 64, 9.5, C.DIM, anchor=an, tracking=0.2)
        members = by.get(zid, [])
        n = len(members)
        r = 104 if n <= 5 else 122
        base = math.pi if left else 0.0
        span = math.radians(130 if n <= 5 else 165)
        for i, s in enumerate(members):
            a = base - span / 2 + span * (i + 0.5) / n
            x, y = hx + r * math.cos(a), hy + r * math.sin(a)
            d.line(hx, hy, x, y, stroke=C.LINE, width=1)
            node(x, y, s, dy=4, anchor="end" if left else "start", dx=-16 if left else 16)

    per = by.get("02", [])
    for i, s in enumerate(per):
        a = math.radians(-90 + (i - (len(per) - 1) / 2) * 50)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        d.circle(x, y, 13, fill=C.BG)
        node(x, y, s, dy=-22)

    d.line(72, 896, 1728, 896, stroke=C.LINE, width=1)
    kpis = [(str(n_total), "SYSTEMS RECORDED"), ("8", "LAYERS — INTRUSION ALERT"), ("22", "ENGINES — SOC PLATFORM"),
            ("~25", "ENDPOINTS PER RUN"), ("0", "LICENCE COST — OWN TOOLS"), ("LOCAL", "PROCESSING BY DEFAULT")]
    cw = (1728 - 72) / len(kpis)
    for i, (big, small) in enumerate(kpis):
        x = 72 + i * cw
        if i:
            d.line(x, 912, x, 984, stroke=C.LINE, width=1)
        c.kpi(x + 22, 958, big, small, color=C.OK if i == 4 else C.TEXT)
    return c


# =========================================================== 2 · OPERATOR
def operator(f: Fonts, data: dict) -> Card:
    profile = data["profile"]
    c = Card(f, 580, "Operator profile", "Current focus, collaboration interests, learning, and the standing rule "
             "that everyday tools stay free.", code="OPR · 01", heading="OPERATOR PROFILE", status=("ON DUTY", C.OK))
    d = c.doc
    # left: fields
    y = 170
    for label, value in profile["operator"]:
        c.mono(label, 72, y, 10.5, C.ACCENT, tracking=0.22)
        lines = c.wrap(f.body, value, 15.5, 880)
        for ln in lines[:3]:
            y += 24
            c.body(ln, 72, y, 15.5, C.TEXT)
        y += 30
        d.line(72, y - 14, 980, y - 14, stroke=C.LINE, width=1)
    # right: rule + identity
    c.panel(1040, 150, 688, 200, "STANDING RULE")
    yy = 200
    for ln in c.wrap(f.body, profile["rule"], 15, 640):
        c.body(ln, 1060, yy, 15, C.TEXT)
        yy += 24
    c.body(profile["statement"], 1060, 330, 12.5, C.MUTED)

    c.panel(1040, 370, 688, 130, "IDENTITY")
    c.display("404", 1060, 462, 58, C.ACCENT)
    c.mono("//", 1188, 462, 36, C.DIM, tracking=0)
    c.display("0404", 1244, 462, 58, C.TEXT)
    c.mono(profile["punchline"], 1060, 490, 11, C.MUTED, tracking=0.16)
    c.footer(f"{profile['site']}   ·   github.com/{profile['handle']}", "STATUS LINE REFRESHES WITH EVERY SYNC")
    return c


# ========================================================== 3 · TELEMETRY
def telemetry(f: Fonts, data: dict) -> Card:
    tlm = data["telemetry"]
    live = bool(tlm.get("weeks"))
    status = ("LIVE · DAILY SYNC", C.OK) if live else ("AWAITING FIRST SYNC", C.WARN)
    c = Card(f, 620, "GitHub telemetry", "Contribution activity over the last 52 weeks, streaks, repositories and "
             "followers, refreshed daily.", code="TLM · 02", heading="TELEMETRY — GITHUB", status=status)
    d = c.doc

    def n(k, default="—"):
        v = tlm.get(k)
        return default if v is None else (f"{v:,}" if isinstance(v, int) else str(v))

    kpis = [(n("contributions_year"), "CONTRIBUTIONS · 52 WEEKS"), (n("current_streak"), "CURRENT STREAK · DAYS"),
            (n("longest_streak"), "LONGEST STREAK · DAYS"), (n("public_repos"), "PUBLIC REPOSITORIES"),
            (n("followers"), "FOLLOWERS"), (n("account_age"), "ON GITHUB")]
    for i, (big, small) in enumerate(kpis):
        x = 72 + (i % 3) * 300
        y = 200 + (i // 3) * 110
        c.kpi(x, y, big, small, size=38)

    # 52-week uptime strip
    sx, sy, sw, sh = 1000, 160, 728, 300
    c.panel(sx, sy, sw, sh, "ACTIVITY — 52 WEEKS  ·  ONE BAR PER WEEK")
    weeks = tlm.get("weeks") or [0] * 52
    mx = max(weeks) or 1
    bw = (sw - 36) / 52
    for i, v in enumerate(weeks):
        x = sx + 18 + i * bw
        h = 6 + (sh - 100) * (v / mx) if live else 6
        col = C.OK if v > 0 else C.LINE
        if live and v >= 0.75 * mx:
            col = C.ACCENT
        d.rect(x + 1, sy + sh - 44 - h, bw - 2.5, h, fill=col, rx=1.5, fill_opacity=0.9 if live else 0.6)
    c.mono("52W AGO", sx + 18, sy + sh - 22, 9.5, C.DIM, tracking=0.16)
    c.mono("THIS WEEK", sx + sw - 18, sy + sh - 22, 9.5, C.DIM, anchor="end", tracking=0.16)
    if not live:
        c.mono("FIRST SYNC WILL POPULATE THIS STRIP", sx + sw / 2, sy + sh / 2 + 4, 12, C.WARN, anchor="middle", tracking=0.2)

    # weekday distribution
    wy = 480
    c.mono("BY WEEKDAY", 72, wy, 10.5, C.DIM, tracking=0.22)
    days = tlm.get("weekday") or [0] * 7
    dm = max(days) or 1
    for i, lab in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        x = 72 + i * 122
        c.bar(x, wy + 18, 100, 8, days[i] / dm if live else 0, color=C.ACCENT)
        c.mono(lab, x, wy + 44, 9.5, C.DIM, tracking=0.16)
    if live and tlm.get("busiest_day"):
        c.mono(f"BUSIEST DAY  {tlm['busiest_day']}", 1000, wy + 44, 10, C.MUTED, tracking=0.16)
    c.footer("SOURCE  GITHUB GRAPHQL API  ·  INCLUDES PRIVATE CONTRIBUTION COUNTS WHERE PERMITTED",
             f"SYNCED  {tlm.get('synced_at', 'PENDING')}")
    return c


# =========================================================== 4 · SECURITY
def security(f: Fonts, data: dict) -> Card:
    systems = data["systems"]
    soc, ias, policy = _sys(systems, "soc"), _sys(systems, "ias"), _sys(systems, "policy")
    c = Card(f, 780, "Security stack", "Intrusion Alert System drawn as eight rings around a server; SOC platform as "
             "a rack of twenty-two engines; zero-trust access chain and policy bundle.",
             code="SEC · 03", heading="SECURITY STACK", status=("ALL LAYERS ARMED", C.OK))
    d = c.doc

    # -- IAS rings
    cx, cy = 372, 450
    c.mono("202  ·  IAS — INTRUSION ALERT SYSTEM", 72, 166, 11.5, C.ACCENT, tracking=0.2)
    c.mono("EIGHT LAYERS AROUND ONE SERVER. EVERY LAYER RAISES AN ALERT.", 72, 188, 10, C.MUTED, tracking=0.08)
    layers = ias["counts"]["layers"]
    for i in range(layers):
        r = 54 + i * 26
        d.circle(cx, cy, r, stroke=C.ACCENT, width=1.1, stroke_opacity=0.22 + 0.06 * (layers - i))
        a = math.radians(-38)
        lx, ly = cx + (r + 4) * math.cos(a), cy + (r + 4) * math.sin(a)
        c.mono(f"L{i+1}", lx + 6, ly + 3, 9, C.DIM, tracking=0.1)
    d.add(f'<circle cx="{cx}" cy="{cy}" r="54" fill="none" stroke="{C.OK}" stroke-width="2" opacity="0.8">'
          f'<animate attributeName="r" values="54;240" dur="4s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0.8;0" dur="4s" repeatCount="indefinite"/></circle>')
    d.path(c.hexagon(cx, cy, 34), fill=C.PANEL, stroke=C.ACCENT, width=1.8)
    c.mono("SRV", cx, cy + 4, 11, C.TEXT, anchor="middle", tracking=0.2, medium=True)
    c.led(cx + 26, cy - 26, C.OK, r=3)
    c.mono("8 LAYERS  ·  ALERT ON EVERY BREACH ATTEMPT  ·  SERVER-SIDE", cx, 712, 10, C.MUTED, anchor="middle", tracking=0.14)

    # -- SOC rack
    rx0, ry0, rw = 700, 156, 420
    c.mono("201  ·  SOC / ENDPOINT SECURITY PLATFORM", rx0, 166, 11.5, C.ACCENT, tracking=0.2)
    c.mono("22 ENGINES · LAYERED · BUILT FROM FIRST PRINCIPLES", rx0, 188, 10, C.MUTED, tracking=0.08)
    engines = soc["counts"]["engines"]
    named = ["WAZUH", "VELOCIRAPTOR", "PROMETHEUS", "GRAFANA", "TACTICAL RMM"]
    slot_h = 22
    top = 210
    d.rect(rx0, top - 8, rw, engines * slot_h + 16, fill=C.PANEL2, stroke=C.LINE, width=1, rx=8)
    rnd = random.Random(404)
    for i in range(engines):
        y = top + i * slot_h
        d.rect(rx0 + 14, y, rw - 28, slot_h - 5, fill=C.PANEL, stroke=C.LINE, width=1, rx=3)
        label = named[i] if i < len(named) else f"ENGINE {i+1:02d}"
        c.mono(label, rx0 + 28, y + 12.5, 9, C.MUTED if i >= len(named) else C.TEXT, tracking=0.12)
        for k in range(6):
            d.rect(rx0 + rw - 120 + k * 12, y + 5, 7, 7, fill=C.LINE, rx=1)
        # activity LED with its own phase
        dur = 0.8 + rnd.random() * 2.2
        d.add(f'<circle cx="{rx0 + rw - 32}" cy="{y + 8.5}" r="3" fill="{C.OK}">'
              f'<animate attributeName="opacity" values="1;0.15;1" dur="{dur:.2f}s" repeatCount="indefinite"/></circle>')
    c.mono("DETECTION  ·  MONITORING  ·  RESPONSE  ·  RMM", rx0 + rw / 2, 712, 10, C.MUTED, anchor="middle", tracking=0.14)

    # -- zero trust chain + policy bundle
    zx = 1180
    c.mono("ACCESS CHAIN  ·  ZERO TRUST", zx, 166, 11.5, C.ACCENT, tracking=0.2)
    c.mono("NO IMPLICIT TRUST. EVERY HOP RE-VERIFIES.", zx, 188, 10, C.MUTED, tracking=0.08)
    chain = ["IDENTITY", "DEVICE", "POLICY", "SESSION", "RESOURCE"]
    for i, step in enumerate(chain):
        y = 236 + i * 60
        d.rect(zx, y - 20, 200, 40, fill=C.PANEL2, stroke=C.LINE, width=1, rx=6)
        c.mono(f"{i+1:02d}", zx + 14, y + 4.5, 10, C.DIM, tracking=0.1)
        c.mono(step, zx + 44, y + 4.5, 11.5, C.TEXT, tracking=0.18, medium=True)
        c.led(zx + 180, y, C.OK, r=3, dur=2 + i * 0.4)
        if i < len(chain) - 1:
            d.line(zx + 100, y + 20, zx + 100, y + 40, stroke=C.ACCENT, width=1.2, stroke_opacity=0.6)
            c.packet(zx + 100, y + 20, zx + 100, y + 40, 1.2, begin=i * 0.3, r=2.4)

    bx = 1420
    c.panel(bx, 216, 308, 300, "102 · POLICY BUNDLE — ONE AGENT")
    items = ["USB CONTROL", "SYSMON", "VELOCIRAPTOR", "MONITORING", "ENDPOINT POLICY", "HEADLESS EXECUTION"]
    for i, it in enumerate(items):
        y = 272 + i * 34
        d.rect(bx + 20, y - 8, 8, 8, fill=C.OK, rx=1)
        c.mono(it, bx + 40, y, 11, C.TEXT, tracking=0.14)
    c.mono("APPLIED IN SECONDS  ·  MANY POLICIES, ONE RUN", bx + 20, 494, 9.5, C.MUTED, tracking=0.1)
    c.footer("SECURITY IS DRAWN IN LAYERS. EVERY BOUNDARY IS A CHECKPOINT.", "OPEN-SOURCE ENGINES · OWN ARCHITECTURE")
    return c


# =========================================================== 5 · PIPELINE
def pipeline(f: Fonts, data: dict) -> Card:
    systems = data["systems"]
    onb = _sys(systems, "onboarding")
    n_ep = onb["counts"]["endpoints_per_run"]
    c = Card(f, 580, "Deploy pipeline — auto-onboarding", "Three input fields feed one packaged process that "
             "configures about twenty-five endpoints in a single run.",
             code="PIP · 04", heading="DEPLOY PIPELINE — CORPORATE AUTO-ONBOARDING", status=(f"1 RUN · ~{n_ep} ENDPOINTS", C.OK))
    d = c.doc

    # inputs
    fields = ["EMPLOYEE ID", "DEPARTMENT", "M365 EMAIL"]
    for i, fld in enumerate(fields):
        y = 190 + i * 56
        d.rect(72, y, 220, 38, fill=C.PANEL2, stroke=C.LINE, width=1, rx=6)
        c.mono(fld, 90, y + 24, 11, C.TEXT, tracking=0.16)
        d.line(292, y + 19, 340, y + 19, stroke=C.ACCENT, width=1, stroke_opacity=0.5)
    d.line(340, 209, 340, 209 + 112, stroke=C.ACCENT, width=1, stroke_opacity=0.5)
    c.mono("3 FIELDS  ·  MINIMAL INPUT", 72, 372, 9.5, C.DIM, tracking=0.16)
    c.mono("OPERATOR ×1", 72, 396, 9.5, C.DIM, tracking=0.16)

    # packaged process
    hx, hy = 470, 265
    d.line(340, hy, hx - 50, hy, stroke=C.ACCENT, width=1.2, stroke_opacity=0.6)
    c.packet(340, hy, hx - 50, hy, 1.8)
    d.path(c.hexagon(hx, hy, 50), fill=C.PANEL, stroke=C.ACCENT, width=2)
    c.mono("101", hx, hy - 8, 11, C.ACCENT, anchor="middle", tracking=0.2)
    c.mono("PACKAGE", hx, hy + 12, 10.5, C.TEXT, anchor="middle", tracking=0.2, medium=True)
    c.mono("ONE RUN", hx, hy + 78, 9.5, C.DIM, anchor="middle", tracking=0.2)

    # bus
    bx = 620
    d.line(hx + 50, hy, bx, hy, stroke=C.ACCENT, width=1.6, stroke_opacity=0.8)
    d.line(bx, 170, bx, 470, stroke=C.ACCENT, width=1.6, stroke_opacity=0.8)
    c.mono("BUS", bx + 8, 486, 9.5, C.DIM, tracking=0.2)

    # endpoints 5 x 5 rolling deploy
    ex0, ey0, dx, dy = 700, 176, 92, 58
    ew, eh = 60, 40
    k = 0
    for r in range(5):
        ry = ey0 + r * dy
        d.line(bx, ry + eh / 2, ex0 + 4 * dx + ew / 2, ry + eh / 2, stroke=C.LINE, width=1)
        for col in range(5):
            x = ex0 + col * dx
            delay = (r * 5 + col) * 0.18
            d.rect(x, ry, ew, eh, fill=C.PANEL2, stroke=C.LINE, width=1, rx=4)
            d.rect(x + 8, ry + 7, ew - 16, eh - 18, fill=C.PANEL, stroke=C.LINE, width=0.8, rx=2)
            d.add(f'<rect x="{x+8}" y="{ry+7}" width="{ew-16}" height="{eh-18}" rx="2" fill="{C.OK}" opacity="0">'
                  f'<animate attributeName="opacity" values="0;0;0.85;0.85;0" keyTimes="0;{delay/7:.3f};{(delay+0.4)/7:.3f};0.86;1" dur="7s" repeatCount="indefinite"/></rect>')
            k += 1
            c.mono(f"{k:02d}", x + ew / 2, ry + eh + 12, 8.5, C.DIM, anchor="middle", tracking=0.1)
    c.mono(f"{n_ep} ENDPOINTS  ·  CONFIGURED PER RUN", ex0, 492, 10, C.MUTED, tracking=0.16)

    # stages
    sx, sy = 1220, 190
    c.panel(sx, sy - 34, 508, 300, "STAGES")
    stages = [("INTAKE", "3 fields collected"), ("PACKAGE", "one bundle, headless"), ("DISTRIBUTE", "bus to every endpoint"),
              ("CONFIGURE", "system, accounts, apps"), ("POLICY", "USB · Sysmon · monitoring"), ("VERIFY", "report to operator")]
    for i, (st, note) in enumerate(stages):
        y = sy + 20 + i * 40
        c.mono(f"{i+1:02d}", sx + 20, y + 4, 10, C.DIM, tracking=0.1)
        c.mono(st, sx + 50, y + 4, 11.5, C.TEXT, tracking=0.18, medium=True)
        c.mono(note.upper(), sx + 190, y + 4, 9.5, C.MUTED, tracking=0.08)
        d.rect(sx + 430, y - 4, 56, 8, fill=C.LINE, rx=4)
        d.add(f'<rect x="{sx+430}" y="{y-4}" width="0" height="8" rx="4" fill="{C.OK}">'
              f'<animate attributeName="width" values="0;0;56;56" keyTimes="0;{i/7:.3f};{(i+0.8)/7:.3f};1" dur="7s" repeatCount="indefinite"/></rect>')
    c.footer("ONE OPERATOR SHALL BE SUFFICIENT TO CONFIGURE MANY SYSTEMS.", "MINIMAL MANUAL INTERACTION")
    return c


# ============================================================== 6 · STACK
def stack(f: Fonts, data: dict) -> Card:
    profile = data["profile"]
    domains = profile["domains"]
    groups = profile["stack"]
    n_tools = sum(len(v) for v in groups.values())

    # pre-compute chip layout to size the card
    chip_h, chip_gap, size = 30, 10, 10.5
    rows: list[tuple[str, list[list[tuple[str, float]]]]] = []
    for g, items in groups.items():
        lines: list[list[tuple[str, float]]] = [[]]
        x = 0.0
        for it in items:
            w = f.mono.width(it.upper(), size, 0.12) + 28
            if x + w > 1380 and lines[-1]:
                lines.append([])
                x = 0.0
            lines[-1].append((it, w))
            x += w + chip_gap
        rows.append((g, lines))
    y_groups = 184 + 3 * 44 + 36
    h_groups = sum(len(lines) * (chip_h + chip_gap) + 24 for _, lines in rows)
    height = y_groups + h_groups + 70
    c = Card(f, height, "Capability matrix", "Eighteen practice domains and the tools behind them, grouped by layer.",
             code="CAP · 05", heading="CAPABILITY MATRIX", status=(f"{len(domains)} DOMAINS · {n_tools} TOOLS", C.ACCENT))
    d = c.doc

    c.mono("PRACTICE DOMAINS", 72, 160, 10.5, C.DIM, tracking=0.22)
    cw = (1728 - 72) / 6
    for i, dom in enumerate(domains):
        x = 72 + (i % 6) * cw
        y = 184 + (i // 6) * 44
        d.rect(x, y, cw - 12, 34, fill=C.PANEL2, stroke=C.LINE, width=1, rx=6)
        c.led(x + 16, y + 17, C.OK if dom != "Continuous Learning" else C.ACCENT, r=2.5, dur=2 + (i % 5) * 0.5)
        c.mono(dom.upper(), x + 32, y + 21.5, 10.5, C.TEXT, tracking=0.12)

    y = y_groups
    d.line(72, y - 22, 1728, y - 22, stroke=C.LINE, width=1)
    for g, lines in rows:
        c.mono(g, 72, y + 20, 10.5, C.ACCENT, tracking=0.22)
        for line in lines:
            x = 340
            for it, w in line:
                d.rect(x, y, w, chip_h, fill=C.PANEL2, stroke=C.LINE, width=1, rx=15)
                c.mono(it.upper(), x + 14, y + 20, size, C.TEXT, tracking=0.12)
                x += w + chip_gap
            y += chip_h + chip_gap
        y += 24
        d.line(72, y - 18, 1728, y - 18, stroke=C.LINE, width=1, stroke_opacity=0.6)
    c.footer("DECLARED STACK  ·  OPEN SOURCE PREFERRED  ·  OWN TOOLS WHERE THE MARKET CHARGES FOR BASICS", f"{n_tools} ENTRIES")
    return c


# =========================================================== 7 · SERVICES
def services(f: Fonts, data: dict) -> Card:
    systems, profile = data["systems"], data["profile"]
    feats = [_sys(systems, k) for k in profile["featured"]]
    c = Card(f, 660, "Featured services", "Four systems with status, input, output and a short note.",
             code="SVC · 06", heading="FEATURED SERVICES", status=(f"{len(feats)} SELECTED", C.ACCENT))
    d = c.doc
    pw, ph = 808, 200
    for i, s in enumerate(feats):
        x = 72 + (i % 2) * (pw + 40)
        y = 156 + (i // 2) * (ph + 30)
        label, col = _status(s)
        d.rect(x, y, pw, ph, fill=C.PANEL2, stroke=C.LINE, width=1, rx=12, fill_opacity=0.8)
        d.rect(x, y, 4, ph, fill=col, rx=2)
        c.mono(s["no"], x + 26, y + 34, 11, C.DIM, tracking=0.2)
        c.led(x + pw - 26, y + 30, col, r=3.5)
        c.mono(label, x + pw - 40, y + 34, 10, col, anchor="end", tracking=0.18, medium=True)
        c.display(s["name"].upper(), x + 26, y + 74, 24)
        c.mono(f"{s['input'].upper()}", x + 26, y + 104, 9.5, C.MUTED, tracking=0.08)
        vw = c.mono(s["verb"], x + 26, y + 126, 11, C.ACCENT, tracking=0.24, medium=True)
        d.line(x + 26 + vw + 12, y + 122, x + 26 + vw + 40, y + 122, stroke=C.ACCENT, width=1)
        d.path(f"M{x+26+vw+40},{y+122} l-6,-3.5 v7 z", fill=C.ACCENT)
        out = c.wrap(f.mono, s["output"].upper(), 9.5, pw - 110 - vw)
        c.mono(out[0], x + 26 + vw + 50, y + 126, 9.5, C.TEXT, tracking=0.08)
        yy = y + 158
        for ln in c.wrap(f.body, s.get("note", ""), 13.5, pw - 52)[:3]:
            c.body(ln, x + 26, yy, 13.5, C.MUTED)
            yy += 20
    c.footer("FULL REGISTER OF 26 SYSTEMS BELOW  ·  STATUS AS RECORDED", "WHERE A REQUIRED TOOL DID NOT EXIST, IT WAS BUILT.")
    return c


CARDS = {
    "hero": hero, "operator": operator, "telemetry": telemetry, "security": security,
    "pipeline": pipeline, "stack": stack, "services": services,
}
