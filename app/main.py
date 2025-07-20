from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import io

app = FastAPI()

# Allow access from any frontend (like Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # ✅ Preprocessing steps
    gray = ImageOps.grayscale(image)                     # Convert to grayscale
    contrast = ImageOps.autocontrast(gray)               # Improve contrast
    sharpened = contrast.filter(ImageFilter.SHARPEN)     # Slightly sharpen edges
    bw = sharpened.point(lambda x: 0 if x < 140 else 255, '1')  # Binarize

    # Use OCR
    config = "--oem 1 --psm 6"
    raw_text = pytesseract.image_to_string(bw, config=config)

    # Clean output
    cleaned_text = " ".join(raw_text.split())

    return {"text": cleaned_text}
