# Academic PDF Inspection and Extraction Suite

A robust Python-based framework designed to programmatically parse, inspect, and extract core elements from scientific literature and academic documents. Optimized to resolve common layout challenges—including double-column formats, text-graphic overlaps, and complex formulas—this system pairs automated background heuristics with an interactive Human-in-the-Loop (HITL) architecture.

## Workflow Execution Models

To adapt to the significant stylistic variance across academic publishers, the suite divides its functionality into two distinct processing tiers:

* **Automated Mode (`--figures`, `--tables`, `--equations`, `--toc`, `--citations`)**
  A high-throughput, headless processing tier requiring zero manual oversight. This mode utilizes geometric layout tracking and regex pattern filtering to bulk-extract structural elements directly into standardized output files.
* **Semi-Automated Mode (`--triage`, `--highlights`)**
  An interactive, precision-focused tier designed to maintain absolute layout fidelity. This layout tier leverages computer-assisted structural tracking while integrating human validation to manage non-standard, older archival, or highly complex document structures.

---


## System Installation

1. Clone the project environment:
   ```bash
   git clone [https://github.com/yourusername/pdf-extractor.git](https://github.com/yourusername/pdf-extractor.git)
   cd pdf-extractor
   ```
2. Install dependency requirements:
   ```bash
   pip install -r requirements.txt
   ```

(Note: Linux/WSL environments require a global Tkinter installation via sudo apt install python3-tk).

## Execution Instructions

The core system is orchestrated via main.py.

1. Automated Execution (Tier 1)

Run headless extraction heuristics across the entire input file:
   ```bash
   # Execute all background automated components
   python main.py manuscript.pdf --all

   # Execute isolated target modules
   python main.py manuscript.pdf --figures --equations
   ```

2. Interactive Triage Selection (Tier 2)
Generates coordinate crop hypotheses for difficult equations and data tables, then pushes them to the Tkinter verification app:
  ```bash
  python main.py manuscript.pdf --triage
  ```
Right Arrow Key: Approve current crop and commit to disk.
Left Arrow Key: Discard current candidate crop.
Mouse Left-Click & Drag: Draw a custom bounding rectangle to override an automated layout prediction.

3. Native Highlight Parsing (Tier 3)
  ```bash
  python main.py annotated_manuscript.pdf --highlights
  ```

[Extraction Strategy Overview](extract_overview.md)

## Command Line Reference

| Argument | Specification |
| :--- | :--- |
| `-l`, `--layout` | Sets column context parsing. Options: `single` or `double` (default). |
| `--figures` | Executes headless background extraction of figures to vector SVG files. |
| `--tables` | Executes headless background isolation of data tables to SVG files. |
| `--equations` | Executes headless background isolation of equations to SVG files. |
| `--toc` | Compiles a programmatic Table of Contents outline to the terminal. |
| `--citations` | Examines body text formatting to trace and validate bibliography mapping. |
| `--triage` | Launches the interactive Tkinter verification interface application. |
| `--highlights`| Parses user-drawn highlight annotations into isolated SVG exports. |
| `--all` | Runs every headless background processing module in sequence. |

## License

Distributed under the terms of the MIT License. Refer to LICENSE for complete terms and compliance details.


