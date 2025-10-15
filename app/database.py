from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get database path from environment variable or use default
DB_PATH = os.getenv("DB_PATH", "/data/history.db")
DB_DIR = os.path.dirname(DB_PATH)

# Create directory if it doesn't exist
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

Base = declarative_base()

class RequestHistory(Base):
    __tablename__ = "request_history"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(Text)  # JSON string
    body = Column(Text)  # JSON string
    status_code = Column(Integer)
    response_headers = Column(Text)  # JSON string
    response_body = Column(Text)
    error = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "status_code": self.status_code,
            "response_headers": self.response_headers,
            "response_body": self.response_body,
            "error": self.error,
            "duration_ms": self.duration_ms
        }
