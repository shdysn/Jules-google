import unittest
from unittest.mock import patch
import io
import sys
from pathlib import Path
import urdu_ocr

from unittest.mock import MagicMock

class TestUrduOCR(unittest.TestCase):
    @patch('urdu_ocr.convert_from_path')
    def test_pdf_to_images(self, mock_convert_from_path):
        mock_convert_from_path.return_value = ['image1', 'image2']

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            images = urdu_ocr.pdf_to_images('dummy.pdf')

            self.assertEqual(images, ['image1', 'image2'])
            mock_convert_from_path.assert_called_once_with('dummy.pdf')
            output = mock_stdout.getvalue()
            self.assertIn("Converting dummy.pdf to images...", output)
            self.assertIn("Extracted 2 pages.", output)

    @patch('urdu_ocr.time.sleep')
    @patch('urdu_ocr.genai.GenerativeModel')
    def test_perform_ocr_on_images(self, mock_generative_model, mock_sleep):
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance

        # Simulate responses for two images
        mock_response_1 = MagicMock()
        mock_response_1.text = "text1"
        mock_response_2 = MagicMock()
        mock_response_2.text = "text2"
        mock_model_instance.generate_content.side_effect = [mock_response_1, mock_response_2]

        images = ['image1', 'image2']

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = urdu_ocr.perform_ocr_on_images(images)

            self.assertEqual(result, "text1\n\ntext2\n\n")

            mock_generative_model.assert_called_once_with('gemini-2.5-flash')
            self.assertEqual(mock_model_instance.generate_content.call_count, 2)

            prompt = "Extract all the text from this image. Only output the extracted text, do not include any other comments or Markdown formatting around the text."

            # Check generate_content arguments
            mock_model_instance.generate_content.assert_any_call([prompt, 'image1'])
            mock_model_instance.generate_content.assert_any_call([prompt, 'image2'])

            # Check rate limiting sleep
            mock_sleep.assert_called_once_with(2)

            output = mock_stdout.getvalue()
            self.assertIn("Performing OCR on images using Gemini...", output)
            self.assertIn("Processing page 1/2...", output)
            self.assertIn("Processing page 2/2...", output)

    @patch('urdu_ocr.genai.GenerativeModel')
    def test_proofread_urdu_text(self, mock_generative_model):
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance

        mock_response = MagicMock()
        mock_response.text = "clean_text"
        mock_model_instance.generate_content.return_value = mock_response

        raw_text = "raw_urdu_text"

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = urdu_ocr.proofread_urdu_text(raw_text)

            self.assertEqual(result, "clean_text")
            mock_generative_model.assert_called_once_with('gemini-2.5-flash')

            expected_prompt = (
                "You are an expert Urdu proofreader. Your task is to review the following "
                "raw Urdu text extracted via OCR. Please correct any spelling mistakes, fix "
                "broken Unicode, and adjust incorrect Urdu ligatures (like dots, Noon-Ghunna, "
                "or Hamza). Output only the final, clean, and properly formatted Urdu text. "
                "Do not include any English text, explanations, or extra commentary.\n\n"
                "Raw Text:\n"
                "raw_urdu_text"
            )
            mock_model_instance.generate_content.assert_called_once_with(expected_prompt)

            output = mock_stdout.getvalue()
            self.assertIn("Proofreading extracted Urdu text...", output)

    @patch('os.environ.get')
    def test_main_missing_api_key(self, mock_env_get):
        mock_env_get.return_value = None
        test_args = ['urdu_ocr.py', 'test.pdf']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                urdu_ocr.main()

                output = mock_stdout.getvalue()
                self.assertIn("Error: Gemini API key is required. Please provide it via --api-key or GEMINI_API_KEY environment variable.", output)

    @patch('urdu_ocr.Path.is_file')
    def test_main_missing_pdf_file(self, mock_is_file):
        mock_is_file.return_value = False
        test_args = ['urdu_ocr.py', 'nonexistent.pdf', '--api-key', 'test_key']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                urdu_ocr.main()

                output = mock_stdout.getvalue()
                self.assertIn("Error: Input file nonexistent.pdf not found.", output)

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

    @patch('urdu_ocr.genai.configure')
    @patch('urdu_ocr.pdf_to_images')
    @patch('urdu_ocr.perform_ocr_on_images')
    @patch('urdu_ocr.proofread_urdu_text')
    @patch('urdu_ocr.Path.is_file', return_value=True)
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_main_happy_path(self, mock_file_open, mock_is_file, mock_proofread, mock_perform_ocr, mock_pdf_to_images, mock_configure):
        mock_pdf_to_images.return_value = ['image1']
        mock_perform_ocr.return_value = "raw_extracted_text"
        mock_proofread.return_value = "clean_proofread_text"

        test_args = ['urdu_ocr.py', 'test.pdf', '--output', 'custom_output.md', '--api-key', 'test_key']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                urdu_ocr.main()

                mock_configure.assert_called_once_with(api_key='test_key')
                mock_pdf_to_images.assert_called_once_with('test.pdf')
                mock_perform_ocr.assert_called_once_with(['image1'])
                mock_proofread.assert_called_once_with("raw_extracted_text")

                # Verify file writes
                self.assertEqual(mock_file_open.call_count, 2)
                mock_file_open.assert_any_call("raw_output.txt", "w", encoding="utf-8")
                mock_file_open.assert_any_call("custom_output.md", "w", encoding="utf-8")

                # Check contents written
                handle = mock_file_open()
                handle.write.assert_any_call("raw_extracted_text")
                handle.write.assert_any_call("clean_proofread_text")

                output = mock_stdout.getvalue()
                self.assertIn("Saving raw text to raw_output.txt", output)
                self.assertIn("Saving final proofread text to custom_output.md", output)
                self.assertIn("Done!", output)

if __name__ == '__main__':
    unittest.main()
