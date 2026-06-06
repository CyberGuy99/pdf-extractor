"""
Module for the Human-in-the-Loop (HITL) Triage GUI.
Allows users to rapidly accept, reject, or manually redraw extraction boundaries 
for difficult equations and tables via a Tkinter interface.
"""
import os

import fitz
import re
import sys
import tkinter as tk
from tools.utils import export_svg_from_rect


class PDFTriageApp:
    """
    Tkinter application class managing the image viewing, navigation state, 
    and mouse-driven boundary redrawing for candidate crops.
    """
    def __init__(self, root, doc, candidates, save_dir="triage_outputs"):
        self.root = root
        self.doc = doc
        self.candidates = candidates
        self.current_idx = 0
        self.save_dir = save_dir
        
        self.root.title("PDF Extraction Triage")
        self.root.geometry("1000x800")
        
        self.info_label = tk.Label(root, text="", font=("Arial", 14, "bold"))
        self.info_label.pack(pady=5)
        
        self.instructions = tk.Label(
            root, 
            text="RIGHT = Accept | LEFT = Reject | MOUSE DRAG = Draw new crop | UP/DOWN = Scroll View", 
            fg="blue", font=("Arial", 11, "bold")
        )
        self.instructions.pack(pady=5)
        
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.frame, bg="gray", cursor="cross")
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.root.bind("<Right>", self.accept)
        self.root.bind("<Left>", self.reject)
        self.root.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        self.user_rect = None
        self.user_coords = None
        
        # Scaling factor to map 150 DPI canvas pixels back to 72 DPI PDF coordinates
        self.scale = 150 / 72  
        
        self.load_current()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.user_rect:
            self.canvas.delete(self.user_rect)
        self.user_coords = None
        self.user_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=3)

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.user_rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.user_coords = (self.start_x, self.start_y, cur_x, cur_y)

    def load_current(self):
        if self.current_idx >= len(self.candidates):
            print("\nAll candidates processed!")
            self.root.destroy() 
            return
            
        cand = self.candidates[self.current_idx]
        self.info_label.config(text=f"Reviewing {cand['type'].upper()} ({self.current_idx + 1}/{len(self.candidates)})")
        
        page = self.doc[cand['page']]
        self.user_rect = None
        self.user_coords = None
        
        v_context = 250
        self.ctx_bbox = fitz.Rect(
            0, max(0, cand['bbox'].y0 - v_context),
            page.rect.width, min(page.rect.height, cand['bbox'].y1 + v_context)
        )
        
        pix = page.get_pixmap(clip=self.ctx_bbox, dpi=150)
        self.photo = tk.PhotoImage(data=pix.tobytes("ppm"))
        self.canvas.delete("all")
        
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        cx0 = (cand['bbox'].x0 - self.ctx_bbox.x0) * self.scale
        cy0 = (cand['bbox'].y0 - self.ctx_bbox.y0) * self.scale
        cx1 = (cand['bbox'].x1 - self.ctx_bbox.x0) * self.scale
        cy1 = (cand['bbox'].y1 - self.ctx_bbox.y0) * self.scale
        
        self.canvas.create_rectangle(cx0, cy0, cx1, cy1, outline="red", width=3, dash=(6, 6))

    def accept(self, event):
        cand = self.candidates[self.current_idx]
        page = self.doc[cand['page']]
        
        if self.user_coords:
            x0, y0, x1, y1 = self.user_coords
            left, right = min(x0, x1), max(x0, x1)
            top, bottom = min(y0, y1), max(y0, y1)
            
            pdf_x0 = self.ctx_bbox.x0 + (left / self.scale)
            pdf_y0 = self.ctx_bbox.y0 + (top / self.scale)
            pdf_x1 = self.ctx_bbox.x0 + (right / self.scale)
            pdf_y1 = self.ctx_bbox.y0 + (bottom / self.scale)
            
            final_bbox = fitz.Rect(max(0, pdf_x0), max(0, pdf_y0), min(page.rect.width, pdf_x1), min(page.rect.height, pdf_y1))
        else:
            final_bbox = cand['bbox']
            
        filename = f"{self.save_dir}/{cand['type']}_page_{cand['page']+1}_idx_{self.current_idx+1}.svg"
        export_svg_from_rect(page, final_bbox, filename)
        print(f"[+] Saved: {filename}")
        
        self.current_idx += 1
        self.load_current()

    def reject(self, event):
        print(f"[-] Rejected item {self.current_idx + 1}")
        self.current_idx += 1
        self.load_current()

