"""
Module for generating a programmatic Table of Contents from structural headers.
"""
import re

def generate_toc(doc):
    """
    Analyzes document text to reconstruct a table of contents by identifying 
    standard IEEE/Academic header formats (e.g., 'I. INTRODUCTION').
    
    Args:
        doc (fitz.Document): The loaded PyMuPDF document.
        
    Returns:
        list[dict]: A list of dictionary objects representing section hierarchy.
    """
    toc = []
    # Strictly match standard IEEE formats: "I. INTRODUCTION" or "A. System Model"
    header_pattern = re.compile(r'^(?:[IVX]+\.|[A-Z]\.)\s+[A-Z]')
    
    in_references = False

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for line in b["lines"]:
                    text = "".join([span["text"] for span in line["spans"]]).strip()
                    
                    # Stop parsing completely if we hit the references section
                    # to prevent authors from being flagged as headers.
                    if text.upper() == "REFERENCES" or text.upper() == "REFERENCES ":
                        in_references = True
                        
                    if in_references:
                        continue
                        
                    if header_pattern.match(text):
                        if text.startswith(tuple("IVX")):
                            level = 0
                        else:
                            level = 1
                            
                        toc.append({"level": level, "title": text, "page": page_num + 1})
                        
    return toc