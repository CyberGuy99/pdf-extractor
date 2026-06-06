"""
Module for automatically detecting and extracting vector and raster figures from PDFs.
"""
import os

import fitz
import re
from tools.utils import export_svg_from_rect

def extract_figures(doc, layout='double', save_dir='figures'):
    """
    Scans a document for figure captions and uses both vector drawing coordinates
    and embedded image coordinates above the caption to calculate a bounding box.
    Uses 'column ceilings' to prevent overlapping bounds when multiple figures
    share a column.

    Args:
        doc (fitz.Document): The loaded PyMuPDF document.
        layout (str): 'single' or 'double' column layout.
        save_dir (str): The directory where extracted tables will be saved.

    Returns:
        list: A list of filenames corresponding to the saved SVGs.
    """
    written_files = []
    os.makedirs(save_dir, exist_ok=True)

    # Matches "Fig. 1", "FIG. 1", "Figure 1" strictly at the START of a text block
    caption_pattern = re.compile(r'^(?:FIG\.|Fig\.|Figure|FIGURE)\s+\d+', re.IGNORECASE)

    for page_num, page in enumerate(doc):
        page_center = page.rect.width / 2
        captions = []

        # 1. Identify valid captions
        for b in page.get_text("dict")["blocks"]:
            if b['type'] == 0:
                text = "".join([span["text"] for line in b["lines"] for span in line["spans"]]).strip()
                if caption_pattern.match(text):
                    captions.append(fitz.Rect(b["bbox"]))

        # Sort top-to-bottom
        captions = sorted(captions, key=lambda r: r.y0)

        # 2. Gather filtered visual elements
        visuals = []
        for d in page.get_drawings():
            r = d["rect"]
            # Filter out tiny vector noise (dots/text) and full-page background boxes
            if r.width > 5 and r.height > 5 and r.width < page.rect.width * 0.95:
                visuals.append(r)

        for img in page.get_image_info():
            r = fitz.Rect(img["bbox"])
            visuals.append(r)

        # Keep track of the lowest "cleared" point on the page to prevent figure merging
        ceil_left = 0
        ceil_right = 0
        ceil_full = 0

        for idx, cap in enumerate(captions):
            is_full_width = (cap.width > page.rect.width * 0.6)
            is_left_col = cap.x0 < page_center

            # Determine the hard ceiling for this specific caption
            if layout == 'single' or is_full_width:
                ceiling = max(ceil_full, ceil_left, ceil_right)
            elif is_left_col:
                ceiling = max(ceil_left, ceil_full)
            else:
                ceiling = max(ceil_right, ceil_full)

            associated_visuals = []

            # 3. Match visuals to this caption boundary
            for v in visuals:
                v_center_x = (v.x0 + v.x1) / 2
                v_is_full = (v.width > page.rect.width * 0.6)
                v_is_left = v_center_x < page_center

                # Visual must fall between the previous caption (ceiling) and this caption
                if v.y1 <= cap.y0 + 5 and v.y0 >= ceiling - 5:
                    if layout == 'single' or is_full_width or v_is_full:
                        associated_visuals.append(v)
                    elif is_left_col and v_is_left:
                        associated_visuals.append(v)
                    elif not is_left_col and not v_is_left:
                        associated_visuals.append(v)

            # Update the ceiling for the NEXT figure on this page
            if layout == 'single' or is_full_width:
                ceil_full = ceil_left = ceil_right = cap.y1
            elif is_left_col:
                ceil_left = cap.y1
            else:
                ceil_right = cap.y1

            # 4. Calculate extraction bounding box
            padding = 10
            if associated_visuals:
                min_x = min(v.x0 for v in associated_visuals)
                min_y = min(v.y0 for v in associated_visuals)
                max_x = max(v.x1 for v in associated_visuals)

                final_is_full = is_full_width or ((max_x - min_x) > page.rect.width * 0.6)

                if layout == 'double' and not final_is_full:
                    if is_left_col:
                        f_left, f_right = max(0, min_x - padding), min(page_center, max_x + padding)
                    else:
                        f_left, f_right = max(page_center, min_x - padding), min(page.rect.width, max_x + padding)
                else:
                    f_left, f_right = max(0, min_x - padding), min(page.rect.width, max_x + padding)

                crop_box = fitz.Rect(f_left, max(ceiling, min_y - padding), f_right, cap.y0)
            else:
                # Fallback zone if visuals are purely textual equations or missing
                if layout == 'double' and not is_full_width:
                    if is_left_col:
                        crop_box = fitz.Rect(0, max(ceiling, cap.y0 - 250), page_center, cap.y0)
                    else:
                        crop_box = fitz.Rect(page_center, max(ceiling, cap.y0 - 250), page.rect.width, cap.y0)
                else:
                    crop_box = fitz.Rect(0, max(ceiling, cap.y0 - 250), page.rect.width, cap.y0)
            
            svg_filename = f"figure_page_{page_num + 1}_fig_{idx + 1}.svg"
            export_svg_from_rect(page, crop_box, f"{save_dir}/{svg_filename}")
            written_files.append(svg_filename)

    return written_files
