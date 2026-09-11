"""Site geometry shared by the Site Plan (A-100) and every key plan.

The site is drawn as a secured compound: the security perimeter is the
outer wall and the corridor inside it; four rooms sit within the inner wall.
Coordinates here are normalised (0..1) against the plan's bounding box so
the same geometry renders at full size on A-100 and at thumbnail size in
every title block.
"""

# Plan bounding box on A-100 in sheet units.
PX0, PY0, PW, PH = 140, 150, 1080, 830

WALL_T = 16      # outer wall thickness (cut, poché)
CORRIDOR = 64    # security perimeter corridor width
INSET = WALL_T + CORRIDOR

_inner = (INSET, INSET, PW - 2 * INSET, PH - 2 * INSET)          # 80,80,920,670
_ix, _iy, _iw, _ih = _inner
_split_x = _ix + 420                                              # service core | right stack


def _n(r):
    x, y, w, h = r
    return (x / PW, y / PH, w / PW, h / PH)


ROOMS_PX = {
    "01": (_ix, _iy, 420, _ih),                                   # SERVICE CORE (full height, left)
    "03": (_split_x, _iy, _iw - 420, 225),                        # DOCUMENT ROOM
    "04": (_split_x, _iy + 225, _iw - 420, 225),                  # TOOL WORKSHOP
    "05": (_split_x, _iy + 450, _iw - 420, _ih - 450),            # ANNEX
}

LAYOUT = {
    "outer": (0.0, 0.0, 1.0, 1.0),
    "inner": _n(_inner),
    "rooms": {k: _n(v) for k, v in ROOMS_PX.items()},
}


def px(r):
    """Normalised rect -> sheet-unit rect on A-100."""
    x, y, w, h = r
    return (PX0 + x * PW, PY0 + y * PH, w * PW, h * PH)
