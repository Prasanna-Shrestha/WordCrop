from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, ImageFilter, UnidentifiedImageError
import pytesseract
import io

app = FastAPI()

# Allow access from mobile or any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    # Checking file type to ensure that only image is passed
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="File could not be processed as an image.")

    # Checking image size to ensure very small image is not passed
    if image.width < 20 or image.height < 20:
        raise HTTPException(status_code=400, detail="Image is too small. Must be at least 20x20 pixels.")

    # Image Preprocessing to improve accuracy
    gray = ImageOps.grayscale(image)
    contrast = ImageOps.autocontrast(gray)
    sharpened = contrast.filter(ImageFilter.SHARPEN)
    bw = sharpened.point(lambda x: 0 if x < 140 else 255, '1')

    config = "--oem 1 --psm 6"
    raw_text = pytesseract.image_to_string(bw, config=config)
    cleaned_text = " ".join(raw_text.split())

    if not cleaned_text:
        return {"text": "", "message": "No text detected in the image."}

    return {"text": cleaned_text}
