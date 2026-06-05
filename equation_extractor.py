import fitz
import re
from utils import export_svg_from_rect

def extract_equations(doc, layout='double'):
    written_files = []
    eq_pattern = re.compile(r'\(\s*[A-Z]?\d+\s*\)$') 
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_center = page.rect.width / 2
        
        for idx, b in enumerate(blocks):
            if b['type'] == 0:
                for line in b["lines"]:
                    text = "".join([span["text"] for span in line["spans"]]).strip()
                    if eq_pattern.search(text):
                        bbox = fitz.Rect(line["bbox"])
                        
                        # Drastically increased padding to prevent vertical cropping of tall matrices/integrals
                        vertical_pad = 75 
                        
                        if layout == 'double':
                            if bbox.x0 > page_center: # Right column
                                eq_zone = fitz.Rect(page_center, max(0, bbox.y0 - vertical_pad), page.rect.width, min(page.rect.height, bbox.y1 + vertical_pad))
                            else: # Left column
                                eq_zone = fitz.Rect(0, max(0, bbox.y0 - vertical_pad), page_center, min(page.rect.height, bbox.y1 + vertical_pad))
                        else:
                            eq_zone = fitz.Rect(0, max(0, bbox.y0 - vertical_pad), page.rect.width, min(page.rect.height, bbox.y1 + vertical_pad))

                        svg_filename = f"equation_page_{page_num + 1}_eq_{idx + 1}.svg"
                        export_svg_from_rect(page, eq_zone, svg_filename)
                        written_files.append(svg_filename)
                        break
                        
    return written_files