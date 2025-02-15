from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from ..models.base import get_db, Base, engine
from ..models.models import StudySession, WordReviewItem, Word, Group, WordGroup, StudyActivity
import json
from pathlib import Path

router = APIRouter()

@router.post("/reset_history")
async def reset_history(db: AsyncSession = Depends(get_db)):
    """Reset all study history while keeping words and groups intact"""
    
    # Delete all word review items
    await db.execute(delete(WordReviewItem))
    
    # Delete all study sessions
    await db.execute(delete(StudySession))
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Study history has been reset"
    }

@router.post("/full_reset")
async def full_reset(db: AsyncSession = Depends(get_db)):
    """Completely reset the system and reload seed data"""
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Load seed data
    seeds_dir = Path('db/seeds')
    for seed_file in seeds_dir.glob('*.json'):
        with open(seed_file) as f:
            seed_data = json.load(f)
            
            # Create group
            group = Group(name=seed_data['group_name'])
            db.add(group)
            await db.flush()  # To get the group ID
            
            # Create words and link to group
            for word_data in seed_data['words']:
                word = Word(
                    japanese=word_data['japanese'],
                    romaji=word_data['romaji'],
                    english=word_data['english'],
                    parts=word_data.get('parts', {})
                )
                db.add(word)
                await db.flush()  # To get the word ID
                
                # Create word-group association
                word_group = WordGroup(
                    word_id=word.id,
                    group_id=group.id
                )
                db.add(word_group)
    
    # Create default study activities
    default_activities = [
        {
            "name": "Vocabulary Quiz",
            "thumbnail_url": "/assets/vocab-quiz.jpg",
            "description": "Test your vocabulary knowledge with flashcards"
        },
        {
            "name": "Writing Practice",
            "thumbnail_url": "/assets/writing-practice.jpg",
            "description": "Practice writing Japanese characters"
        },
        {
            "name": "Listening Exercise",
            "thumbnail_url": "/assets/listening-exercise.jpg",
            "description": "Improve your listening comprehension"
        }
    ]
    
    for activity_data in default_activities:
        activity = StudyActivity(**activity_data)
        db.add(activity)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "System has been fully reset"
    } 