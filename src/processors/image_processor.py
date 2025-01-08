from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Define constants at module level
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

class ImageProcessor:
    def __init__(self):
        self.image = None

    def load_image(self, image_path):
        try:
            logger.debug(f"Loading image from {image_path}")
            self.image = Image.open(image_path)
            self.image = self.image.convert('RGB')  # Ensure RGB mode
            
            # Copy original to processed directory
            filename = Path(image_path).name
            processed_path = PROCESSED_DIR / filename
            logger.debug(f"Copying original to {processed_path}")
            shutil.copy2(image_path, processed_path)
            return True
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False

    def resize(self, width, height, method='lanczos'):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            self.image = self.image.resize((width, height), Image.Resampling.LANCZOS)
            return True
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return False

    def enhance(self, factor=1.5):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(factor)
            
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(factor)
            
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(factor)
            return True
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return False

    def denoise(self):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            self.image = self.image.filter(ImageFilter.MedianFilter(size=3))
            return True
        except Exception as e:
            logger.error(f"Error denoising image: {e}")
            return False

    def sharpen(self, factor=1.5):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            enhancer = ImageEnhance.Sharpness(self.image)
            self.image = enhancer.enhance(factor)
            return True
        except Exception as e:
            logger.error(f"Error sharpening image: {e}")
            return False

    def save_image(self, output_path):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            logger.debug(f"Saving image to {output_path}")
            self.image.save(output_path, format='JPEG', quality=95)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
