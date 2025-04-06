from auth import get_current_user
from datetime import datetime, timedelta, UTC
from db import get_db
from fastapi import APIRouter, Depends, HTTPException, Body
from models import StudySession, Word, WordReviewItem, StudyActivity, Group
from pydantic import BaseModel
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class CreateWordReviewRequest(BaseModel):
    correct: bool

@router.get("")
async def get_study_sessions(
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()) \
        .select_from(StudySession) \
        .where(StudySession.user_id == current_user)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get study sessions with review items count
    query = (
        select(
            StudySession.id,
            StudySession.created_at,
            StudySession.group_id,
            StudySession.study_activity_id,
            StudyActivity.name.label("activity_name"),
            Group.name.label("group_name"),
            func.count(WordReviewItem.id).label("review_items_count")
        )
        .join(StudyActivity, StudySession.study_activity_id == StudyActivity.id)
        .join(Group, StudySession.group_id == Group.id)
        .outerjoin(StudySession.review_items)
        .group_by(
            StudySession.id,
            StudySession.created_at,
            StudySession.group_id,
            StudySession.study_activity_id,
            StudyActivity.name,
            Group.name
        )
        .where(StudySession.user_id == current_user)
        .order_by(StudySession.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    
    result = await db.execute(query)
    sessions = result.all()
    
    return {
        "items": [
            {
                "id": session.id,
                "activity_name": session.activity_name,
                "group_name": session.group_name,
                "start_time": session.created_at.isoformat(),
                "end_time": (session.created_at + timedelta(minutes=10)).isoformat(),
                "review_items_count": session.review_items_count
            }
            for session in sessions
        ],
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "total_items": total_count,
            "items_per_page": per_page
        }
    }

@router.get("/{session_id}")
async def get_study_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get details of a specific study session"""
    query = (
        select(StudySession, StudyActivity.name, StudyActivity.type, Group.name) \
        .join(StudyActivity, StudySession.study_activity_id == StudyActivity.id) \
        .join(Group, StudySession.group_id == Group.id) \
        .where(StudySession.id == session_id) \
        .where(StudySession.user_id == current_user)
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session, activity_name, activity_type, group_name = row
    
    return {
        "id": session.id,
        "activity_name": activity_name,
        "activity_type": activity_type,
        "group_name": group_name,
        "start_time": session.created_at
    }

@router.get("/{session_id}/words")
async def get_session_words(
    session_id: int,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
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
     .where(WordReviewItem.user_id == current_user) \
     .group_by(Word.id) \
     .offset(offset) \
     .limit(per_page)
    
    result = await db.execute(query)
    words = result.all()
    
    return {
        "items": [
            {
                "id": word.id,
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
    request: CreateWordReviewRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    correct = request.correct
    # Verify session and word exist
    session = await db.execute(
        select(StudySession) \
            .where(StudySession.id == session_id) \
            .where(StudySession.user_id == current_user)
    )
    session = session.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    word = await db.execute(
        select(Word) \
            .where(Word.id == word_id) \
            .where(Word.user_id == current_user)
    )
    word = word.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Create review item
    review_item = WordReviewItem(
        user_id=current_user,
        word_id=word_id,
        study_session_id=session_id,
        correct=correct,
        created_at=datetime.now(UTC).replace(tzinfo=None)
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

@router.get("/{session_id}/next_words")
async def get_next_words(
    session_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Get the study session
    session_query = select(StudySession) \
        .where(StudySession.id == session_id) \
        .where(StudySession.user_id == current_user)
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    # Get words from the group that haven't been reviewed in this session
    words_query = (
        select(Word)
        .join(Word.groups) \
        .where(Group.id == session.group_id) \
        .outerjoin(
            WordReviewItem,
            and_(
                WordReviewItem.word_id == Word.id,
                WordReviewItem.study_session_id == session_id
            )
        ) \
        .where(WordReviewItem.id == None) \
        .where(Word.user_id == current_user) \
        .limit(limit)
    )
    
    result = await db.execute(words_query)
    words = result.scalars().all()
    
    return {
        "items": [
            {
                "id": word.id,
                "japanese": word.japanese,
                "romaji": word.romaji,
                "english": word.english,
                "parts": word.parts
            }
            for word in words
        ]
    } 