from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from internal.handlers import (
    dashboard,
    words,
    groups,
    study_sessions,
    study_activities,
    system
)

app = FastAPI(title="Language Learning Portal API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(words.router, prefix="/api/words", tags=["words"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(study_sessions.router, prefix="/api/study_sessions", tags=["study_sessions"])
app.include_router(study_activities.router, prefix="/api/study_activities", tags=["study_activities"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 