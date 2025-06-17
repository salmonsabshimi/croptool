import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os

# === CONFIG ===
pdf_path = "S3D4_AFT3.pdf" #change this to your document 
output_folder = "ocr_all_pages" #change this to change the name of your output folder
final_output_pdf = "S3D4_AFT3_Cropped.pdf" #change this name to desired name
dpi = 300

# Create folder to store cropped images
os.makedirs(output_folder, exist_ok=True)

doc = fitz.open(pdf_path)
cropped_images = []

for i in range(1, len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    width, height = img.size

    # OCR: detect words and bounding boxes
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    y_cutoff = None
    for j, word in enumerate(data['text']):
        if "Correct" in word:
            line = ' '.join(data['text'][j:j+4])
            if "Correct Answer:" in line:
                y_cutoff = data['top'][j]
                break

    if y_cutoff:
        crop_box = (0, 200, width, y_cutoff - 10)
        print(f"[Page {i+1}] Found cutoff at y = {y_cutoff}")
    else:
        crop_box = (0, 200, width, int(height * 0.5))
        print(f"[Page {i+1}] Fallback cropping used")

    cropped = img.crop(crop_box)
    save_path = os.path.join(output_folder, f"page_{i+1}.png")
    cropped.save(save_path)
    cropped_images.append(cropped.convert("RGB"))

doc.close()

# === COMBINE TO PDF ===
if cropped_images:
    cropped_images[0].save(
        final_output_pdf,
        save_all=True,
        append_images=cropped_images[1:]
    )
    print(f"\n ALL DONE! Cropped PDF saved as: {final_output_pdf}")
else:
    print("Error: No pages saved.")
