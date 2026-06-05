# Academic PDF Inspector & Extractor

A robust suite of Python tools designed to programmatically parse, inspect, and extract elements from academic and scientific PDFs. It handles complex parsing challenges—such as double-column layouts, overlapping text, and multi-line equations—by combining automated heuristics with an intuitive Human-in-the-Loop (HITL) GUI.

## Core Features

* **Figure & Table Extraction**
  Intelligently isolates and crops vector graphics and tables into clean SVGs.
* **Equation Isolator**
  Automatically targets and extracts numbered formulas (e.g., `(1)`).
* **Programmatic ToC**
  Generates a Table of Contents by analyzing structural header text (e.g., `I. INTRODUCTION`).
* **Citation Validator**
  Scrapes body text to identify orphaned citations or missing bibliography entries.
* **"Triage" UI**
  A lightweight Tkinter GUI to quickly approve, reject, or redraw crop boundaries on tricky tables and equations.
* **Native Highlight Parsing**
  Leverages your PDF viewer's native highlight tool. Highlight target areas, and the script exports those exact coordinates as SVGs.

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/pdf-extractor.git](https://github.com/yourusername/pdf-extractor.git)
   cd pdf-extractor
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Linux/WSL users must ensure Tkinter is installed globally via `sudo apt install python3-tk`).*

## The Tiered Workflow Strategy

Because PDF layouts can vary wildly between journals, this tool is built around a tiered extraction philosophy, balancing automation speed with human accuracy:

* **Tier 1: Headless Bulk Automation (`--equations`, `--tables`)**
  Maximum speed, zero human effort. Ideal for researchers scraping hundreds of standard IEEE papers at once to build datasets. Processes everything in the background via automated heuristics.
* **Tier 2: The Triage App (`--triage`)**
  Medium speed, low human effort. The algorithm guesses the boundaries, and a human rapidly approves, rejects, or adjusts them via a fast GUI. Perfect for processing a handful of structurally complex papers with perfect accuracy.
* **Tier 3: Native Highlighting (`--highlights`)**
  Low speed, high human effort. The user manually highlights targets in a standard PDF viewer, and the script strictly extracts those coordinates. The ultimate fallback for totally unstructured or bizarrely formatted legacy documents.

## Usage Modes

The tool operates via `main.py` and supports the following workflows:

### 1. Fully Automated Mode (Tier 1)
Runs heuristics blindly across the entire document.
```bash
# Run all automated extractors
python main.py paper.pdf --all

# Or run specific headless modules
python main.py paper.pdf --figures --equations --citations
```

### 2. Human-in-the-Loop Triage Mode (Tier 2)
Generates candidate crops for equations and tables, then launches a fast Tkinter GUI for manual validation.
```bash
python main.py paper.pdf --triage
```
* **Right Arrow:** Accept and save crop.
* **Left Arrow:** Reject and discard candidate.
* **Mouse Drag:** Draw a custom bounding box to fix an incorrect crop.

### 3. Native Highlight Mode (Tier 3)
Open your PDF in any standard viewer (Acrobat, Preview, Foxit) and use the yellow highlight tool to mark equations, charts, or text blocks. Save the document, then run:
```bash
python main.py highlighted_paper.pdf --highlights
```
The script will cleanly remove the highlighter annotations from memory and extract unmasked SVGs of the selected areas.

## Outputs
All outputs are saved in a folder determined by (1) the pdf's title or filepath (as a backup) and (2) the usage mode.

## Command Line Arguments

| Argument | Description |
| :--- | :--- |
| `-l`, `--layout` | `single` or `double` (default). Adjusts the spatial scanning logic. |
| `--figures` | Headless extraction of figures to SVG. |
| `--tables` | Headless extraction of tables to SVG. |
| `--equations` | Headless extraction of numbered equations to SVG. |
| `--toc` | Generate a terminal-based Table of Contents. |
| `--citations` | Validate internal `[#]` citation linkages. |
| `--triage` | Launch the Tkinter review GUI. |
| `--highlights`| Extract SVGs from native PDF highlight annotations. |
| `--all` | Execute all headless automated modules. |

## Contributing

Pull requests are welcome. If you encounter parsing bugs with specific journal formats (e.g., ACM, Nature), please open an issue and include a reproducible PDF sample if possible.

## License

Distributed under the MIT License. See `LICENSE` for more information.