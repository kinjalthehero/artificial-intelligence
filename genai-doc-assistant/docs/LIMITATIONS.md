# Limitations, Assumptions & Security

## Limitations

- **Rate Limiting**: Gemini free tier allows 15 requests per minute. The 5-agent pipeline uses ~5 API calls per query, limiting throughput to ~3 queries/minute.
- **Cold Start**: Render.com free tier sleeps after 15 minutes of inactivity. First request takes 30-60 seconds to wake up.
- **Memory**: Render free tier provides 512 MB RAM. Large documents or many concurrent users may cause issues.
- **File Size**: Maximum upload size is 10 MB per file.
- **No Authentication**: The application is a public demo with no user authentication or data isolation.
- **Embedding Dimensions**: Uses Gemini text-embedding-004 (768 dimensions). Not all document types produce equally good embeddings.
- **ChromaDB Scalability**: Embedded ChromaDB is not horizontally scalable. Suitable for demo/small-scale use.
- **No Real-Time Collaboration**: Single-user experience per session.

## Assumptions

- Users have a valid Google API key with access to Gemini 2.5 Flash.
- Documents are in the supported formats and contain extractable text (scanned PDFs without OCR are not supported).
- The Gemini API is available and responsive.
- Users understand that AI-generated responses may not be 100% accurate.
- The vector store data is ephemeral on free hosting (lost on redeploy).

## Security Considerations

- **API Key Management**: The Google API key is stored as an environment variable, never committed to code. The `.env.example` file documents required variables.
- **Input Validation**: All uploads are validated for file type (whitelist), file size (10 MB max), and content type. Query length is capped at 2000 characters.
- **Output Verification**: The Verification Agent checks that responses are grounded in source documents, reducing hallucination risk.
- **No Code Execution**: The system does not execute any code from uploaded documents.
- **CORS**: Cross-origin requests are restricted to configured origins.
- **SQL Injection**: All database queries use parameterized statements via aiosqlite.
- **Error Handling**: Global exception handler prevents stack trace leakage to clients.
- **Structured Logging**: All operations are logged with structlog for audit trail.
- **Rate Limiting**: Built-in sliding window rate limiter prevents Gemini API abuse.
- **No PII Storage**: The system does not collect or store personal information beyond uploaded documents and chat history, which are stored locally in SQLite.
