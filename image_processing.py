import io
import pytesseract
from PIL import Image
import numpy as np

def extract_text_from_image(image):
    """
    Extract text from an image using OCR
    
    Args:
        image: Uploaded image file (from Streamlit file_uploader)
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Convert the uploaded file to PIL Image
        img = Image.open(io.BytesIO(image.read()))
        
        # Convert to grayscale for better OCR
        img = img.convert('L')
        
        # Perform OCR using Tesseract
        text = pytesseract.image_to_string(img)
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
