import fitz
from utils import export_svg_from_rect

def extract_highlights(doc):
    written_files = []
    
    for page_num, page in enumerate(doc):
        bboxes_to_extract = []
        annots_to_delete = []
        
        # Step 1: Find highlights and record their coordinates
        for idx, annot in enumerate(page.annots()):
            if annot.type[0] == fitz.PDF_ANNOT_HIGHLIGHT:
                bbox = annot.rect
                
                # Add a 5-point padding so the stroke/text right on the edge isn't clipped
                pad = 5
                padded_bbox = fitz.Rect(
                    max(0, bbox.x0 - pad),
                    max(0, bbox.y0 - pad),
                    min(page.rect.width, bbox.x1 + pad),
                    min(page.rect.height, bbox.y1 + pad)
                )
                
                bboxes_to_extract.append((idx, padded_bbox))
                annots_to_delete.append(annot)
                
        # Step 2: Delete the highlight annotations so they don't mask the text
        # (This only deletes them in memory, it won't ruin your original PDF file)
        for annot in annots_to_delete:
            page.delete_annot(annot)
            
        # Step 3: Export the SVGs from the cleaned page
        for idx, padded_bbox in bboxes_to_extract:
            svg_filename = f"highlight_page_{page_num + 1}_idx_{idx + 1}.svg"
            export_svg_from_rect(page, padded_bbox, svg_filename)
            written_files.append(svg_filename)
                
    return written_files