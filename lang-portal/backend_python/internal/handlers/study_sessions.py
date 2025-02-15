from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
from ..models.base import get_db
from ..models.models import StudySession, Word, WordReviewItem

router = APIRouter()

@router.get("")
async def get_study_sessions(
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(StudySession)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get study sessions with review items count
    query = select(
        StudySession,
        func.count(WordReviewItem.id).label("review_items_count")
    ).outerjoin(StudySession.review_items) \
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

@router.get("/{session_id}")
async def get_study_session(session_id: int, db: AsyncSession = Depends(get_db)):
    query = select(
        StudySession,
        func.count(WordReviewItem.id).label("review_items_count")
    ).outerjoin(StudySession.review_items) \
     .where(StudySession.id == session_id) \
     .group_by(StudySession.id)
    
    result = await db.execute(query)
    session_data = result.first()
    
    if not session_data:
        return None
    
    session, review_count = session_data
    
    return {
        "id": session.id,
        "activity_name": session.activity.name,
        "group_name": session.group.name,
        "start_time": session.created_at.isoformat(),
        "end_time": (session.created_at + timedelta(minutes=10)).isoformat(),  # Estimated
        "review_items_count": review_count
    }

@router.get("/{session_id}/words")
async def get_session_words(
    session_id: int,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count of reviewed words in session
    count_query = select(func.count(Word.id)) \
        .join(WordReviewItem) \
        .where(WordReviewItem.study_session_id == session_id)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get words with their review results for this session
    query = select(
        Word,
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == True).label("correct_count"),
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == False).label("wrong_count")
    ).join(WordReviewItem) \
     .where(WordReviewItem.study_session_id == session_id) \
     .group_by(Word.id) \
     .offset(offset) \
     .limit(per_page)
    
    result = await db.execute(query)
    words = result.all()
    
    return {
        "items": [
            {
                "japanese": word.japanese,
                "romaji": word.romaji,
                "english": word.english,
                "correct_count": correct_count,
                "wrong_count": wrong_count
            }
            for word, correct_count, wrong_count in words
        ],
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "total_items": total_count,
            "items_per_page": per_page
        }
    }

@router.post("/{session_id}/words/{word_id}/review")
async def create_word_review(
    session_id: int,
    word_id: int,
    correct: bool,
    db: AsyncSession = Depends(get_db)
):
    # Verify session and word exist
    session = await db.execute(
        select(StudySession).where(StudySession.id == session_id)
    )
    session = session.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    word = await db.execute(
        select(Word).where(Word.id == word_id)
    )
    word = word.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Create review item
    review_item = WordReviewItem(
        word_id=word_id,
        study_session_id=session_id,
        correct=correct,
        created_at=datetime.utcnow()
    )
    
    db.add(review_item)
    await db.commit()
    
    return {
        "success": True,
        "word_id": word_id,
        "study_session_id": session_id,
        "correct": correct,
        "created_at": review_item.created_at.isoformat()
    } 