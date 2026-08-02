# ============================================================
# pdf_summary.py - PDF Summary Tool with Page Citations
# ============================================================
# Reads a PDF file, extracts text, and sends it to an LLM
# to produce a structured summary with [Page X] citations.
# ============================================================

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file, page by page.
    Returns: list of dicts with 'page_number' and 'text' keys.
    """
    try:
        import pdfplumber
    except ImportError:
        raise SystemExit(
            "pdfplumber is not installed. Run: pip install pdfplumber"
        )

    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    pages.append({"page_number": i, "text": text.strip()})
                print(f"Extracting page {i}/{total}...")
    except Exception as e:
        raise SystemExit(f"Failed to read PDF: {e}")

    return pages


MAX_CHARS = 100_000


def build_numbered_text(pages):
    """
    Combine extracted pages into a single numbered text for the LLM prompt.
    Truncates and warns if the total exceeds MAX_CHARS characters.
    Returns: (numbered_text, was_truncated)
    """
    blocks = []
    total_chars = 0
    truncated = False

    for page in pages:
        page_block = f"[Page {page['page_number']}]\n{page['text']}"
        # +2 for the "\n\n" separator that will be added
        if total_chars + len(page_block) > MAX_CHARS:
            truncated = True
            break
        blocks.append(page_block)
        total_chars += len(page_block) + 2

    if blocks:
        return "\n\n".join(blocks), truncated
    return "", False


def ask_llm(numbered_text, was_truncated=False):
    """
    Send the extracted text to the LLM and return the structured summary.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is missing. Add it to .env and try again.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = """You are a precise research assistant. Summarize the provided document.

Rules:
1. Write a short Overview (2-3 sentences) covering the main topic.
2. List 3-5 Key Points using bullet points (start each with "- "). Every bullet must end with the page citation in brackets, like this: [Page X].
3. Write a Limitations section noting what the summary may miss.
4. Format your output with these exact headings: ## Overview, ## Key Points, ## Limitations
5. Do NOT add information beyond what is in the text.

Example format:
## Overview
Brief summary here.

## Key Points
- First key point with supporting detail [Page 1].
- Second key point with supporting detail [Page 2].

## Limitations
- Limitation noted here.
"""

    user_prompt = f"""Here is the document text:

{numbered_text}

Please provide the structured summary."""

    if was_truncated:
        user_prompt += (
            "\n\n[WARNING: This document was too long and has been truncated at "
            f"approximately {MAX_CHARS:,} characters. Only the beginning of the "
            "document is shown above. In your Limitations section, mention that "
            "your summary only covers the early pages and the rest of the "
            "document was not analyzed.]"
        )

    try:
        response = client.chat.completions.create(
            model="google/gemma-4-26b-a4b-it:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        if not response.choices:
            return (
                "ERROR: The API returned an empty response. "
                "This may be a temporary server issue. Please try again."
            )

        return response.choices[0].message.content

    except Exception as e:
        print(f"API call failed: {e}")
        return (
            f"ERROR: The API call failed — {e}\n\n"
            "Check that your OPENROUTER_API_KEY is valid in .env "
            "and that you have an internet connection."
        )


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 pdf_summary.py <path-to-pdf>")

    pdf_path = sys.argv[1]

    if not os.path.isfile(pdf_path):
        raise SystemExit(f"File not found: {pdf_path}")

    # Step 1: Extract text from PDF
    pages = extract_text_from_pdf(pdf_path)

    if not pages:
        raise SystemExit(
            "No extractable text found in this PDF. "
            "It may be a scanned document or contain only images. "
            "Try a PDF with selectable text."
        )

    print(f"\nExtracted text from {len(pages)} page(s).\n")

    # Step 2: Build the numbered text (with truncation safeguard)
    numbered_text, was_truncated = build_numbered_text(pages)
    if was_truncated:
        print(f"Warning: Text exceeds {MAX_CHARS:,} characters. "
              "Only the beginning of the document will be summarized.\n")

    # Step 3: Call the LLM
    print("Generating summary...\n")
    summary = ask_llm(numbered_text, was_truncated)

    # Step 4: Print the result
    print(summary)


if __name__ == "__main__":
    main()
