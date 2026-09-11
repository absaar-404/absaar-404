<p align="center"><sub>AS-BUILT DRAWING SET &nbsp;·&nbsp; PROJECT NO. {{NUMBER}} &nbsp;·&nbsp; ISSUE {{ISSUE}} &nbsp;·&nbsp; REV {{REV}} &nbsp;·&nbsp; NTS</sub></p>

<a href="assets/sheets/A-100-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 700px)" srcset="assets/sheets/A-100-key-dark.svg">
  <source media="(max-width: 700px)" srcset="assets/sheets/A-100-key-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/A-100-dark.svg">
  <img alt="{{ALT_A100}}" src="assets/sheets/A-100-light.svg" width="100%">
</picture>
</a>

<p align="center"><sub>A-100 &nbsp;·&nbsp; SITE PLAN &nbsp;—&nbsp; every system located by zone. Openings between spaces are access checkpoints. Open the sheet for full size.</sub></p>

I build secure infrastructure, automate operations, simplify complicated enterprise workflows and engineer resilient systems. Many everyday tools are unnecessarily expensive or complicated, so where practical I build my own — simple, lightweight, useful and free. This set records what has been built.

## Sheet index

| Sheet | Title | Contents |
|:--|:--|:--|
{{INDEX}}

## General notes

{{NOTES}}

## A-200 · Fleet Floor

<a href="assets/sheets/A-200-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/A-200-dark.svg">
  <img alt="{{ALT_A200}}" src="assets/sheets/A-200-light.svg" width="100%">
</picture>
</a>

One administrator, three input fields, one packaged process, one run: about twenty-five endpoints configured with minimal manual interaction. The enlarged Service Core shows the systems that keep the fleet running once it exists — policy automation, an on-prem asset register at zero licence cost, and a ticketing system that routes each ticket so the technician already knows what needs attention.

## A-300 · Security Section

<a href="assets/sheets/A-300-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/A-300-dark.svg">
  <img alt="{{ALT_A300}}" src="assets/sheets/A-300-light.svg" width="100%">
</picture>
</a>

Section A-A cuts through the perimeter. The Intrusion Alert System is drawn as it is built: eight layers around one server. Beside it, the SOC and endpoint security platform — twenty-two engines in a layered architecture, built from first principles rather than assembled from a commercial product.

## A-400 · Document Room

<a href="assets/sheets/A-400-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/A-400-dark.svg">
  <img alt="{{ALT_A400}}" src="assets/sheets/A-400-light.svg" width="100%">
</picture>
</a>

Four intake lines. Agency documents become Salesforce-ready spreadsheets; CAD drawings become structured documentation; employee documents are converted and edited on a local server. Nothing leaves the site to be processed.

## A-500 · Annex

<a href="assets/sheets/A-500-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/A-500-dark.svg">
  <img alt="{{ALT_A500}}" src="assets/sheets/A-500-light.svg" width="100%">
</picture>
</a>

The spatial and creative work: scroll-driven camera paths through WebGL scenes, a 3D real-estate walkthrough, camera-based inventory scanning, audio-matched visualisation, a local RAG orchestration interface, and training-loop experiments. Each camera station is one system; the keynotes give its input, its verb and its output.

## D-501 · Capture Detail

<a href="assets/sheets/D-501-light.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/sheets/D-501-dark.svg">
  <img alt="{{ALT_D501}}" src="assets/sheets/D-501-light.svg" width="100%">
</picture>
</a>

HayaScope HyperSync, drawn at the one rule that defines it: the extension's interface sits outside the capture boundary and is never drawn onto the page being captured. Capture, stitch, annotate and export — all processed locally in the browser. Infinite captures. Zero paywalls.

## S-001 · Schedule

{{STATS}}

| No. | System | Zone | Status | Input → Output | Note |
|:--|:--|:--|:--|:--|:--|
{{SCHEDULE}}

## R-001 · Revision log

| Rev | Issue | Description |
|:--|:--|:--|
| A | {{ISSUE}} | First issue. {{COUNT}} systems recorded; {{CLOUDED}} clouded as work in progress. |

## Instruments

Cloud architecture · Enterprise infrastructure · Cybersecurity engineering · Linux administration · Docker & Kubernetes · Infrastructure automation · Identity & access management · Network security · SIEM & XDR · Incident response · Performance optimisation · Disaster recovery · Cloud security · Enterprise monitoring · Container platforms · Zero-trust architecture · Threat detection & response · Continuous learning

---

<p align="center"><sub>DRAWN BY <b>ABSAAR IT</b> &nbsp;·&nbsp; PRINCIPAL DEVSECOPS &amp; SYSTEMS ARCHITECT &nbsp;·&nbsp; <a href="https://absaar.dev">absaar.dev</a></sub><br>
<sub>Sheets are generated from <code>tools/asbuilt</code>. Lettering is outlined; nothing on a sheet depends on a font being installed.</sub><br>
<sub>Where a required tool did not exist, it was built.</sub></p>
