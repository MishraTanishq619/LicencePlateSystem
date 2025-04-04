import pytesseract
from PIL import Image

# Set the Tesseract path (if needed)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Test OCR on an image
text = pytesseract.image_to_string(Image.open('test_image.jpg'))
print("Extracted Text:", text)