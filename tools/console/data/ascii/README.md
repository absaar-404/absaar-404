# ASCII core — make it yours

The boot card renders an ASCII animation here. Three ways to fill it, in
order of priority:

1. **Your own frames** — drop text files named `frame-01.txt`, `frame-02.txt`, …
   in this folder. Each file is one frame of the animation (same width for all).
   Draw them by hand, or export from any ASCII tool.
2. **Any picture** — drop `source.png` (or .jpg/.gif/.webp) here. It is
   converted to ASCII at build time and animated with a band of light
   sweeping across it. Works well with logos and high-contrast portraits.
3. **Nothing** — the procedural rotating torus is used.

Then run `python3 tools/console/build.py --light` and commit.
