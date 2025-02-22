# Kana Writing Practice Application - Technical Specification

## Overview
A web-based application for practicing Japanese kana writing using AWS services and Gradio interface.

## System Architecture

### Components
1. **Frontend (Gradio Interface)**
   - Interactive drawing canvas (300px high, 900px wide)
   - Word group selection interface
   - Clear canvas functionality
   - Multi-character input support
   - Loading indicator for API calls
   - Audio playback controls with progress indicator and speed adjustment
   - Word regeneration functionality

2. **Backend Services**
   - Configurable backend URL (default: localhost:8000)
   - Word group retrieval endpoint integration
   - Word list retrieval endpoint integration
   - AWS Bedrock for kana representation generation
   - Amazon Polly for Japanese word audio synthesis
   - manga_ocr package for OCR and character recognition
   - Caching system for frequently used words and audio

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
- Gradio framework for UI
- AWS SDK (boto3) for AWS services integration
- Manga OCR for character recognition

### API Integration
#### Endpoints
1. GET /api/groups
   - Response: {"items": [{"id": groupId, "name": groupName}]}
   - Used for initial word group loading

2. GET /api/groups/{groupId}/words
   - Response: {"items": [{"japanese": japanese, "english": english}]}
   - Used for word retrieval after group selection

### User Interface Requirements
1. Writing Input
   - Primary: Drawing canvas
   - Secondary: File upload input
   - Automatic fallback to canvas if no file

2. Drawing Canvas
   - Dimensions: 300px high, 900px wide
   - Multi-character input support
   - Clear canvas button
   - No grid lines or guide marks
   - No reference images while drawing

3. File Handling
   - Supported formats: JPG, PNG
   - Maximum file size: 10MB
   - No batch upload support
   - Image preprocessing: contrast enhancement

4. Audio Playback
   - Play button for Polly-generated audio
   - Replay functionality
   - Speed adjustment controls
   - Progress indicator during playback
   - No automatic playback for new words
   - Cached audio for frequently used words

5. Validation
   - Submit button for OCR processing
   - Clear success/failure feedback
   - "Try Again" option for failures
   - "Next Word" button for new word from same group

### Error Handling
1. Backend Service Unavailability
   - User-friendly error messages indicating which service failed
   - No automatic retries
   - Specific error handling for AWS services (Bedrock/Polly)

2. OCR Processing
   - Failed OCR treated as incorrect match
   - No confidence score implementation
   - No retry attempt limits

### Performance Considerations
1. API Rate Limiting
   - Implemented for Bedrock and Polly services
   - 30-second timeout for all API calls
   - Loading indicators during API calls

2. Caching
   - Audio files for frequently used words
   - Kana representations for common words
   - No offline mode support

### Progress Tracking
- No user progress tracking
- No success rate tracking
- No storage of successful attempts