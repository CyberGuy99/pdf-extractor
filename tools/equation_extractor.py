"""
Module for isolating and extracting standalone mathematical equations.
"""
import os

import fitz
import re
from tools.utils import export_svg_from_rect

def extract_equations(doc, layout='double', save_dir="equations"):
    """
    Scans document text lines for standard academic equation numbering 
    (e.g., "(1)", "(A2)") on the margins, and creates a vertical extraction band.
    
    Args:
        doc (fitz.Document): The loaded PyMuPDF document.
        layout (str): 'single' or 'double' column layout.
        save_dir (str): The directory where extracted equations will be saved.

    Returns:
        list: Filenames of the extracted equation SVGs.
    """
    written_files = []
    os.makedirs(save_dir, exist_ok=True)
    # Regex targets equation tags hugging the end of a line
    eq_pattern = re.compile(r'\(\s*[A-Z]?\d+\s*\)$') 
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_center = page.rect.width / 2
        
        for idx, b in enumerate(blocks):
            if b['type'] == 0:  # Ensure block is text, not an image
                for line in b["lines"]:
                    text = "".join([span["text"] for span in line["spans"]]).strip()
                    if eq_pattern.search(text):
                        bbox = fitz.Rect(line["bbox"])
                        
                        # 75-point padding acts as a wide safety net to prevent 
                        # vertical cropping of tall matrices or double integrals.
                        vertical_pad = 75 
                        
                        if layout == 'double':
                            if bbox.x0 > page_center: # Right column
                                eq_zone = fitz.Rect(page_center, max(0, bbox.y0 - vertical_pad), page.rect.width, min(page.rect.height, bbox.y1 + vertical_pad))
                            else: # Left column
                                eq_zone = fitz.Rect(0, max(0, bbox.y0 - vertical_pad), page_center, min(page.rect.height, bbox.y1 + vertical_pad))
                        else:
                            eq_zone = fitz.Rect(0, max(0, bbox.y0 - vertical_pad), page.rect.width, min(page.rect.height, bbox.y1 + vertical_pad))

                        svg_filename = f"equation_page_{page_num + 1}_eq_{idx + 1}.svg"
                        export_svg_from_rect(page, eq_zone, f"{save_dir}/{svg_filename}")
                        written_files.append(svg_filename)
                        
                        # Break out of the line loop to prevent double-extracting wrapped text
                        break
                        
    return written_files