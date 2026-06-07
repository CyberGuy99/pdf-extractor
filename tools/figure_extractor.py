"""
Figure Extractor Router.
Detects the journal publisher from the PDF metadata or first page text, 
and routes the document to the corresponding journal-specific extraction profile.
"""
import fitz

# Import the specific journal profiles
from tools.journals.base_extractor import extract_figures_base
from tools.journals.aip_extractor import extract_figures_aip
from tools.journals.ieee_extractor import extract_figures_ieee

def detect_journal(doc):
    """
    Scans the first page for copyright strings or DOI prefixes to identify the publisher.
    """
    first_page_text = doc[0].get_text("text").lower()
    
    # Check for AIP Publishing or AVS
    if "aip publishing" in first_page_text or "avs quantum" in first_page_text or "10.1116/" in first_page_text:
        return "AIP"
        
    # Check for IEEE
    elif "ieee" in first_page_text or "10.1109/" in first_page_text:
        return "IEEE"
        
    # Check for Nature / Springer
    elif "macmillan publishers" in first_page_text or "springer nature" in first_page_text:
        return "NATURE"
        
    return "UNKNOWN"

def extract_figures(doc, layout='double', save_dir='figures'):
    """
    The main entry point called by main.py. Detects the journal and routes the task.
    """
    journal_profile = detect_journal(doc)
    print(f"    [!] Detected Journal Profile: {journal_profile}")
    
    if journal_profile == "AIP":
        return extract_figures_aip(doc, layout, save_dir=save_dir)
        
    elif journal_profile == "IEEE":
        return extract_figures_ieee(doc, save_dir=save_dir)
        
    else:
        print("    [!] Using fallback baseline extractor...")
        return extract_figures_base(doc, layout)
