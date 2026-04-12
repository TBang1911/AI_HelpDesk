from datetime import datetime
from sqlmodel import CHAR, TIMESTAMP, SQLModel, Field, text
from sqlalchemy import Column, Index
from typing import Optional
import uuid6

class ConversationHistory(SQLModel, table=True):
    __tablename__ = "conversation_history"
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
    )
    
    id: str = Field(default_factory=lambda: str(uuid6.uuid7()), sa_column=Column(CHAR(36), primary_key=True))
    session_id: str = Field(index=True)
    role: str = Field()
    content: str = Field()
    timestamp: Optional[datetime] = Field(default=None, sa_column=Column('timestamp', TIMESTAMP, server_default=text('(now())')))