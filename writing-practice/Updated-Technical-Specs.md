# Kana Writing Practice Application - Updated Technical Specification

## System Architecture

### Components
1. **Frontend (Gradio Interface)**
   - User interface for word group selection
   - Canvas/file upload for kana writing
   - Audio playback interface
   - Validation result display
   - Word regeneration functionality

2. **Backend Integration**
   - Configurable backend URL (default: localhost:8000)
   - Word group retrieval endpoint integration
   - Word list retrieval endpoint integration

3. **AWS Services**
   - AWS Bedrock: Kana representation generation
   - Amazon Polly: Japanese word audio synthesis

4. **OCR Integration**
   - manga_ocr package for kana validation

### Data Flow
1. Application startup:
   - Load backend URL from environment variables (BACKEND_URL)
   - Fetch available word groups from /api/groups

2. Word group selection:
   - User selects word group from dropdown
   - Fetch words for selected group from /api/groups/{groupId}/words
   - Randomly select one word from the group

3. Word processing:
   - Display English translation
   - Generate kana representation using AWS Bedrock
   - Generate audio using Amazon Polly

4. User input:
   - Primary: Canvas drawing interface
   - Alternative: Image file upload (pictures only)
   - Submit button to trigger validation

5. Validation process:
   - Process user input (canvas/image) with manga_ocr
   - Compare OCR result with Bedrock-generated kana
   - Display success/retry message
   - Option to generate new word from same group

## Technical Requirements

### Development Stack
- Python 3.9+
- Gradio for UI
- manga_ocr package
- AWS SDK (boto3) for Bedrock and Polly integration
- Environment variable support

### API Integration
#### Endpoints
1. GET /api/groups
   - Response: {"items": [{"id": groupId, "name": groupName}]}
   - Used for initial word group loading

2. GET /api/groups/{groupId}/words
   - Response: {"items": [{"japanese": japanese, "english": english}]}
   - Used for word retrieval after group selection

### User Interface Requirements
1. Word Group Selection
   - Dropdown populated from /api/groups endpoint
   - Automatic word fetch on selection

2. Writing Input
   - Primary: Drawing canvas
   - Secondary: File upload input
   - File type restriction to images
   - Automatic fallback to canvas if no file

3. Audio Playback
   - Play button for Polly-generated audio
   - Replay functionality

4. Validation
   - Submit button for OCR processing
   - Clear success/failure feedback
   - "Try Again" option for failures
   - "Next Word" button for new word from same group

## Questions for Clarification:

### User Interface
1. Should there be a specific size/dimension requirement for the drawing canvas? What is the optimal size for kana character input?
2. Should we provide grid lines or guide marks on the canvas to help with character alignment and sizing?
3. Should we support multi-character input on a single canvas, or one character at a time?
4. Should there be an "undo" or "clear" function for the drawing canvas?
5. Should we show a reference image of the correct kana while the user is drawing?

### File Upload
6. What file formats should be accepted for image upload (jpg, png, etc.)?
7. Should there be a maximum file size limit for uploads?
8. Should we support batch upload of multiple character images?
9. Should we provide image preprocessing (e.g., contrast enhancement, background removal) before OCR?

### Audio Features
10. Should the audio playback support speed adjustment?
11. Should we cache audio files for frequently used words?
12. Should we provide a visual waveform or progress indicator during playback?
13. Should we support automatic audio playback when a new word is generated?

### Validation and Learning
14. What should be the exact criteria for matching kana (exact match, fuzzy match)?
15. Should we implement a confidence score for OCR matching?
16. Should there be a limit to the number of retry attempts?
17. Should we track and display the user's success rate for different kana?
18. Should successful attempts be tracked or stored for progress tracking?

### Performance and Storage
19. Should the application support offline mode with cached word groups?
20. Should we implement rate limiting for API calls to Bedrock and Polly?
21. Should we cache kana representations and audio for frequently used words?
22. What should be the timeout values for API calls to backend services?

### Error Handling
23. How should the application handle backend service unavailability?
24. Should we implement automatic retries for failed API calls?
25. How should we handle OCR failures or low-confidence results?
26. What feedback should be provided when AWS services (Bedrock/Polly) fail?