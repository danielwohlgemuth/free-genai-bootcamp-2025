# Haiku Generator

A frontend application for generating and managing haikus using React.

## Features

- View a list of haikus
- Generate new haikus through a chat interface
- Play audio for haikus
- Display images associated with haikus

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/danielwohlgemuth/free-genai-bootcamp-2025.git
   cd haiku-generator/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a .env file in the root of the project and set the backend API URL:
   ```bash
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

## Running the Application

To start the application, run:
```bash
npm start
```

The application will be available at `http://localhost:3001`.

## Built With
- [React](https://react.dev/) - The web framework used
- [Axios](https://axios-http.com/) - For making HTTP requests
- [UUID](https://www.npmjs.com/package/uuid) - For generating unique identifiers
- [Material UI](https://mui.com/) - For styling
