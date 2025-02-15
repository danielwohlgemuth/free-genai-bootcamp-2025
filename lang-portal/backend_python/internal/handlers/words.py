from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from ..models.base import get_db
from ..models.models import Word, WordReviewItem, Group
from typing import Optional

router = APIRouter()

@router.get("")
async def get_words(
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(Word)
    total_count = await db.execute(count_query)
    total_count = total_count.scalar()
    
    # Get words with their review stats
    query = select(
        Word,
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == True).label("correct_count"),
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == False).label("wrong_count")
    ).outerjoin(WordReviewItem) \
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

@router.get("/{word_id}")
async def get_word(word_id: int, db: AsyncSession = Depends(get_db)):
    # Get word with its review stats and groups
    query = select(
        Word,
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == True).label("correct_count"),
        func.count(WordReviewItem.id).filter(WordReviewItem.correct == False).label("wrong_count")
    ).outerjoin(WordReviewItem) \
     .where(Word.id == word_id) \
     .group_by(Word.id)
    
    result = await db.execute(query)
    word_data = result.first()
    
    if not word_data:
        return None
    
    word, correct_count, wrong_count = word_data
    
    # Get groups for the word
    groups_query = select(Group).join(Word.groups).where(Word.id == word_id)
    groups_result = await db.execute(groups_query)
    groups = groups_result.scalars().all()
    
    return {
        "japanese": word.japanese,
        "romaji": word.romaji,
        "english": word.english,
        "stats": {
            "correct_count": correct_count,
            "wrong_count": wrong_count
        },
        "groups": [
            {
                "id": group.id,
                "name": group.name
            }
            for group in groups
        ]
    } 