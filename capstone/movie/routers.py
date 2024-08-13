from fastapi import APIRouter, Depends, status


from capstone.movie.schema import Movie, CreateMovie
from capstone.user.schemas import Login
from capstone.database import db_dependency
from capstone.authentification.oauth2 import get_current_user
import capstone.movie.crud as crud
from capstone.database import db_dependency
from capstone.movie.schema import Rating as RatingSchema
from capstone.movie.schema import Comment as CommentSchema
from capstone.movie.schema import CommentResponse
from capstone.movie.schema import ReplyComment 



movie_router = APIRouter(
    prefix= "/movie",
    tags= ["Movie"]
)

@movie_router.post("/", response_model = Movie, status_code = status.HTTP_201_CREATED)
def list_movie(db : db_dependency, payload : CreateMovie, current_user : Login = Depends(get_current_user)):

    """
    ## Listing a movie
    This requires the folowing
    - title : str
    - description : str
    """
    return crud.list_movie(db , payload , current_user)

@movie_router.get("/", response_model= list[Movie])
def fetch_movies(db : db_dependency):
    """
    ## Fetch all movies
    This lists all movies in database and can be accessed by the public
    """

    return crud.fetch_movies(db)

@movie_router.get("/{id}", response_model = Movie)
def fetch_movie(db : db_dependency, id : int):
    """
    ## Fetch a movie by id
    This fetches a movie by its id and can be accessed by the public
    """
    return crud.fetch_movie_by_id(db, id)


@movie_router.put("/{id}", response_model = Movie)
def update_movie(db : db_dependency, id : int, payload : CreateMovie, current_user : Login = Depends(get_current_user)):
    """
    ## Update a movie by id
    This updates a movie by its id and can only be executed by the owner
    """
    return crud.update_movie(db, id, payload, current_user)

@movie_router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_movie(db : db_dependency, id : int, current_user : Login = Depends(get_current_user)):
    """
    ## Delete a movie by id
    This deletes a movie by its id and can only be executed by the owner
    """
    return crud.delete_movie(db, id, current_user)

@movie_router.get("/search/{title}", response_model= list[Movie])
def search_movie(db : db_dependency, title : str):
    """
    ## Search for a movie by title
    This searches for movies by their title and can be accessed by the public
    """
    return crud.search_movie(db, title)

@movie_router.post("/{movie_id}/rate", status_code= status.HTTP_201_CREATED)
def rate_movie(db : db_dependency, payload : RatingSchema, current_user : Login = Depends(get_current_user)):
    """
    ## Rate a movie by id
    This rates a movie by its id and can only be executed a registered users once
    """
    return crud.rate_movie(db, payload, current_user)


@movie_router.get("/{movie_id}/ratings")
def fetch_ratings(db : db_dependency, movie_id : int):
    """
    ## Get ratings for a movie by id
    This fetches ratings for a movie by its id and can be accessed by the public
    """
    return crud.get_ratings(db, movie_id)

@movie_router.post("/{id}/comment", response_model= CommentResponse, status_code=status.HTTP_201_CREATED)
def comment(db : db_dependency, payload : CommentSchema,  current_user : Login = Depends(get_current_user)):
    """
    ## Comment on a movie by id
    This comments on a movie by its id and can only be executed registered users
    """
    return crud.comment(db, payload, current_user)

@movie_router.get("/{movie_id}/comments")
def fetch_comments(db : db_dependency, movie_id : int):
    """
    ## Get comments for a movie by id
    This fetches comments for a movie by its id and can be accessed by the public
    """

    return crud.fetch_comments(db, movie_id)

@movie_router.post("/{comment_id}/reply")
def reply_to_comment(db : db_dependency, payload : ReplyComment,  current_user : Login = Depends(get_current_user)):
    """
    ## Reply to a comment by id
    This replies to a comment by its id and can only be executed registered users
    """
    return crud.reply_to_comment(db, payload, current_user)

    

