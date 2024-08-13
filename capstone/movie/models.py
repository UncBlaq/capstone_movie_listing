from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from capstone.database import Base


class Movie(Base):

    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    release_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc ))
    user_id = Column(Integer, ForeignKey("users.id"))
   
    owner = relationship("User", back_populates="movies")
    ratings = relationship("Rating", back_populates="movies")
    comments = relationship("Comment", back_populates="movies")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Integer)
  
    owner = relationship("User", back_populates="ratings")
    movies = relationship("Movie", back_populates="ratings")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text)
 

    owner = relationship("User", back_populates="comments")
    movies = relationship("Movie", back_populates="comments")
    parent = relationship("Comment", remote_side= [id], backref = "replies")


