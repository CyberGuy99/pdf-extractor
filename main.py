import argparse
import os
import sys
import fitz

# Import all modules
from tools.figure_extractor import extract_figures
from tools.table_isolator import extract_tables
from tools.toc_generator import generate_toc
from tools.equation_extractor import extract_equations
from tools.citation_validator import validate_citations
from tools.highlight_extractor import extract_highlights
from tools.triage_app import run_triage

def main():
    parser = argparse.ArgumentParser(description="Advanced Academic PDF Inspection Suite")
    
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("-l", "--layout", choices=["single", "double"], default="double", help="Page layout (default: double)")
    
    # Fully Automated Modules
    parser.add_argument("--figures", action="store_true", help="Extract figures automatically")
    parser.add_argument("--tables", action="store_true", help="Extract tables automatically")
    parser.add_argument("--equations", action="store_true", help="Extract numbered equations automatically")
    parser.add_argument("--toc", action="store_true", help="Generate programmatic Table of Contents")
    parser.add_argument("--citations", action="store_true", help="Validate internal citation linkages")
    
    # Human-in-the-Loop Modules
    parser.add_argument("--highlights", action="store_true", help="Extract SVGs natively drawn from PDF highlights")
    parser.add_argument("--triage", action="store_true", help="Launch UI to manually review/crop equations and tables")
    
    # Master switch (Only runs the automated ones)
    parser.add_argument("--all", action="store_true", help="Run all automated inspection tools")

    args = parser.parse_args()
    
    try:
        doc = fitz.open(args.pdf_path)
        full_path = args.pdf_path.split(".pdf")[0]

        pdf_title = doc.metadata.get("title")
        if not pdf_title:
            pdf_title = full_path

        pdf_title = pdf_title.replace(" ", "_") if pdf_title else "output"
        second_underscore_idx = pdf_title.find("_", pdf_title.find("_") + 1)
        if second_underscore_idx != -1:
            pdf_title = pdf_title[:second_underscore_idx]
        print(f"Opened PDF: '{pdf_title}' with {doc.page_count} pages.")
    except Exception as e:
        print(f"Failed to open PDF: {e}")
        sys.exit(1)

    print(f"--- Analyzing: {args.pdf_path} (Layout: {args.layout}) ---")

    # 1. Automatic Extraction
    if args.figures or args.all:
        print("\n[*] Extracting Figures...")
        print(pdf_title)
        svgs = extract_figures(doc, layout=args.layout, save_dir=f"{pdf_title}_figures")
        print(f"    Saved {len(svgs)} {pdf_title}_figures.")

    if args.tables or args.all:
        print("\n[*] Extracting Tables (Automated)...")
        tables = extract_tables(doc, layout=args.layout, save_dir=f"{pdf_title}_tables")
        print(f"    Saved {len(tables)} {pdf_title}_tables.")

    if args.equations or args.all:
        print("\n[*] Extracting Equations (Automated)...")
        eqs = extract_equations(doc, layout=args.layout, save_dir=f"{pdf_title}_equations")
        print(f"    Saved {len(eqs)} {pdf_title}_equations.")

    if args.toc or args.all:
        print("\n[*] Generating Table of Contents...")
        toc = generate_toc(doc)
        for item in toc:
            indent = "  " * item["level"]
            print(f"    {indent}- {item['title']} (Page {item['page']})")

    if args.citations or args.all:
        print("\n[*] Validating Citations...")
        report = validate_citations(doc)
        print(f"    Total Body Citations: {report['total_body_citations']}")
        print(f"    Total Bibliography Entries: {report['total_bibliography_items']}")
        if report['cited_but_missing_in_bibliography']:
            print(f"    [!] Warning: Missing in Bib: {report['cited_but_missing_in_bibliography']}")
        if report['in_bibliography_but_never_cited']:
            print(f"    [!] Warning: Unused in Body: {report['in_bibliography_but_never_cited']}")

    # 2. Human-in-the-loop Extraction
    if args.highlights:
        os.makedirs(f"{pdf_title}_highlights", exist_ok=True)
        print("\n[*] Extracting SVGs from PDF Highlights...")
        hl_files = extract_highlights(doc, save_dir=f"{pdf_title}_highlights")
        print(f"    Saved {len(hl_files)} custom highlight crops at {pdf_title}_highlights.")

    if args.triage:
        os.makedirs(f"{pdf_title}_triage", exist_ok=True)
        print("\n[*] Launching Manual Triage UI...")
        run_triage(doc, layout=args.layout, save_dir=f"{pdf_title}_triage")
        # UI prints its own save logs
            
    doc.close()
    print("\n--- Processing Complete ---")

if __name__ == '__main__':
    main()
