"""Sheet registry. Order here is the order of the set."""

from . import g000, a100, a200, a300, a400, a500, d501

REGISTRY = {
    "G-000": g000.make,
    "A-100": a100.make,
    "A-200": a200.make,
    "A-300": a300.make,
    "A-400": a400.make,
    "A-500": a500.make,
    "D-501": d501.make,
}
