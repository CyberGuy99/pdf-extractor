import fitz
from utils import export_svg_from_rect

def extract_figures(doc, layout='double', prefix='Fig.'):
    written_files = []
    
    for page_num, page in enumerate(doc):
        page_center = page.rect.width / 2
        captions = sorted(page.search_for(prefix), key=lambda r: r.y0)
        
        for idx, rect in enumerate(captions):
            if layout == 'double':
                caption_column = "left" if rect.x0 < page_center else "right"
            else:
                caption_column = "single"
                
            associated_drawings = []
            
            # Scan vector elements sitting directly ABOVE the caption marker
            for d in page.get_drawings():
                d_rect = d["rect"]
                if rect.y0 - 650 <= d_rect.y1 <= rect.y0 + 5:
                    if layout == 'double':
                        if caption_column == "left" and d_rect.x0 < page_center:
                            associated_drawings.append(d_rect)
                        elif caption_column == "right" and d_rect.x1 > page_center:
                            associated_drawings.append(d_rect)
                    else:
                        associated_drawings.append(d_rect)
            
            # Calculate final extraction boundaries
            padding = 15
            if associated_drawings:
                min_x = min(r.x0 for r in associated_drawings)
                min_y = min(r.y0 for r in associated_drawings)
                max_x = max(r.x1 for r in associated_drawings)
                
                if layout == 'double':
                    if caption_column == "left":
                        final_left, final_right = max(0, min_x - padding), min(page.rect.width, max(page_center, max_x + padding))
                    else:
                        final_left, final_right = min(page_center, max(0, min_x - padding)), min(page.rect.width, max_x + padding)
                else:
                    final_left, final_right = max(0, min_x - padding), min(page.rect.width, max_x + padding)
                    
                figure_zone = fitz.Rect(final_left, max(0, min_y - padding), final_right, rect.y0)
            else:
                # Fallback for purely raster images
                if layout == 'double':
                    if caption_column == "left":
                        figure_zone = fitz.Rect(0, max(0, rect.y0 - 350), page_center, rect.y0)
                    else:
                        figure_zone = fitz.Rect(page_center, max(0, rect.y0 - 350), page.rect.width, rect.y0)
                else:
                    figure_zone = fitz.Rect(0, max(0, rect.y0 - 350), page.rect.width, rect.y0)
            
            svg_filename = f"figure_page_{page_num + 1}_fig_{idx + 1}.svg"
            export_svg_from_rect(page, figure_zone, svg_filename)
            written_files.append(svg_filename)

    return written_files
