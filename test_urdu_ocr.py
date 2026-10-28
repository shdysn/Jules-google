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

    @patch('urdu_ocr.genai.GenerativeModel')
    def test_proofread_urdu_text(self, mock_generative_model):
        # Arrange
        mock_model_instance = mock_generative_model.return_value
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.text = "Clean Urdu Text"
        mock_model_instance.generate_content.return_value = mock_response

        raw_text = "Raw Urdu Text"

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = urdu_ocr.proofread_urdu_text(raw_text)

            # Assert
            output = mock_stdout.getvalue()
            self.assertIn("Proofreading extracted Urdu text...", output)

        self.assertEqual(result, "Clean Urdu Text")
        mock_generative_model.assert_called_once_with('gemini-2.5-flash')

        expected_prompt = (
            "You are an expert Urdu proofreader. Your task is to review the following "
            "raw Urdu text extracted via OCR. Please correct any spelling mistakes, fix "
            "broken Unicode, and adjust incorrect Urdu ligatures (like dots, Noon-Ghunna, "
            "or Hamza). Output only the final, clean, and properly formatted Urdu text. "
            "Do not include any English text, explanations, or extra commentary.\n\n"
            "Raw Text:\n"
            f"{raw_text}"
        )
        mock_model_instance.generate_content.assert_called_once_with(expected_prompt)

if __name__ == '__main__':
    unittest.main()
