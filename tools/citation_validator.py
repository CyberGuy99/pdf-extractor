"""
Module for validating internal citation linkages across an academic paper.
"""
import re

def validate_citations(doc):
    """
    Scrapes the document for [1] or [1]-[3] style citations and cross-references
    them with the bibliography section to find orphaned or unused references.
    
    Args:
        doc (fitz.Document): The loaded PyMuPDF document.
        
    Returns:
        dict: A report containing sets of missing and unused citations.
    """
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    # Safely split the document exactly where the References section begins
    parts = re.split(r'\n\s*(?:[IVX]+\.\s*)?REFERENCES\s*\n', full_text, maxsplit=1, flags=re.IGNORECASE)
    
    body_text = parts[0]
    reference_section = parts[1] if len(parts) > 1 else ""

    body_citations = set()
    
    # Target anything enclosed in brackets
    bracket_groups = re.findall(r'\[(.*?)\]', body_text)
    for group in bracket_groups:
        # Strip out spaces and hidden newlines that break digit checks
        group = group.replace(" ", "").replace("\n", "")
        dash_regex = r'[-–—\u2010-\u2015]'
        
        if re.search(dash_regex, group):
            # Expand citation ranges (e.g., [12-14] -> 12, 13, 14)
            ranges = re.split(dash_regex, group)
            if len(ranges) == 2 and ranges[0].isdigit() and ranges[1].isdigit():
                body_citations.update(range(int(ranges[0]), int(ranges[1]) + 1))
        else:
            # Expand comma-separated lists (e.g., [12, 14] -> 12, 14)
            for p in group.split(','):
                if p.isdigit():
                    body_citations.add(int(p))

    # Identify literal numeric lines in the bibliography block
    ref_list_matches = re.findall(r'\[(\d+)\]', reference_section)
    bibliography_citations = set([int(m) for m in ref_list_matches])
    
    return {
        "total_body_citations": len(body_citations),
        "total_bibliography_items": len(bibliography_citations),
        "cited_but_missing_in_bibliography": sorted(list(body_citations - bibliography_citations)),
        "in_bibliography_but_never_cited": sorted(list(bibliography_citations - body_citations))
    }