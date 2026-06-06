# Limitations, Assumptions & Security

## Limitations

- **Gemini API Quotas**: Using Gemini paid tier with daily request quotas set in Google Cloud Console (1,500 requests/day, 30 RPM) to cap costs at ~$5/month. The 5-agent pipeline uses ~5 API calls per query.
- **Per-IP Rate Limiting**: Each visitor is limited to 30 chat queries/hour and 10 document uploads/hour to prevent abuse.
- **Cold Start (Render)**: Render.com free tier sleeps after 15 minutes of inactivity. First request takes 30-60 seconds. The app shows a "Waking up the server" loading screen.
- **Memory**: Render free tier provides 512 MB RAM. EC2 t3.micro provides 1 GB. Large documents or many concurrent users may cause issues.
- **File Size**: Maximum upload size is 10 MB per file.
- **No Authentication**: The application is a public demo with no user authentication or data isolation.
- **Embedding Dimensions**: Uses Gemini embedding-001 (3072 dimensions). Not all document types produce equally good embeddings.
- **ChromaDB Scalability**: Embedded ChromaDB is not horizontally scalable. Suitable for demo/small-scale use.
- **No Real-Time Collaboration**: Single-user experience per session.

## Assumptions

- Users have a valid Google API key with access to Gemini 2.5 Flash.
- Documents are in the supported formats and contain extractable text (scanned PDFs without OCR are not supported).
- The Gemini API is available and responsive.
- Users understand that AI-generated responses may not be 100% accurate.
- The vector store data is ephemeral on free hosting (lost on redeploy for Render; persistent with Docker volumes on EC2).

## Security Considerations

- **API Key Management**: The Google API key is stored as an environment variable, never committed to code. The `.env.example` file documents required variables.
- **Input Validation**: All uploads are validated for file type (whitelist), file size (10 MB max), and content type. Query length is capped at 2000 characters.
- **Per-IP Rate Limiting**: Chat and upload endpoints enforce per-IP rate limits (30 chats/hour, 10 uploads/hour) to prevent API abuse from individual visitors.
- **Output Verification**: The Verification Agent checks that responses are grounded in source documents, reducing hallucination risk.
- **No Code Execution**: The system does not execute any code from uploaded documents.
- **CORS**: Cross-origin requests are restricted to configured origins. Production URLs added via `EXTRA_CORS_ORIGINS` env var.
- **SQL Injection**: All database queries use parameterized statements via aiosqlite.
- **Error Handling**: Global exception handler prevents stack trace leakage to clients.
- **Structured Logging**: All operations are logged with structlog for audit trail.
- **Cost Protection**: Google Cloud quotas cap daily API usage. AWS Budget alerts warn at $1 threshold.
- **No PII Storage**: The system does not collect or store personal information beyond uploaded documents and chat history, which are stored locally in SQLite.

## Deployment Options

| Platform | Cost | Persistence | Cold Start |
|----------|------|-------------|------------|
| Render.com (free) | $0 | Ephemeral (lost on redeploy) | 30-60s after 15 min idle |
| AWS EC2 (free tier) | $0 for 12 months | Persistent (Docker volumes) | None (always running) |

## Cost Breakdown

| Service | Provider | Monthly Cost |
|---------|----------|-------------|
| Gemini API | Google Cloud | $0.50 - $5 (capped by quotas) |
| EC2 t3.micro | AWS | $0 (free tier, 12 months) |
| Render | Render.com | $0 (free tier) |
| **Total** | | **$0.50 - $5/month** |
