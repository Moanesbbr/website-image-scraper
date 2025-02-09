import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from threading import Thread
from PIL import Image, ImageTk
from io import BytesIO

class ImageScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Website Image Scraper")
        self.root.geometry("800x600")
        
        # URL Frame
        url_frame = ttk.LabelFrame(root, text="Website URL", padding="10")
        url_frame.pack(fill="x", padx=10, pady=5)
        
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(fill="x", expand=True)
        
        # Output Directory Frame
        dir_frame = ttk.LabelFrame(root, text="Save Location", padding="10")
        dir_frame.pack(fill="x", padx=10, pady=5)
        
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side="right", padx=5)
        
        # Control Buttons
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.scan_btn = ttk.Button(btn_frame, text="Scan for Images", command=self.start_scanning)
        self.scan_btn.pack(side="left", padx=5)
        
        self.download_btn = ttk.Button(btn_frame, text="Download Selected", command=self.download_selected)
        self.download_btn.pack(side="left", padx=5)
        self.download_btn.config(state="disabled")
        
        # Progress Bar
        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Image Preview Area
        preview_frame = ttk.LabelFrame(root, text="Image Preview", padding="10")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas and scrollbar for image list
        self.canvas = tk.Canvas(preview_frame)
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.image_vars = []
        self.image_labels = []
        self.image_references = []
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def start_scanning(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.scan_btn.config(state="disabled")
        self.clear_preview()
        Thread(target=self.scan_website, args=(url,)).start()
    
    def clear_preview(self):
        for label in self.image_labels:
            label.destroy()
        self.image_vars.clear()
        self.image_labels.clear()
        self.image_references.clear()
    
    def scan_website(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img')
            
            for i, img in enumerate(images):
                src = img.get('src')
                if src:
                    if not src.startswith(('http://', 'https://')):
                        src = urllib.parse.urljoin(url, src)
                    
                    try:
                        img_response = requests.get(src)
                        img_data = Image.open(BytesIO(img_response.content))
                        
                        # Resize image for preview
                        img_data.thumbnail((150, 150))
                        photo = ImageTk.PhotoImage(img_data)
                        
                        self.root.after(0, self.add_image_preview, photo, src, i)
                        self.image_references.append(photo)
                        
                    except Exception as e:
                        print(f"Error loading image {src}: {e}")
            
            self.root.after(0, self.enable_buttons)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to scan website: {str(e)}"))
            self.root.after(0, lambda: self.scan_btn.config(state="normal"))
    
    def add_image_preview(self, photo, src, index):
        var = tk.BooleanVar()
        self.image_vars.append(var)
        
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(pady=5)
        
        check = ttk.Checkbutton(frame, variable=var)
        check.pack(side="left")
        
        label = ttk.Label(frame, image=photo)
        label.pack(side="left")
        
        url_label = ttk.Label(frame, text=src, wraplength=400)
        url_label.pack(side="left", padx=5)
        
        self.image_labels.append(frame)
    
    def enable_buttons(self):
        self.scan_btn.config(state="normal")
        self.download_btn.config(state="normal")
    
    def download_selected(self):
        save_dir = self.dir_entry.get()
        if not save_dir:
            messagebox.showerror("Error", "Please select a save location")
            return
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        selected_images = [(var.get(), label.winfo_children()[2]['text']) 
                          for var, label in zip(self.image_vars, self.image_labels)]
        selected_images = [url for selected, url in selected_images if selected]
        
        if not selected_images:
            messagebox.showinfo("Info", "No images selected")
            return
        
        Thread(target=self.download_images, args=(selected_images, save_dir)).start()
    
    def download_images(self, urls, save_dir):
        total = len(urls)
        self.progress['maximum'] = total
        self.progress['value'] = 0
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url)
                filename = os.path.join(save_dir, f"image_{i+1}{os.path.splitext(url)[1]}")
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                self.root.after(0, lambda v=i+1: self.progress.configure(value=v))
                
            except Exception as e:
                print(f"Error downloading {url}: {e}")
        
        self.root.after(0, lambda: messagebox.showinfo("Success", "Download completed!"))
        self.root.after(0, lambda: self.progress.configure(value=0))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageScraperGUI(root)
    root.mainloop()