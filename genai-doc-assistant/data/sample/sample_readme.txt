GenAI Document Assistant - Technical Overview
=============================================

Introduction
------------
The GenAI Document Assistant is an AI-powered application that enables users
to upload documents in multiple formats and ask natural language questions
about their content. The system uses a Retrieval-Augmented Generation (RAG)
pipeline combined with a multi-agent reasoning architecture to provide
accurate, grounded responses with source citations.

How It Works
-----------
1. Document Upload: Users upload files through the web interface or REST API.
   Supported formats include PDF, TXT, CSV, Excel, JSON, and YAML.

2. Text Extraction: Each document is parsed using format-specific extractors.
   PDFs use PyPDF2 for page-by-page extraction. CSV and Excel files are
   converted to markdown tables using pandas. JSON and YAML files are
   pretty-printed for readability.

3. Chunking: Extracted text is split into overlapping chunks using LlamaIndex's
   SentenceSplitter, which respects sentence boundaries to maintain context.
   Default chunk size is 512 tokens with 50-token overlap.

4. Embedding: Each chunk is converted to a 768-dimensional vector using
   Google's gemini-embedding-001 model. These embeddings capture the semantic
   meaning of each text segment.

5. Storage: Embeddings are stored in ChromaDB, a persistent vector database.
   Each document gets its own collection for isolation and easy cleanup.

6. Query Processing: When a user asks a question, the system uses a
   multi-agent pipeline:

   a) Planner Agent: Analyzes the question and creates a retrieval strategy
      with focused search queries.

   b) Retriever Agent: Executes the planned queries against the vector store,
      finding the most relevant document chunks via cosine similarity.

   c) Reasoning Agent: Analyzes the retrieved chunks, identifies key facts,
      notes contradictions or gaps, and synthesizes a structured analysis.

   d) Response Agent: Generates a clear, well-structured answer using only
      the information from the analysis, with [Source N] citations.

   e) Verification Agent: Checks that the final response is grounded in
      the source documents and flags any unsupported claims.

7. Streaming Response: The final answer is streamed to the user in real-time
   via Server-Sent Events (SSE), with agent progress updates shown in the UI.

Technology Stack
---------------
- Frontend: React 19, TypeScript, Vite, Tailwind CSS 4
- Backend: FastAPI, Python 3.11, SQLite, ChromaDB
- AI/ML: Google Gemini 2.5 Flash, LlamaIndex, gemini-embedding-001
- Deployment: Docker, Render.com (free tier)

Security Considerations
----------------------
- File upload validation: type whitelist, size limits (10 MB max)
- Query length validation: 2000 character maximum
- No user authentication (public demo)
- API keys stored as environment variables, never in code
- Rate limiting to stay within Gemini free tier (15 RPM)
- Output verification agent to reduce hallucination
