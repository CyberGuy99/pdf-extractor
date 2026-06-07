# Technical Overview of Extraction Strategies
[See readme for context](README.md)

## Automated Strategies

Headless extraction engines process documents continuously in the background by evaluating coordinate systems, drawing operations, and text lines.

### 1. Figure Extraction (`--figures`)
* **Description:** Employs a line-level scanning parser to sequentially locate standard figure caption prefixes (e.g., *Fig. 1*). It establishes an upper column boundary ("ceiling") based on prior text blocks and aggregates all local graphical elements, embedded bitmaps, and vector paths lying within that zone to dynamically draw the final extraction bounds.
* **Developer Customization Parameters (`ieee_extractor.py` / `aip_extractor.py`):**
  * **Crop Padding Control:** Locate the variables `padding_top`, `padding_bottom`, and `padding_x` within the final export logic. Adjusting these values increases or decreases the whitespace buffer captured around the figure's extreme coordinates.
  * **Caption Pattern Modification:** Modify the `caption_pattern = re.compile(r'...')` regular expression to accommodate non-standard caption prefixes, alternative punctuation rules, or localized language strings.
  * **Fallback Dimensions:** In cases where a figure contains no explicit native vector lines or bitmap metadata to calculate geometric limits, the engine applies a fallback bounding box defined by `c_rect.y0 - 250`. Tweak this `250` value to adjust the default vertical height allocation.

### 2. Table Extraction (`--tables`)
* **Description:** Identifies structural table caption markers (e.g., *TABLE I*) on the page. Once identified, the engine runs a downstream geometric scan to isolate underlying structural vector lines, cell grids, mesh drawings, and line dividers belonging to the layout.
* **Developer Customization Parameters (`table_isolator.py`):**
  * **Scanning Depth Window:** The algorithm evaluates drawings within the relative coordinate frame `rect.y1 - 5 <= d_rect.y0 <= rect.y1 + 400`. For exceptionally long tables that span standard page layouts, scale the `400` pixel limit upward.
  * **Deduplication Threshold:** The deduplication engine relies on `abs(rect.y0 - captions[-1].y0) > 150` to avoid double-capturing tables when caption phrases repeat inside structural headers. Adjust this distance threshold if dealing with dense text matrices.
  * **Margin Adjustments:** Modify the local `padding` assignment to control the crispness of the border crops around table headers.

### 3. Mathematical Equation Extraction (`--equations`)
* **Description:** Scans marginal space segments within text paths to capture trailing, right-aligned alphanumeric tags (e.g., `(1)`, `(A2)`). It maps the vertical center line of the corresponding text string to clip out the standalone equation band.
* **Developer Customization Parameters (`equation_extractor.py`):**
  * **Vertical Slice Padding:** The extraction band uses `vertical_pad = 75` to establish safe vertical crop limits. For deep matrices, large summation symbols, fraction integrations, or multi-line derivations that get vertically clipped, increase this value to `90` or `100`.
  * **Tag Assignment Regex:** Modify `eq_pattern = re.compile(r'\(\s*[A-Z]?\d+\s*\)$')` if target documents index their structural equations using brackets `[1]` or specific sub-item characters like `(1a)`.

### 4. Table of Contents Generation (`--toc`)
* **Description:** Parses text streams linearly starting from the opening page to reconstruct document section hierarchies. It uses standard academic structural notations (e.g., *I. INTRODUCTION*, *A. System Model*) to index the document.
* **Developer Customization Parameters (`toc_generator.py`):**
  * **Header Pattern Rules:** Tweak `header_pattern` if target journals deviate from standard Roman numeral or uppercase letter classification frameworks.
  * **Parsing Sentinels:** The loop halts execution when encountering `"REFERENCES"` to avoid falsely registering authors or bibliography sections as text headers. Expand this sentinel list to include fields like `"APPENDIX"` or `"BIBLIOGRAPHY"` as required.

### 5. Citation Link Verification (`--citations`)
* **Description:** Evaluates body strings sequentially to parse cross-reference indicators (e.g., `[12]`). It maps links against the terminal bibliography items to identify missing links or orphan strings.
* **Developer Customization Parameters (`citation_validator.py`):**
  * **Citation Syntax Rules:** Adjust the underlying matching logic to shift between brackets `[#]`, superscript digits, or parenthetical author-date notation models.

---

## Semi-Automated Strategies

Interactive processing layers rely on structural document markup or direct user feedback to bypass challenging parsing rules.

### 1. Annotation-Driven Highlight Extraction (`--highlights`)
* **Description:** A robust fallback strategy for unstructured layouts or uncooperative legacy scans. The user marks target figures or formulas with standard yellow highlighting inside any external PDF viewer (e.g., Acrobat, Preview, Foxit). The engine extracts those exact highlighted coordinates from the unmasked canvas, temporarily wiping the visual highlight layer from memory so the text beneath remains perfectly clean in the output SVG.
* **Developer Customization Parameters (`highlight_extractor.py`):**
  * **Annotation Buffers:** Tweak `pad = 5` to scale the boundary clipping margin out from the highlight box paths.

### 2. Interactive Triage Interface (`--triage`)
* **Description:** Spawns a lightweight desktop GUI built on Tkinter that systematically displays layout candidate predictions alongside the raw text. Users accept, discard, or manually re-draw boundaries in real time, making short work of verification tasks.