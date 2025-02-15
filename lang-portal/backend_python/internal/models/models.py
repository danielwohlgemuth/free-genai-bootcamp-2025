from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime, UTC

class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True)
    japanese = Column(String)
    romaji = Column(String)
    english = Column(String)
    parts = Column(JSON)
    
    groups = relationship("Group", secondary="words_groups", back_populates="words")
    review_items = relationship("WordReviewItem", back_populates="word")

class WordGroup(Base):
    __tablename__ = "words_groups"
    
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    words = relationship("Word", secondary="words_groups", back_populates="groups")
    study_sessions = relationship("StudySession", back_populates="group")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    study_activity_id = Column(Integer, ForeignKey("study_activities.id"))
    
    group = relationship("Group", back_populates="study_sessions")
    activity = relationship("StudyActivity", back_populates="sessions")
    review_items = relationship("WordReviewItem", back_populates="study_session")

class StudyActivity(Base):
    __tablename__ = "study_activities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    thumbnail_url = Column(String)
    description = Column(String)
    
    sessions = relationship("StudySession", back_populates="activity")

class WordReviewItem(Base):
    __tablename__ = "word_review_items"
    
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"))
    correct = Column(Boolean)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    word = relationship("Word", back_populates="review_items")
    study_session = relationship("StudySession", back_populates="review_items") 