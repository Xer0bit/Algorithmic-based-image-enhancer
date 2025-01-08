import unittest
from src.processors.image_processor import ImageProcessor
import os

class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.test_image_path = "test_image.jpg"
        self.output_path = "test_output.jpg"
        
        # Create a dummy test image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image_path)

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_load_and_save(self):
        self.assertTrue(self.processor.load_image(self.test_image_path))
        self.assertTrue(self.processor.save_image(self.output_path))

    def test_enhance(self):
        self.processor.load_image(self.test_image_path)
        self.assertTrue(self.processor.enhance(factor=1.5))

    def test_resize(self):
        self.processor.load_image(self.test_image_path)
        self.assertTrue(self.processor.resize(50, 50))

if __name__ == '__main__':
    unittest.main()

