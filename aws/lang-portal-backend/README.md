# Language Learning Portal Backend

A FastAPI-based backend service for the language learning portal.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install the requirements:
```bash
pip install -r requirements.txt
```

### Database Setup

Start the database:
```bash
docker compose up -d
```

Connect to the database:
```bash
docker exec -it lang-portal-backend-db-1 psql -U user dbname
```

Before running the server for the first time:

Run the complete setup with:
```bash
invoke setup
```

Or run individual tasks:
```bash
invoke init-db
invoke run-migrations
invoke seed-data
```

## Running the Server

You can run the server in two ways:

1. Using invoke:
```bash
invoke run-server
```

2. Using invoke with auto-reload (recommended for development):
```bash
invoke dev-server
```

The server will start on `http://localhost:8000`.

## Project Structure

```
backend_python/
├── db/
│   ├── migrations/ # Database migrations
│   └── seeds/      # Seed data files
├── handlers/       # HTTP handlers organized by feature
├── main.py         # Server entry point
├── models.py       # Data structures and database operations
├── requirements.txt    # Python dependencies
└── tasks.py        # Task definitions
```

## API Endpoints

The API provides endpoints for:
- Dashboard statistics
- Word management
- Group management
- Study sessions
- Study activities
- System management

For detailed API documentation, please refer to the Swagger UI (`http://localhost:8000/docs`) or ReDoc (`http://localhost:8000/redoc`) when the server is running.