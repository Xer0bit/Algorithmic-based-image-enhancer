from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from processors.image_processor import ImageProcessor, UPLOAD_DIR, PROCESSED_DIR

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Ensure directories exist and are empty at startup
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

app.mount("/processed", StaticFiles(directory=str(PROCESSED_DIR)), name="processed")

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Enhancer</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { display: flex; gap: 20px; margin-top: 20px; }
            .image-container { flex: 1; }
            img { max-width: 100%; height: auto; }
            .form-group { margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h1>Image Enhancer</h1>
        <form action="/enhance/" enctype="multipart/form-data" method="post">
            <div class="form-group">
                <label>Select Image: </label>
                <input type="file" name="file" accept="image/*" required>
            </div>
            <div class="form-group">
                <label>Enhancement Factor: </label>
                <input type="number" name="factor" value="1.3" step="0.1" min="0.1" max="3.0">
            </div>
            <div class="form-group">
                <button type="submit">Enhance Image</button>
            </div>
        </form>
        <div id="result"></div>
        <div class="container" id="imageContainer" style="display: none;">
            <div class="image-container">
                <h3>Original Image</h3>
                <img id="original" src="">
            </div>
            <div class="image-container">
                <h3>Enhanced Image</h3>
                <img id="enhanced" src="">
            </div>
        </div>
        <script>
            document.querySelector('form').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                
                try {
                    const response = await fetch('/enhance/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('imageContainer').style.display = 'flex';
                        document.getElementById('original').src = data.original_url;
                        document.getElementById('enhanced').src = data.enhanced_url;
                        document.getElementById('result').innerHTML = '<p style="color: green;">Image enhanced successfully!</p>';
                    } else {
                        document.getElementById('result').innerHTML = '<p style="color: red;">Error processing image</p>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = '<p style="color: red;">Error processing image</p>';
                }
            };
        </script>
    </body>
    </html>
    """

@app.post("/enhance/")
async def enhance_image(file: UploadFile = File(...), factor: float = 1.3):
    try:
        # Ensure filename is safe
        safe_filename = Path(file.filename).name
        file_path = UPLOAD_DIR / safe_filename
        
        logger.debug(f"Saving uploaded file to {file_path}")
        
        # Save uploaded file
        try:
            with file_path.open("wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise HTTPException(status_code=400, detail="Failed to save uploaded file")

        # Process image
        processor = ImageProcessor()
        logger.debug("Loading image into processor")
        
        if not processor.load_image(str(file_path)):
            logger.error("Failed to load image into processor")
            raise HTTPException(status_code=400, detail="Failed to load image")

        # Apply enhancements
        logger.debug("Applying enhancements")
        processor.denoise()
        processor.enhance(factor=factor)
        processor.sharpen(factor=1.2)

        # Save processed image
        output_filename = f"enhanced_{safe_filename}"
        output_path = PROCESSED_DIR / output_filename
        
        logger.debug(f"Saving enhanced image to {output_path}")
        if not processor.save_image(str(output_path)):
            logger.error("Failed to save enhanced image")
            raise HTTPException(status_code=500, detail="Failed to save enhanced image")

        return {
            "success": True,
            "original_url": f"/processed/{safe_filename}",
            "enhanced_url": f"/processed/{output_filename}",
        }

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

