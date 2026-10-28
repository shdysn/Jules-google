import time
from unittest.mock import MagicMock
from PIL import Image

# Create dummy images
images = [Image.new('RGB', (100, 100), color = 'white') for _ in range(5)]

def mock_generate_content(args):
    # Simulate realistic API latency
    time.sleep(5)
    mock_response = MagicMock()
    mock_response.text = "Dummy text"
    return mock_response

# Monkeypatch
import urdu_ocr
mock_model = MagicMock()
mock_model.generate_content = mock_generate_content
urdu_ocr.genai.GenerativeModel = MagicMock(return_value=mock_model)

from urdu_ocr import perform_ocr_on_images

start_time = time.time()
perform_ocr_on_images(images)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
