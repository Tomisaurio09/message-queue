
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.app.core.config import settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  
    pool_pre_ping=True    
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()