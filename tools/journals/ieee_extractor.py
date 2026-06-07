"""
Specialized figure extraction profile for IEEEE.
"""
import os

import fitz
import re
from tools.utils import export_svg_from_rect

def extract_figures_ieee(doc, save_dir='figures'):
    written_files = []
    os.makedirs(save_dir, exist_ok=True)
    # IEEE standard caption pattern (often "Fig. 1." or "Figure 1.")
    caption_pattern = re.compile(r'^\s*(?:Fig\.|FIG\.|Figure|FIGURE)\s*\d+[\.:]', re.IGNORECASE)
    
    for page_num, page in enumerate(doc):
        page_w = page.rect.width
        page_h = page.rect.height
        page_center = page_w / 2
        
        # 1. Line-Level Caption Detection
        captions = []
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0: 
                for line in b["lines"]:
                    line_text = "".join([span["text"] for span in line["spans"]]).strip()
                    if caption_pattern.match(line_text):
                        # Store both the exact line coordinate and its parent block container
                        captions.append({
                            "line_rect": fitz.Rect(line["bbox"]),
                            "block_rect": fitz.Rect(b["bbox"])
                        })
                        break # Process next text block once found
        
        unique_captions = []
        # Sort sequentially from top-to-bottom, left-to-right
        for c in sorted(captions, key=lambda item: (item["line_rect"].y0, item["line_rect"].x0)):
            cl = c["line_rect"]
            is_duplicate = any(abs(cl.y0 - uc["line_rect"].y0) < 10 and abs(cl.x0 - uc["line_rect"].x0) < 20 for uc in unique_captions)
            if not is_duplicate:
                unique_captions.append(c)
                
        # 2. Collect raw graphical data paths
        elements = [fitz.Rect(img["bbox"]) for img in page.get_image_info()]
        elements += [fitz.Rect(d["rect"]) for d in page.get_drawings()]
            
        # 3. Process every verified caption
        for idx, c_data in enumerate(unique_captions):
            c_rect = c_data["line_rect"]
            b_rect = c_data["block_rect"]
            
            # True column span determination via pure geometry
            is_wide_caption = (c_rect.x0 < page_center - 40) and (c_rect.x1 > page_center + 40)
            c_col = 'wide' if is_wide_caption else ('left' if c_rect.x0 < page_center else 'right')
            
            # --- THE CEILING LOGIC ---
            ceiling = 40  
            for other_c in unique_captions:
                ocl = other_c["line_rect"]
                if ocl.y0 < c_rect.y0:
                    other_is_wide = (ocl.x0 < page_center - 40) and (ocl.x1 > page_center + 40)
                    other_col = 'wide' if other_is_wide else ('left' if ocl.x0 < page_center else 'right')
                    if other_col == c_col or c_col == 'wide' or other_col == 'wide':
                        if other_c["block_rect"].y1 > ceiling:
                            ceiling = other_c["block_rect"].y1 + 5
                            
            # Isolate elements within the column boundary rules
            fig_elements = []
            for el in elements:
                if ceiling < el.y1 and el.y0 < c_rect.y0:
                    el_center = (el.x0 + el.x1) / 2
                    el_col = 'left' if el_center < page_center else 'right'
                    is_wide_el = el.width > page_w * 0.5
                    
                    if c_col == 'wide' or is_wide_el or el_col == c_col:
                        fig_elements.append(el)
            
            # --- CROPPING BOUNDS ---
            if fig_elements:
                min_x = min(r.x0 for r in fig_elements)
                min_y = min(r.y0 for r in fig_elements)
                max_x = max(r.x1 for r in fig_elements)
                max_y = b_rect.y1  # Captures the entire multi-line text block smoothly
            else:
                # Safe, generous box allocation for complex hidden math layouts
                min_y = max(ceiling, c_rect.y0 - 250)
                max_y = b_rect.y1
                if c_col == 'wide':
                    min_x, max_x = 40, page_w - 40
                elif c_col == 'left':
                    min_x, max_x = 40, page_center - 10
                else:
                    min_x, max_x = page_center + 10, page_w - 40
                    
            # Column wall enforcement to split side-by-side figures perfectly
            if c_col == 'left':
                max_x = min(max_x, page_center - 2)
            elif c_col == 'right':
                min_x = max(min_x, page_center + 2)
                
            # 4. Save clean output vector file
            padding = 10
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
