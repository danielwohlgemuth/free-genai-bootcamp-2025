import json
from auth import get_current_user
from db import get_db
from fastapi import APIRouter, Depends
from models import StudySession, WordReviewItem, Word, Group, WordGroup
from pathlib import Path
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/reset_study_progress")
async def reset_study_progress(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Reset all study progress while keeping words and groups intact"""
    
    # Delete all word review items
    await db.execute(delete(WordReviewItem).where(WordReviewItem.user_id == current_user))
    
    # Delete all study sessions
    await db.execute(delete(StudySession).where(StudySession.user_id == current_user))
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Study progress has been reset"
    }

@router.post("/reset_data")
async def reset_data(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Reset all data"""
    
    # Delete all word review items
    await db.execute(delete(WordReviewItem).where(WordReviewItem.user_id == current_user))
    
    # Delete all study sessions
    await db.execute(delete(StudySession).where(StudySession.user_id == current_user))
    
    # Delete all word groups
    await db.execute(delete(WordGroup).where(WordGroup.user_id == current_user))

    # Delete all words
    await db.execute(delete(Word).where(Word.user_id == current_user))
    
    # Delete all groups
    await db.execute(delete(Group).where(Group.user_id == current_user))
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Data has been reset"
    }

@router.post("/load_initial_data")
async def load_initial_data(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Load initial data"""

    # Load seed data
    seeds_dir = Path('db/seeds')
    for seed_file in seeds_dir.glob('*.json'):
        with open(seed_file) as f:
            seed_data = json.load(f)
            
            # Create group
            group = Group(
                user_id=current_user,
                name=seed_data['group_name'],
            )
            db.add(group)
            
            # Create words and link to group
            words = []
            for word_data in seed_data['words']:
                word = Word(
                    user_id=current_user,
                    japanese=word_data['japanese'],
                    romaji=word_data['romaji'],
                    english=word_data['english'],
                    parts=word_data.get('parts', {})
                )
                db.add(word)
                words.append(word)

            # Get the group ID and the word ID
            await db.flush()

            # Create word-group association
            for word in words:
                word_group = WordGroup(
                    user_id=current_user,
                    word_id=word.id,
                    group_id=group.id
                )
                db.add(word_group)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Initial data has been loaded"
    } 