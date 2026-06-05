"""
Shared utility functions for the PDF extraction suite.
"""
import fitz

def export_svg_from_rect(page, rect, output_filename):
    """
    Safely crops a page to a specific bounding box, extracts the SVG vector data, 
    and restores the page's original crop box to prevent corrupting downstream tasks.
    
    Args:
        page (fitz.Page): The PyMuPDF page object.
        rect (fitz.Rect): The bounding box coordinates to crop.
        output_filename (str): The destination file path.
    """
    original_cropbox = page.cropbox
    
    # Apply the new crop zone
    page.set_cropbox(rect)
    svg_data = page.get_svg_image()
    
    # Save to file
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(svg_data)
        
    # Restore the original page box
    page.set_cropbox(original_cropbox)