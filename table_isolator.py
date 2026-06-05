import fitz
from utils import export_svg_from_rect

def extract_tables(doc, layout='double', prefix='TABLE'):
    written_files = []
    
    for page_num, page in enumerate(doc):
        page_center = page.rect.width / 2
        raw_captions = sorted(page.search_for(prefix), key=lambda r: r.y0)
        
        # Increased deduplication threshold to 150 to prevent double-captures
        captions = []
        for rect in raw_captions:
            if not captions or abs(rect.y0 - captions[-1].y0) > 150:
                captions.append(rect)
        
        for idx, rect in enumerate(captions):
            caption_column = "left" if rect.x0 < page_center and layout == 'double' else "right" if layout == 'double' else "single"
            associated_drawings = []
            
            for d in page.get_drawings():
                d_rect = d["rect"]
                if rect.y1 - 5 <= d_rect.y0 <= rect.y1 + 400:
                    if layout == 'double':
                        if caption_column == "left" and d_rect.x0 < page_center:
                            associated_drawings.append(d_rect)
                        elif caption_column == "right" and d_rect.x1 > page_center:
                            associated_drawings.append(d_rect)
                    else:
                        associated_drawings.append(d_rect)
                        
            padding = 10
            if associated_drawings:
                min_x = min(r.x0 for r in associated_drawings)
                max_x = max(r.x1 for r in associated_drawings)
                max_y = max(r.y1 for r in associated_drawings)
                
                table_zone = fitz.Rect(max(0, min_x - padding), rect.y0 - padding, min(page.rect.width, max_x + padding), max_y + padding)
                
                svg_filename = f"table_page_{page_num + 1}_idx_{idx + 1}.svg"
                export_svg_from_rect(page, table_zone, svg_filename)
                written_files.append(svg_filename)
                
    return written_files