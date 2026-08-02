# CLI Q&A Tool - PRD (Product Requirements Document)

## What it does
A command-line tool that takes a multi-paragraph text and a question,
then uses an LLM to answer the question with paragraph-level citations.

## Input
1. Multi-line text from user (terminated by typing 'END' on a new line)
   OR a text file via --file flag
2. One or more questions about the text

## Output
Answers that reference specific paragraphs using [Paragraph X] format.

## Done when / acceptance tests
- User can paste text or load from file
- Answers include [Paragraph X] citations
- Supports multiple questions in one session
- Uses OpenRouter API (google/gemma-4-31b-it:free model)
- API key loaded from .env file and never printed
- Empty text exits with a friendly error before any API call
- Missing answers return exactly: The text does not provide this information.
- python3 -m py_compile cli_qa.py succeeds
