import pytesseract
from PIL import Image

def extract_word_boxes(image: Image.Image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['text'])
    results = []

    for i in range(n_boxes):
        if int(data['conf'][i]) > 60 and data['text'][i].strip():
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            results.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "text": data['text'][i]
            })

    return results
