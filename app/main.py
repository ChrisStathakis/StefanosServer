from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
import shutil
import os
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    image: str  # This will store the image path or URL
    timestamp: datetime = Field(default_factory=datetime.utcnow)



app = FastAPI()

MEDIA_FOLDER = "app/media"
os.makedirs(MEDIA_FOLDER, exist_ok=True)

app.mount("/media", StaticFiles(directory=MEDIA_FOLDER), name="media")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/posts/", response_model=Post)
def create_post_with_image(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    image_path = os.path.join(MEDIA_FOLDER, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    post = Post(title=title, description=description, image=f"/media/{image.filename}")
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@app.get("/posts/", response_model=List[Post])
def read_posts(session: Session = Depends(get_session)):
    return session.exec(select(Post)).all()

@app.get("/posts/{post_id}", response_model=Post)
def read_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
