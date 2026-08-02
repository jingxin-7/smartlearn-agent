# SmartLearn Agent - Product Design

## User Stories

1. As a **student**, I want to **upload a PDF and ask questions about it**, so that **I can study more efficiently**.
2. As a **student**, I want to **get answers with page numbers**, so that **I can quickly find the original content in the PDF**.
3. As a **student**, I want to **ask follow-up questions in a conversation**, so that **I can deepen my understanding of a topic**.

## Feature List

| Priority | Feature | Day |
|----------|---------|-----|
| P0 | PDF text extraction | Day 2 |
| P0 | LLM Q&A with page citation | Day 2 |
| P1 | RAG pipeline (chunk + embed + search) | Day 3 |
| P1 | Web UI (FastAPI + React) | Day 3 |
| P2 | Chat history / multi-turn conversation | Day 3 |

## What We Will NOT Build

- User authentication / login — workshop time is limited
- Multi-file support — perfect the single-PDF experience first
- Mobile app — web version only

## Data Flow

### Day 2: Simple Mode

```
PDF File
  -> [PDF parser / extract text]      # pdfplumber reads each page
  -> pages[]                          # list of {page_number, text}
  -> [Build prompt: pages + question]  # combine extracted text with question
  -> [LLM]                            # send to OpenRouter
  -> Answer with [Page X]             # cited response returned to user
```

### Day 3: RAG Mode

```
PDF -> [extract text] -> pages
    -> [split into chunks] -> chunks with source_page
    -> [embed] -> embeddings
    -> [vector store (FAISS)]         # storage

Question -> [encode] -> [similarity search] -> relevant chunks -> [LLM] -> Answer
```
