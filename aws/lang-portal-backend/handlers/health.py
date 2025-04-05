import json
from db import get_db, Base, engine
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check the health of the application"""
    return {
        "success": True,
        "message": "Application is healthy"
    }