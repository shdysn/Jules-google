import unittest
from unittest.mock import MagicMock
from urdu_ocr import perform_ocr_on_images
from PIL import Image

class TestUrduOCR(unittest.TestCase):
    def test_perform_ocr(self):
        images = [Image.new('RGB', (100, 100), color='white') for _ in range(3)]

        def mock_generate_content(args):
            mock_response = MagicMock()
            mock_response.text = f"Text for {args[0]}"
            return mock_response

        import urdu_ocr
        mock_model = MagicMock()
        mock_model.generate_content = mock_generate_content
        urdu_ocr.genai.GenerativeModel = MagicMock(return_value=mock_model)

        result = perform_ocr_on_images(images)
        self.assertIn("Text for Extract all the text", result)

if __name__ == '__main__':
    unittest.main()
