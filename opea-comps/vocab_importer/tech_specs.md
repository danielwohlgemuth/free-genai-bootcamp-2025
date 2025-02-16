# Japanese Language Vocabulary Importer

## Business Goal

The purpose of this app is to generate a list of Japanese words together with their romanji representation and English translation based on a topic provided by the user.

## Technical Requirements

- Streamlit app that connects to a backend service to generate the words
- Docker compose file to run the app
- Backend service URL configurable via environment variable `BACKEND_SERVICE_URL` (default: http://0.0.0.0:8888)

## Functional Requirements

### User Interface

1. Topic Input
   - Text input field with 50 character limit
   - Placeholder text with example topics (e.g., "Basic Greetings", "Food and Drinks", "Weather")
   - Visual indicator when character limit is reached

2. Word Count Control
   - Slider control for number of words to generate
   - Range: 3-10 words
   - Default: 5 words

3. Generate Button
   - Triggers backend request
   - Disabled during API calls
   - Loading indicator while waiting for response

4. Results Display
   - Primary view: Card-based display for each word
     - Each card shows: Japanese text, romaji, English translation, and parts information
   - Secondary view: Collapsible raw JSON view
     - Copy to clipboard button
     - Initially collapsed

5. Theme Toggle
   - Dark/light mode switch
   - Persists user preference

6. Responsive Design
   - Adapts to different screen sizes
   - Card layout adjusts based on viewport width

### Error Handling

The app should handle and display user-friendly messages for:
- Backend service unavailable
- Rate limiting errors
- Invalid responses from backend
- Input validation errors

### API Integration

Backend Request:
```json
{
    "topic": "string",  // User provided topic
    "word_count": number  // User selected count (3-10)
}
```

Backend Response:
```json
{
    "group_name": "string",
    "words": [
        {
            "japanese": "string",
            "romaji": "string",
            "english": "string",
            "parts": {
                "type": "string",
                "formality": "string"
            }
        }
    ]
}
```

## Non-Functional Requirements

1. Performance
   - Responsive UI during API calls
   - Smooth animations for collapsible elements and theme changes

2. Error Recovery
   - Clear error messages
   - Ability to retry failed requests
   - Maintain form state during errors

3. Configuration
   - Environment variable for backend service URL
   - Default configuration suitable for local development