def generate_candidates(doc, layout='double'):
    candidates = []

    eq_pattern = re.compile(r'\(\s*[A-Z]?\d+\s*\)$')
    table_pattern = re.compile(r'^TABLE\s+[IVX]+', re.IGNORECASE)
    fig_pattern = re.compile(r'^(?:FIG\.|Fig\.|Figure|FIGURE)\s+\d+', re.IGNORECASE)

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_center = page.rect.width / 2

        for b in blocks:
            if b['type'] == 0:
                for line in b["lines"]:
                    text = "".join([span["text"] for span in line["spans"]]).strip()
                    bbox = fitz.Rect(line["bbox"])

                    # 1. Check for Equations
                    if eq_pattern.search(text):
                        vertical_pad = 75
                        if layout == 'double':
                            left_x = page_center if bbox.x0 > page_center else 0
                            right_x = page.rect.width if bbox.x0 > page_center else page_center
                        else:
                            left_x, right_x = 0, page.rect.width

                        eq_zone = fitz.Rect(left_x, max(0, bbox.y0 - vertical_pad), right_x, min(page.rect.height, bbox.y1 + vertical_pad))
                        candidates.append({'type': 'equation', 'page': page_num, 'bbox': eq_zone})
                        break

                    # 2. Check for Tables
                    elif table_pattern.match(text):
                        # Tables usually have the caption ABOVE the table content
                        v_pad_down = 350
                        if layout == 'double':
                            left_x = page_center if bbox.x0 > page_center else 0
                            right_x = page.rect.width if bbox.x0 > page_center else page_center
                        else:
                            left_x, right_x = 0, page.rect.width

                        table_zone = fitz.Rect(left_x, max(0, bbox.y0 - 10), right_x, min(page.rect.height, bbox.y1 + v_pad_down))
                        candidates.append({'type': 'table', 'page': page_num, 'bbox': table_zone})
                        break

                    # 3. Check for Figures
                    elif fig_pattern.match(text):
                        # Figures usually have the caption BELOW the figure content
                        v_pad_up = 400
                        is_left = bbox.x0 < page_center
                        is_full = (bbox.width > page.rect.width * 0.6)

                        if layout == 'double' and not is_full:
                            left_x = 0 if is_left else page_center
                            right_x = page_center if is_left else page.rect.width
                        else:
                            left_x, right_x = 0, page.rect.width

                        # Grab a generous box ABOVE the caption
                        fig_zone = fitz.Rect(left_x, max(0, bbox.y0 - v_pad_up), right_x, bbox.y1)
                        candidates.append({'type': 'figure', 'page': page_num, 'bbox': fig_zone})
                        break

    return candidates

def run_triage(doc, layout='double', save_dir="triage_outputs"):
    """
    Initializes and launches the Tkinter Triage application.
    """
    print("[*] Scanning document for UI triage candidates...")
    candidates = generate_candidates(doc, layout=layout)
    
    if not candidates:
        print("    No equations or tables found for triage.")
        return

    print(f"    Found {len(candidates)} potential targets. Launching UI...")
    
    root = tk.Tk()
    # Force the window to pop up over the terminal
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    os.makedirs(save_dir, exist_ok=True)
    app = PDFTriageApp(root, doc, candidates, save_dir=save_dir)
    root.mainloop()
