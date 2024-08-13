from pydantic import BaseModel
from datetime import datetime


class Movie(BaseModel):
    id: int
    title: str
    description: str
    release_date: datetime
    updated_at: datetime
    
class CreateMovie(BaseModel):
    title: str
    description: str


class Rating(BaseModel):
    rating: int
    movie_id : int

class Comment(BaseModel):
    content: str
    movie_id: int 

class CommentResponse(Comment):
    content: str
    movie_id: int 
    parent_id: int | None

class ReplyComment(BaseModel):
    content: str
    comment_id: int


