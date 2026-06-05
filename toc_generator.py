import re

def generate_toc(doc):
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