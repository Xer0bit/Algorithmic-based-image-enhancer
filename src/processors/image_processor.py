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
        self.interpolation_methods = {
            'nearest': Image.Resampling.NEAREST,
            'box': Image.Resampling.BOX,
            'bilinear': Image.Resampling.BILINEAR,
            'hamming': Image.Resampling.HAMMING,
            'bicubic': Image.Resampling.BICUBIC,
            'lanczos': Image.Resampling.LANCZOS
        }

    def load_image(self, image_path):
        try:
            logger.debug(f"Loading image from {image_path}")
            self.image = Image.open(image_path)
            
            # Handle different image modes
            if self.image.mode not in ['RGB', 'L']:
                self.image = self.image.convert('RGB')
            
            # Validate image dimensions
            if self.image.size[0] * self.image.size[1] == 0:
                raise ValueError("Invalid image dimensions")
                
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
            # Validate dimensions
            if width <= 0 or height <= 0:
                raise ValueError("Invalid dimensions")
                
            # Use safer interpolation method
            interp_method = self.interpolation_methods.get(method.lower(), Image.Resampling.LANCZOS)
            self.image = self.image.resize((width, height), interp_method)
            return True
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return False

    def enhance(self, factor=1.5):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            # Clamp enhancement factor to safe range
            safe_factor = max(0.1, min(2.5, factor))
            
            # Apply enhancements with error checking
            for enhancer_class in [ImageEnhance.Contrast, ImageEnhance.Brightness, ImageEnhance.Color]:
                try:
                    enhancer = enhancer_class(self.image)
                    self.image = enhancer.enhance(safe_factor)
                except Exception as e:
                    logger.warning(f"Skipping {enhancer_class.__name__} enhancement: {e}")
                    continue
            
            return True
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return False

    def denoise(self):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            # Use a more robust denoising approach
            self.image = self.image.filter(ImageFilter.MedianFilter(size=3))
            self.image = self.image.filter(ImageFilter.GaussianBlur(radius=0.5))
            return True
        except Exception as e:
            logger.error(f"Error denoising image: {e}")
            return False

    def sharpen(self, factor=1.5):
        if self.image is None:
            logger.error("No image loaded")
            return False
        try:
            # Clamp sharpening factor
            safe_factor = max(0.1, min(2.0, factor))
            
            # Apply custom sharpening kernel for better results
            if safe_factor > 1.0:
                self.image = self.image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            enhancer = ImageEnhance.Sharpness(self.image)
            self.image = enhancer.enhance(safe_factor)
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
