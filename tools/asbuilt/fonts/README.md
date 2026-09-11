# Lettering face

The cards are lettered in **PetrumEX** (Regular, Medium) and **TBJ Terminal
Mono** (Regular, Medium), licensed typefaces. The licences do not permit
redistribution of the font files, so they are not part of this repository.
All lettering in `assets/console/` is already converted to outlines; the
fonts are only needed to regenerate cards.

To rebuild, place these files in this directory:

    PetrumEX-Regular.otf
    PetrumEX-Medium.otf
    TBJTerminalMono-Regular.otf
    TBJTerminalMono-Medium.otf

then run `python3 tools/console/build.py` from the repository root.

For GitHub Actions, store the same four files as a secret:

    tar -czf - -C tools/asbuilt/fonts PetrumEX-Regular.otf PetrumEX-Medium.otf \
        TBJTerminalMono-Regular.otf TBJTerminalMono-Medium.otf | base64 -w0 > fonts.b64
    gh secret set FONT_BUNDLE_B64 < fonts.b64 && rm fonts.b64

If the files are absent the console generator stops with an error rather
than render with a stand-in face.
