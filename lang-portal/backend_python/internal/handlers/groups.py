from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from ..models.base import get_db
from ..models.models import Group, Word, StudySession, WordReviewItem

router = APIRouter()

@router.get("")
async def get_groups(
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(Group)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get groups with word count
    query = select(
        Group,
        func.count(Word.id).label("word_count")
    ).outerjoin(Group.words) \
     .group_by(Group.id) \
     .offset(offset) \
     .limit(per_page)
    
    result = await db.execute(query)
    groups = result.all()
    
    return {
        "items": [
            {
                "id": group.id,
                "name": group.name,
                "word_count": word_count
            }
            for group, word_count in groups
        ],
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "total_items": total_count,
            "items_per_page": per_page
        }
    }

@router.get("/{group_id}")
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    # Get group with word count
    query = select(
        Group,
        func.count(Word.id).label("word_count")
    ).outerjoin(Group.words) \
     .where(Group.id == group_id) \
     .group_by(Group.id)
    
    result = await db.execute(query)
    group_data = result.first()
    
    if not group_data:
        return None
    
    group, word_count = group_data
    
    return {
        "id": group.id,
        "name": group.name,
        "stats": {
            "total_word_count": word_count
        }
    }

@router.get("/{group_id}/words")
async def get_group_words(
    group_id: int,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count of words in group
    count_query = select(func.count()).select_from(Word).join(Word.groups).where(Group.id == group_id)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get words with their review stats
    query = select(
        Word,
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == True).label("correct_count"),
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == False).label("wrong_count")
    ).join(Word.groups) \
     .outerjoin(WordReviewItem) \
     .where(Group.id == group_id) \
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

@router.get("/{group_id}/study_sessions")
async def get_group_study_sessions(
    group_id: int,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(StudySession).where(StudySession.group_id == group_id)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get study sessions with review items count
    query = select(
        StudySession,
        func.count(WordReviewItem.id).label("review_items_count")
    ).outerjoin(StudySession.review_items) \
     .where(StudySession.group_id == group_id) \
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