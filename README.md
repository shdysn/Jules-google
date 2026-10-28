# Urdu PDF OCR and Proofreader

This script takes a multi-page scanned Urdu PDF book, converts each page into an image, and uses the `gemini-2.5-flash` model to perform OCR. It then passes the full raw text back to Gemini to act as an expert Urdu proofreader, correcting spelling mistakes, fixing broken Unicode, and adjusting incorrect Urdu ligatures, before outputting the clean text into a final formatted Markdown/Text file.

## Requirements

1. **Python Dependencies:** Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **System Dependencies (`poppler`):**
   The `pdf2image` library requires `poppler` to be installed on your system.
   - **Ubuntu/Debian:** `sudo apt-get install poppler-utils`
   - **macOS:** `brew install poppler`
   - **Windows:** Download the latest poppler binaries, extract them, and add the `bin/` directory to your system's PATH.

3. **Google Gemini API Key:**
   You will need a Google Gemini API key. You can get one from Google AI Studio.

## Usage

You can run the script from the command line:

```bash
python urdu_ocr.py path/to/your/document.pdf --api-key YOUR_GEMINI_API_KEY --output final_result.md
```

### Arguments:
- `pdf_path`: The path to the input PDF file (positional argument).
- `--output`: Optional. The path to save the final cleaned text. Defaults to `output.md`.
- `--api-key`: Optional. Your Google Gemini API Key. If not provided here, you must set it in the `GEMINI_API_KEY` environment variable.

Example using environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"
python urdu_ocr.py sample.pdf --output cleaned_book.md
```
