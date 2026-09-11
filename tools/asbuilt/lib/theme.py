"""Palettes and line weights for the AS-BUILT sheet set.

Two variants only. Light is canonical (paper). Dark is vellum on a light
table: a grey sheet with bone ink. There is deliberately no blue anywhere.

Red has exactly one meaning on every sheet: the revision cloud around work
in progress. Nothing else may use it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    name: str
    paper: str
    ink: str
    grey: str       # medium grey: secondary lettering, hidden lines
    light: str      # light grey: poché fill, grid, background rules
    red: str        # revision only


LIGHT = Palette(
    name="light",
    paper="#FFFFFF",
    ink="#141414",
    grey="#7A7A7A",
    light="#D6D6D6",
    red="#C8102E",
)

DARK = Palette(
    name="dark",
    paper="#2A2C2F",
    ink="#E9E6DF",
    grey="#9A9C9F",
    light="#454850",
    red="#E4493F",
)

PALETTES = {"light": LIGHT, "dark": DARK}


# Line weights in sheet units (sheet is 1800 wide; GitHub shows it at ~896,
# so on-screen weights are roughly half these values).
HEAVY = 3.2      # cut trust boundaries, sheet border outer line
MEDIUM = 1.6     # system outlines, symbols
HAIR = 0.7       # dimensions, leaders, grid, hidden lines
