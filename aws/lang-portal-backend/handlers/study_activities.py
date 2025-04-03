from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from models import StudyActivity, StudySession, WordReviewItem, Group
from pydantic import BaseModel

router = APIRouter()

class CreateStudySessionRequest(BaseModel):
    group_id: int
    study_activity_id: int

@router.get("")
async def get_study_activities(db: AsyncSession = Depends(get_db)):
    query = select(StudyActivity)
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return [
        {
            "id": activity.id,
            "name": activity.name,
            "thumbnail_url": activity.thumbnail_url,
            "description": activity.description,
            "type": activity.type
        }
        for activity in activities
    ]

@router.get("/{activity_id}")
async def get_study_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    query = select(StudyActivity).where(StudyActivity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        return None
    
    return {
        "id": activity.id,
        "name": activity.name,
        "thumbnail_url": activity.thumbnail_url,
        "description": activity.description,
        "type": activity.type
    }

@router.get("/{activity_id}/study_sessions")
async def get_activity_study_sessions(
    activity_id: int,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(StudySession) \
        .where(StudySession.study_activity_id == activity_id)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get study sessions with review items count
    query = select(
        StudySession,
        func.count(WordReviewItem.id).label("review_items_count")
    ).outerjoin(StudySession.review_items) \
     .where(StudySession.study_activity_id == activity_id) \
     .group_by(StudySession.id) \
     .order_by(StudySession.created_at.desc()) \
     .offset(offset) \
     .limit(per_page)
    
    result = await db.execute(query)
    sessions = result.all()
    
    return {
        "items": [
            {
                "id": session.id,
                "activity_name": session.activity.name,
                "group_name": session.group.name,
                "start_time": session.created_at.isoformat(),
                "end_time": (session.created_at + timedelta(minutes=10)).isoformat(),  # Estimated
                "review_items_count": review_count
            }
            for session, review_count in sessions
        ],
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "total_items": total_count,
            "items_per_page": per_page
        }
    }

@router.post("")
async def create_study_session(
    request: CreateStudySessionRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    group_id = request.group_id
    study_activity_id = request.study_activity_id
    # Verify group and activity exist
    group = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = group.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    activity = await db.execute(
        select(StudyActivity).where(StudyActivity.id == study_activity_id)
    )
    activity = activity.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Study activity not found")
    
    # Create study session
    session = StudySession(
        group_id=group_id,
        study_activity_id=study_activity_id,
        created_at=datetime.now(UTC)
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "id": session.id,
        "group_id": group_id
    } 