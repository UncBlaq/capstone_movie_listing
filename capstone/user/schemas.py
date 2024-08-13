from typing import Optional

from pydantic import BaseModel, ConfigDict

from capstone.movie.schema import Movie


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "123"
            }
        }
    )
class UserResponse(BaseModel):
    username : str
    movies : list[Movie]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "test",
                "movies": [
                    {
                        "title": "Test Movie",
                        "description": "Test Description",
                        "release_date": "2022-01-01",
                    }
                ]
            }
        }
    )
        
class Login(BaseModel):
    username: str
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None



 
  




   