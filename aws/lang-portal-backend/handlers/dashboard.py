from auth import get_current_user
from datetime import datetime
from db import get_db
from fastapi import APIRouter, Depends
from models import StudySession, Group, WordReviewItem, Word, StudyActivity
from sqlalchemy import func, select, Integer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/last_study_session")
async def get_last_study_session(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = (
        select(
            StudySession,
            Group.name.label("group_name"),
            StudyActivity.name.label("activity_name"),
            func.count(WordReviewItem.id).label("review_items_count")
        )
        .join(Group)
        .join(StudyActivity)
        .outerjoin(WordReviewItem)
        .where(StudySession.user_id == current_user)
        .group_by(StudySession.id, Group.name, StudyActivity.name)
        .order_by(StudySession.created_at.desc())
        .limit(1)
    )
    
    result = await db.execute(query)
    session_data = result.first()
    
    if not session_data:
        return None
    
    session, group_name, activity_name, review_count = session_data
    return {
        "id": session.id,
        "group_name": group_name,
        "activity_name": activity_name,
        "start_time": session.created_at.isoformat(),
        "review_items_count": review_count
    }

@router.get("/study_progress")
async def get_study_progress(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Get total available words
    total_words_query = select(func.count()).select_from(Word)
    total_words_result = await db.execute(total_words_query)
    total_available_words = total_words_result.scalar()
    
    # Get total unique words studied
    studied_words_query = select(func.count(func.distinct(WordReviewItem.word_id))) \
        .select_from(WordReviewItem) \
        .where(WordReviewItem.user_id == current_user)
    studied_words_result = await db.execute(studied_words_query)
    total_words_studied = studied_words_result.scalar()
    
    return {
        "total_words_studied": total_words_studied or 0,
        "total_available_words": total_available_words or 0
    }

@router.get("/quick-stats")
async def get_quick_stats(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Calculate success rate
    review_stats_query = select(
        func.count().label("total"),
        func.sum(func.cast(WordReviewItem.correct, Integer)).label("correct")
    ).select_from(WordReviewItem) \
    .where(WordReviewItem.user_id == current_user)
    review_stats = await db.execute(review_stats_query)
    review_stats = review_stats.first()
    
    success_rate = 0
    if review_stats.total:
        success_rate = (review_stats.correct / review_stats.total) * 100
    
    # Get total study sessions
    sessions_query = select(func.count()).select_from(StudySession) \
        .where(StudySession.user_id == current_user)
    total_sessions = await db.execute(sessions_query)
    total_sessions = total_sessions.scalar()
    
    # Get total active groups (groups with at least one study session)
    active_groups_query = select(func.count(func.distinct(StudySession.group_id))) \
        .select_from(StudySession) \
        .where(StudySession.user_id == current_user)
    active_groups = await db.execute(active_groups_query)
    active_groups = active_groups.scalar()
    
    # Calculate study streak
    streak_query = select(StudySession.created_at) \
        .where(StudySession.user_id == current_user) \
        .order_by(StudySession.created_at.desc())
    sessions = await db.execute(streak_query)
    sessions = sessions.scalars().all()
    
    streak_days = 0
    if sessions:
        # Convert all session dates to date objects and get unique dates
        session_dates = sorted(set(session.date() for session in sessions), reverse=True)
        
        current_date = datetime.now().date()
        # Check if there's a session today or yesterday to start the streak
        if (current_date - session_dates[0]).days <= 1:
            streak_days = 1
            prev_date = session_dates[0]
            
            # Check consecutive days
            for session_date in session_dates[1:]:
                # If exactly one day difference, continue streak
                if (prev_date - session_date).days == 1:
                    streak_days += 1
                    prev_date = session_date
                # If same day, skip
                elif (prev_date - session_date).days == 0:
                    continue
                # If gap in days, end streak
                else:
                    break
    
    return {
        "success_rate": round(success_rate, 1),
        "total_study_sessions": total_sessions or 0,
        "total_active_groups": active_groups or 0,
        "study_streak_days": streak_days
    } 