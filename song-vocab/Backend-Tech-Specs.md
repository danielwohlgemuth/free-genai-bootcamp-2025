# Japanese Song Vocabulary Extractor - Backend Technical Specifications

## System Overview
A backend service that extracts and translates key vocabulary from Japanese song lyrics. The service uses an LLM-driven agentic workflow to process requests and coordinate various tools for searching, extracting, and analyzing lyrics.

## API Specification

### Endpoint
- **URL**: `/extract_vocabulary`
- **Method**: POST
- **Authentication**: None required
- **Rate Limiting**: None implemented

### Request Format
```json
{
    "query": "Song name"
}
```

### Success Response
```json
{
    "group_name": "Song name",
    "words": [{
        "japanese": "Japanese letters",
        "romaji": "Romanji letters",
        "english": "English letters",
        "parts": {
            "type": "Type",
            "formality": "Formality"
        }
    }]
}
```

### Error Response
```json
{
    "error": "Error message"
}
```

## Technical Architecture

### Core Components
1. **LLM Agent Workflow**
   - Uses LangChain for agent orchestration
   - ReAct agent pattern for tool selection and execution
   - LLM determines least common words based on context.
     The LLM will be available at `http://localhost:11434` and should be configurable through env vars.

2. **Lyrics Processing Pipeline**
   - Search includes "japanese lyrics" in query terms
   - No distinction between kanji, hiragana, and katakana processing
   - No specific website targeting for lyrics sources

3. **Tools**
   - Link retriever: DuckDuckGo Search
   - Lyrics retriever: Web scraping using BeautifulSoup4
   - Lyrics extractor: LLM (qwen2.5:3b model)
   - Vocabulary extractor: LLM (qwen2.5:3b model)
   - Vocabulary filter: Reduce to the 3 - 10 least common words using LLM (qwen2.5:3b model)
   - Vocabulary enhancer: Add Romanji and English representation using LLM (qwen2.5:3b model)

### Tech Stack
- Ollama (qwen2.5:3b model)
- LangChain for agent workflow
- Python
- DuckDuckGo Search API for lyrics discovery
- BeautifulSoup4 for web scraping
- FastAPI for API endpoint

### Infrastructure
- Deployment: Docker-based
- No specific performance requirements
- No caching implementation
- Basic logging only
- No additional security measures beyond standard API practices

## Development References

### LangChain Integration
- Web Scraping: `langchain_community.document_loaders.WebBaseLoader` with BeautifulSoup4
- Agent Creation: `langgraph.prebuilt.chat_agent_executor.create_react_agent`

## Implementation Notes
- Single endpoint design
- Agentic workflow where LLM coordinates tool usage
- Error handling for non-found songs
- No specific response time requirements
- Designed for low-volume usage
