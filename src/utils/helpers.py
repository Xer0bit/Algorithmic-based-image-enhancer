def load_image(image_path):
    """Load an image from the specified path."""
    from PIL import Image
    return Image.open(image_path)

def save_image(image, save_path):
    """Save the processed image to the specified path."""
    image.save(save_path)

def display_image(image):
    """Display the image using the default image viewer."""
    image.show()