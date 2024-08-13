from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from capstone.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable = False)
    email = Column(String, unique=True, index=True, nullable = False)
    password = Column(Text)


    movies = relationship("Movie", back_populates="owner")
    ratings = relationship("Rating", back_populates="owner")
    comments = relationship("Comment", back_populates="owner")

    def __repr__(self):
        return f'<User(id={self.id}, username="{self.username}")>'