import unittest
from unittest.mock import patch
import io
import sys
from pathlib import Path
import urdu_ocr

class TestUrduOCR(unittest.TestCase):
    @patch('urdu_ocr.pdf_to_images')
    @patch('urdu_ocr.Path.is_file', return_value=True)
    def test_main_error_handling(self, mock_is_file, mock_pdf_to_images):
        # Mock pdf_to_images to raise an Exception
        test_error_message = "Test exception during PDF processing"
        mock_pdf_to_images.side_effect = Exception(test_error_message)

        # Set up sys.argv and environment variables to bypass initial checks
        test_args = ['urdu_ocr.py', 'test.pdf', '--api-key', 'test_key']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                urdu_ocr.main()

                output = mock_stdout.getvalue()
                self.assertIn(f"An error occurred: {test_error_message}", output)

if __name__ == '__main__':
    unittest.main()
