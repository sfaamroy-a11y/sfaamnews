"""
database.py - SFAAM NEWS V2
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sfaam.db")
DELETE_AFTER = int(os.getenv("DELETE_AFTER_DAYS", "30"))

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(500), nullable=False)
    slug         = Column(String(600), nullable=True)
    original_url = Column(String(1000), unique=True, nullable=False)
    ai_content   = Column(Text, nullable=False)
    summary      = Column(Text, nullable=True)
    image_url    = Column(String(1000), nullable=True)
    region       = Column(String(50), nullable=False)
    meta_desc    = Column(String(300), nullable=True)
    keywords     = Column(String(500), nullable=True)
    views        = Column(Integer, default=0)
    date         = Column(DateTime, default=datetime.utcnow)


class ProcessedURL(Base):
    __tablename__ = "processed_urls"
    id  = Column(Integer, primary_key=True)
    url = Column(String(1000), unique=True, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ SFAAM NEWS Database ready.")


def delete_old_articles():
    db = SessionLocal()
    try:
        cutoff  = datetime.utcnow() - timedelta(days=DELETE_AFTER)
        deleted = db.query(Article).filter(Article.date < cutoff).delete()
        db.commit()
        if deleted:
            print(f"🗑️ {deleted} purane articles delete hue.")
    except Exception as e:
        db.rollback()
        print(f"Cleanup error: {e}")
    finally:
        db.close()
