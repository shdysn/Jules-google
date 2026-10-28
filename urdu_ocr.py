import argparse
import os
import time
from pathlib import Path
from pdf2image import convert_from_path
import google.generativeai as genai

def pdf_to_images(pdf_path: str):
    """
    Converts a multi-page PDF into a list of PIL Image objects.
    """
    print(f"Converting {pdf_path} to images...")
    images = convert_from_path(pdf_path)
    print(f"Extracted {len(images)} pages.")
    return images

def perform_ocr_on_images(images):
    """
    Extracts raw text from a list of images using Gemini 2.5 Flash model.
    """
    print("Performing OCR on images using Gemini...")
    model = genai.GenerativeModel('gemini-2.5-flash')

    full_text = ""
    for i, image in enumerate(images):
        print(f"Processing page {i + 1}/{len(images)}...")
        prompt = "Extract all the text from this image. Only output the extracted text, do not include any other comments or Markdown formatting around the text."
        response = model.generate_content([prompt, image])
        full_text += response.text + "\n\n"
        # Avoid hitting API rate limits
        if i < len(images) - 1:
            time.sleep(2)

    return full_text

def proofread_urdu_text(raw_text: str) -> str:
    """
    Passes raw Urdu text to Gemini 2.5 Flash to act as an expert proofreader.
    Corrects spelling, Unicode, and ligatures.
    """
    print("Proofreading extracted Urdu text...")
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = (
        "You are an expert Urdu proofreader. Your task is to review the following "
        "raw Urdu text extracted via OCR. Please correct any spelling mistakes, fix "
        "broken Unicode, and adjust incorrect Urdu ligatures (like dots, Noon-Ghunna, "
        "or Hamza). Output only the final, clean, and properly formatted Urdu text. "
        "Do not include any English text, explanations, or extra commentary.\n\n"
        "Raw Text:\n"
        f"{raw_text}"
    )

    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Convert Urdu PDF to clean text using Gemini 2.5 Flash OCR and proofreading.")
    parser.add_argument("pdf_path", type=str, help="Path to the input PDF file")
    parser.add_argument("--output", type=str, default="output.md", help="Path to the output Markdown/Text file (default: output.md)")
    parser.add_argument("--api-key", type=str, help="Google Gemini API Key. Alternatively, set GEMINI_API_KEY environment variable.")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key is required. Please provide it via --api-key or GEMINI_API_KEY environment variable.")
        return

    if not Path(args.pdf_path).is_file():
        print(f"Error: Input file {args.pdf_path} not found.")
        return

    genai.configure(api_key=api_key)

    try:
        images = pdf_to_images(args.pdf_path)
        raw_text = perform_ocr_on_images(images)

        print("Saving raw text to raw_output.txt (for debugging/reference)...")
        with open("raw_output.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)

        clean_text = proofread_urdu_text(raw_text)

        print(f"Saving final proofread text to {args.output}...")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(clean_text)

        print("Done!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
