# Agent Workflow

## Multi-Agent Reasoning Pipeline

The system uses 5 sequential agents to process each query:

```
User Query
    │
    ▼
┌─────────────┐   Analyzes question, identifies key topics,
│   PLANNER   │   generates 1-3 focused search queries
│             │   Output: {queries, strategy, focus_areas}
└──────┬──────┘
       │
       ▼
┌─────────────┐   Executes each planned query against ChromaDB,
│  RETRIEVER  │   deduplicates results, returns top-K chunks
│             │   Output: [ranked relevant chunks]
└──────┬──────┘
       │
       ▼
┌─────────────┐   Identifies most relevant info, extracts key facts,
│  REASONING  │   notes contradictions/gaps, synthesizes analysis
│             │   Output: structured analysis text
└──────┬──────┘
       │
       ▼
┌─────────────┐   Generates answer ONLY from provided info,
│  RESPONSE   │   cites sources with [Source N] notation,
│             │   uses markdown formatting
└──────┬──────┘   Output: final answer text
       │
       ▼
┌─────────────┐   Checks if answer is grounded in sources,
│ VERIFICATION│   returns confidence score (0-1),
│             │   flags unsupported claims
└──────┬──────┘   Output: {grounded, confidence, issues}
       │
       ▼
  Final Answer
  (with disclaimer if not fully grounded)
```

## Agent Details

### Planner Agent
- **LLM**: Gemini 2.5 Flash (temperature: 0.3)
- **Tools**: None (pure reasoning)
- **Input**: User question + document IDs
- **Output**: JSON with search queries and strategy

### Retriever Agent
- **LLM**: Not used directly
- **Tools**: `search_knowledge_base` (ChromaDB vector search)
- **Input**: Retrieval plan from Planner
- **Output**: Deduplicated, ranked document chunks

### Reasoning Agent
- **LLM**: Gemini 2.5 Flash (temperature: 0.3)
- **Tools**: None (analysis only)
- **Input**: User question + retrieved chunks
- **Output**: Structured analysis with source references

### Response Agent
- **LLM**: Gemini 2.5 Flash (temperature: 0.5)
- **Tools**: None
- **Input**: Question + analysis + source list
- **Output**: Final markdown answer with citations

### Verification Agent
- **LLM**: Gemini 2.5 Flash (temperature: 0.1)
- **Tools**: None
- **Input**: Generated answer + source chunks
- **Output**: JSON grounding assessment

## Fallback Behavior

If the agent pipeline fails (e.g., rate limit), the system falls back to
direct RAG: embed query → retrieve chunks → augment prompt → stream from Gemini.
