from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    image: str  # This will store the image path or URL
    timestamp: datetime = Field(default_factory=datetime.utcnow)