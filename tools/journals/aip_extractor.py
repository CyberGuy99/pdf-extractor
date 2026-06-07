"""
Specialized figure extraction profile for AIP Publishing (including AVS Quantum Science).
"""
import os

import fitz
import re
from tools.utils import export_svg_from_rect

def extract_figures_aip(doc, layout='double', save_dir='figures'):
    written_files = []
    os.makedirs(save_dir, exist_ok=True)
    caption_pattern = re.compile(r'^\s*(?:FIG\.|Fig\.)\s*\d+')

    for page_num, page in enumerate(doc):
        page_w = page.rect.width
        page_h = page.rect.height
        page_center = page_w / 2
        
        # 1. Locate and deduplicate caption blocks
        captions = []
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0: 
                text = "".join([span["text"] for line in b["lines"] for span in line["spans"]]).strip()
                if caption_pattern.match(text):
                    captions.append(fitz.Rect(b["bbox"]))
        
        unique_captions = []
        for c in sorted(captions, key=lambda r: r.y0):
            if not unique_captions or abs(c.y0 - unique_captions[-1].y0) > 20:
                unique_captions.append(c)
                
        # 2. Collect all raw graphical elements on the page (Images and Vector Drawings)
        elements = []
        for img in page.get_image_info():
            elements.append(fitz.Rect(img["bbox"]))
        for d in page.get_drawings():
            elements.append(fitz.Rect(d["rect"]))
            
        # 3. Define bounding boxes for each caption
        for idx, c_rect in enumerate(unique_captions):
            fig_elements = []
            
            # Grab elements strictly above the caption, ignoring page headers/margins
            for el in elements:
                if 40 < el.y0 < c_rect.y0 and el.y1 <= c_rect.y0 + 10:
                    # Filter out elements too far up to avoid blending into prior figures
                    if c_rect.y0 - el.y1 < 450:
                        fig_elements.append(el)
            
            # Determine Vertical (Y) Span
            if fig_elements:
                min_y = min(r.y0 for r in fig_elements)
                max_y = c_rect.y1
                
                # Check if elements or the caption occupy both columns
                has_left = any(r.x0 < page_center - 10 for r in fig_elements) or (c_rect.x0 < page_center - 10)
                has_right = any(r.x1 > page_center + 10 for r in fig_elements) or (c_rect.x1 > page_center + 10)
                is_wide = has_left and has_right
            else:
                # Fallback geometry if elements are empty or embedded invisibly
                min_y = max(40, c_rect.y0 - 250)
                max_y = c_rect.y1
                is_wide = (layout != 'double') or (c_rect.width > page_w * 0.5)
                has_left = c_rect.x0 < page_center

            # Determine Horizontal (X) Span
            if layout != 'double' or is_wide:
                min_x = 0
                max_x = page_w
            else:
                # Restrict to the specific column side
                if has_left:
                    min_x = 0
                    max_x = page_center
                else:
                    min_x = page_center
                    max_x = page_w
            
            # 4. Generate final box with uniform padding
            padding = 15
            final_rect = fitz.Rect(
                max(0, min_x - padding),
                max(0, min_y - padding),
                min(page_w, max_x + padding),
                min(page_h, max_y + padding)
            )

            svg_filename = f"figure_page_{page_num + 1}_fig_{idx + 1}.svg"
            export_svg_from_rect(page, final_rect, f"{save_dir}/{svg_filename}")
            written_files.append(svg_filename)

    return written_files
