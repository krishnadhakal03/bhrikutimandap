
import os
from PIL import Image
import sys

def optimize_logo():
    source_path = r'f:\Bhrikutimandap\New Bhrikutimandap logo.png'
    dest_path = r'f:\Bhrikutimandap\static\img\logo_optimized.png'
    
    if not os.path.exists(source_path):
        print(f"Error: Source file not found at {source_path}")
        return
        
    try:
        with Image.open(source_path) as img:
            # Calculate new size maintaining aspect ratio
            # Default logo max-width in some templates is around 200px. 
            # Let's make it slightly larger for high-DPI screens (e.g., 400px width)
            base_width = 400
            w_percent = (base_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            
            # Resize uses high quality downsampling
            img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            
            # Save as optimized PNG
            img.save(dest_path, optimize=True, quality=85)
            
            print(f"Success! Logo optimized and saved to: {dest_path}")
            print(f"New dimensions: {base_width}x{h_size}")
            
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    optimize_logo()
