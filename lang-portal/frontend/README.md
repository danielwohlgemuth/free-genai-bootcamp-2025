# Japanese Study Portal Frontend

## Overview

This is a web application that allows users to study Japanese vocabulary. It serves as:
- An inventory of possible vocabulary that can be learned
- A record store for tracking correct and wrong answers during practice
- A unified launchpad for different learning apps

## Technical Stack

- React (frontend framework)
- TypeScript (statically typed javascript)
- Tailwind CSS (css framework)
- Vite.js (frontend tooling)
- ShadCN (UI components)
- React Query (data fetching)
- React Router (routing)

## Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)
- Backend server running (see [backend README](../backend_python/README.md))

## Directory Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── ui/        # ShadCN components
│   │   └── shared/    # Shared components across pages
│   ├── pages/         # Page components
│   │   ├── Dashboard/
│   │   ├── StudyActivities/
│   │   ├── Words/
│   │   ├── Groups/
│   │   ├── StudySessions/
│   │   └── Settings/
│   ├── lib/           # Utilities and helpers
│   ├── api/           # API integration
│   ├── types/         # TypeScript types
│   └── routes/        # Route definitions
├── public/            # Static assets
└── index.html
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory:
```env
VITE_API_URL=http://localhost:8000
```

## Development

To start the development server:

```bash
npm run dev
```

This will start the application in development mode at `http://localhost:5173`

## Building for Production

To create a production build:

```bash
npm run build
```

To preview the production build:

```bash
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Pages

The application includes the following pages:

- `/dashboard` - Overview of learning progress
- `/study_activities` - List of available study activities
- `/study_activities/:id` - Details of a specific study activity
- `/study_activities/:id/launch` - Launch a study activity
- `/words` - List of all vocabulary words
- `/words/:id` - Details of a specific word
- `/groups` - List of word groups
- `/groups/:id` - Details of a specific group
- `/study_sessions` - List of study sessions
- `/study_sessions/:id` - Details of a specific study session
- `/settings` - Application settings and reset options

## API Integration

The frontend communicates with the backend server through a REST API. The base URL for the API is configured through the `VITE_API_URL` environment variable.

Make sure the backend server is running and accessible before starting the frontend application. See [backend README](../backend_python/README.md) for more details.
