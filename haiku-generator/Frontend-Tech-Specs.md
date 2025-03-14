# Haiku Generator - Frontend Technical Specifications

## Introduction

This document outlines the technical specifications for the Haiku Generator frontend application. The application is designed to provide users with an interactive interface to generate and manage haikus. Built using React, the frontend communicates with a backend API to fetch, create, and delete haikus, enhancing the user experience with real-time updates and a chat interface.

## Architecture Overview

The Haiku Generator frontend is built using React, a popular JavaScript library for building user interfaces. The application follows a component-based architecture, allowing for reusable UI components that manage their own state.

The frontend communicates with a backend API, which is responsible for handling data storage and retrieval. The key technologies involved in the architecture include:

- **React**: For building the user interface.
- **TailwindCSS**: For styling the components and ensuring a responsive design.

The architecture allows for a seamless user experience, with real-time updates and efficient data handling.

## Pages Overview

The Haiku Generator frontend consists of two main pages:

### Haiku Overview Page
This page displays a list of haikus with the following features:
- **Haiku ID**: Unique identifier for each haiku.
- **Haiku**: Displays the combined English haiku lines.
- **Status**: Indicates whether the haiku generation has failed, along with a count of populated fields versus total fields.
- **Data Fetching**: Utilizes the `GET /haiku` endpoint to retrieve haiku data.
- **Delete Functionality**: Each haiku has a delete button that triggers the `DELETE /haiku/{haiku_id}` endpoint.
- **Create Haiku Button**: Redirects to the generator page with a new haiku ID.

### Haiku Generator Page
This page features a chat interface for generating haikus:
- **Message Sending**: Each message is sent to the backend using the `POST /chat/{haiku_id}` endpoint, with a loading indicator displayed during processing.
- **Chat Disablement**: The chat interface is disabled once the backend returns a haiku status that is not "new".
- **Summary Section**: Conditionally displays available haiku information, including:
  - English haiku lines.
  - A grid layout for displaying Japanese haiku lines, images, and audio playback options.
- **Data Fetching**: Uses the `GET /haiku/{haiku_id}` endpoint to retrieve haiku and chat history.
- **Delete Functionality**: Includes a delete button that utilizes the `DELETE /haiku/{haiku_id}` endpoint.

## API Endpoints

The Haiku Generator frontend interacts with several backend API endpoints to perform various operations. Below are the key endpoints utilized by the application:

### 1. GET /haiku
- **Description**: Retrieves a list of all haikus.
- **Response Structure**:
  ```json
  {
    "haikus": [
      {
        "haiku_id": "string",
        "status": "string",
        "error_message": "string",
        "haiku_line_en_1": "string",
        "haiku_line_en_2": "string",
        "haiku_line_en_3": "string",
        "image_description_1": "string",
        "image_description_2": "string",
        "image_description_3": "string",
        "image_link_1": "string",
        "image_link_2": "string",
        "image_link_3": "string",
        "haiku_line_ja_1": "string",
        "haiku_line_ja_2": "string",
        "haiku_line_ja_3": "string",
        "audio_link_1": "string",
        "audio_link_2": "string",
        "audio_link_3": "string"
      }
    ]
  }
  ```
 
### 2. GET /haiku/{haiku_id}
- **Description**: Retrieves details for a specific haiku using its ID.
- **Response Structure**:
  ```json
  {
    "haiku": {
      "haiku_id": "string",
      "status": "string",
      "error_message": "string",
      "haiku_line_en_1": "string",
      "haiku_line_en_2": "string",
      "haiku_line_en_3": "string",
      "image_description_1": "string",
      "image_description_2": "string",
      "image_description_3": "string",
      "image_link_1": "string",
      "image_link_2": "string",
      "image_link_3": "string",
      "haiku_line_ja_1": "string",
      "haiku_line_ja_2": "string",
      "haiku_line_ja_3": "string",
      "audio_link_1": "string",
      "audio_link_2": "string",
      "audio_link_3": "string"
    },
    "chats": [
      {
        "chat_id": 0,
        "haiku_id": "string",
        "role": "string",
        "message": "string"
      }
    ]
  }
  ```

### 3. POST /chat/{haiku_id}
- **Description**: Sends a message to the chat interface for a specific haiku.
- **Request Body**:
  ```json
  {
    "message": "string"
  }
  ```
- **Response Structure**:
  ```json
  {
    "chat": {
      "chat_id": 0,
      "haiku_id": "string",
      "role": "string",
      "message": "string"
    },
    "haiku": {
      "haiku_id": "string",
      "status": "string",
      "error_message": "string",
      "haiku_line_en_1": "string",
      "haiku_line_en_2": "string",
      "haiku_line_en_3": "string",
      "image_description_1": "string",
      "image_description_2": "string",
      "image_description_3": "string",
      "image_link_1": "string",
      "image_link_2": "string",
      "image_link_3": "string",
      "haiku_line_ja_1": "string",
      "haiku_line_ja_2": "string",
      "haiku_line_ja_3": "string",
      "audio_link_1": "string",
      "audio_link_2": "string",
      "audio_link_3": "string"
    }
  }
  ```

### 4. DELETE /haiku/{haiku_id}
- **Description**: Deletes a specific haiku using its ID.
- **Request Body**:
  ```json
  {
    "message": "string"
  }
  ```

## UI Components

The Haiku Generator frontend is composed of various UI components that enhance user interaction and experience. Below are the key components used in the application:

### 1. Haiku List Component
- **Description**: Displays a list of haikus retrieved from the backend.
- **Features**:
  - Renders each haiku with its ID, text, and status.
  - Includes delete buttons for each haiku.

### 2. Haiku Generator Component
- **Description**: Provides a chat interface for generating haikus.
- **Features**:
  - Previous chat messages.
  - Input field for user messages.
  - Send button to submit messages to the backend.
  - Displays responses from the backend, including generated haikus and associated images.

### 3. Summary Display Component
- **Description**: Conditionally shows additional information about the haikus.
- **Features**:
  - Displays English haiku lines when available.
  - Grid Layout:
    - Top-Left: Shows the Japanese haiku lines with a play button after each line to play the corresponding audio file, if it exists.
    - Top-Right: Displays Image 1 associated with the haiku.
    - Bottom-Left: Displays Image 2 associated with the haiku.
    - Bottom-Right: Displays Image 3 associated with the haiku.

### 4. Loading Indicator Component
- **Description**: Indicates that a request is being processed.
- **Features**:
  - Shown during API calls to enhance user experience by providing feedback.

### 5. Error Message Component
- **Description**: Displays error messages to the user.
- **Features**:
  - Provides feedback when API requests fail or when input validation errors occur.

## Environment Configuration

To ensure the Haiku Generator frontend operates correctly, the following environment variables should be configured:

### 1. Backend API URL
- **Variable Name**: `REACT_APP_BACKEND_URL`
- **Description**: This variable holds the URL of the backend API. It should be set to the appropriate address where the backend service is running, for example:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### 2. Other Configuration Variables
- Additional configuration variables may be required depending on the features implemented in the application. Ensure to review the codebase for any other necessary environment settings.

### Setup Instructions
1. Create a `.env` file in the root of the project directory.
2. Add the required environment variables in the format specified above.
3. Restart the development server to apply the changes.
