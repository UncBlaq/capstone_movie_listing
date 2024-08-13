from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from capstone.database import db_dependency
from capstone.movie.schema import CreateMovie
from capstone.user.schemas  import Login
from capstone.user.models import User
from capstone.movie.models import Movie as Movie_model
from capstone.authentification.oauth2 import get_current_user
from capstone.movie.models import Rating as RatingModel
from capstone.movie.schema import Rating as RatingSchema
from capstone.movie.schema import Comment as CommentSchema
from capstone.movie.models import Comment as CommentModel
from capstone.movie.schema import ReplyComment

from capstone.movie.service import MovieService


from capstone.logger import get_logger

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
# Enable sending logs from the standard Python logging module to Sentry
logging_integration = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)
sentry_sdk.init(
    dsn="https://ee3ca659cdc5658bf02659af610f818b@o4507693153386496.ingest.de.sentry.io/4507693158629456",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    integrations= [logging_integration]
)

logger = get_logger(__name__)


def list_movie(db : db_dependency, payload : CreateMovie, current_user : Login = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is attempting to list a new movie: {payload.title}")

    user = MovieService.fetch_user(db, current_user)
    MovieService.check_db_description(db, payload)
    new_movie = MovieService.create_new_movie(db, payload, user.id)

    logger.info(f"Movie '{new_movie.title}' has been listed by user {current_user.username} with ID {new_movie.id}.")
    return new_movie


def fetch_movies(db : db_dependency, offset : int = 0, limit : int =10):
    logger.info(f"Fetching movies with offset={offset} and limit={limit}")

    movies = db.query(Movie_model).offset(offset).limit(limit).all()
    logger.info(f"Fetched {len(movies)} movies with offset={offset} and limit={limit}")
    return movies

def fetch_movie_by_id(db : db_dependency, movie_id : int):
    logger.info(f"Fetching movie with ID={movie_id}")
    movie =MovieService.fetch_movie(db, movie_id)

    if movie is None:
        logger.warning(f"Movie with ID={movie_id} not found")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
    logger.info(f"Movie with ID={movie_id} found: {movie.title}")

    return movie


def update_movie(db : db_dependency, movie_id : int, payload : CreateMovie, current_user : Login = Depends(get_current_user)):
    logger.info(f"User '{current_user.username}' is attempting to update movie with ID={movie_id}")

    user = MovieService.fetch_user(db, current_user)
    movie = MovieService.fetch_movie(db, movie_id)
    if movie is None:
        logger.info(f"User '{current_user.username}' is attempting to update movie with ID={movie_id}")
    
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
    MovieService.check_movie_ownership(user, movie)
    MovieService.check_db_description(db, payload)
    movie = MovieService.update_movie_details(movie, payload)
    db.commit()
    logger.info(f"Movie with ID={movie_id} successfully updated by user '{current_user.username}'")
    return movie
   

def delete_movie(db : db_dependency, movie_id : int, current_user : Login = Depends(get_current_user)):
    logger.info(f"User '{current_user.username}' is attempting to delete movie with ID={movie_id}")

    user =MovieService.fetch_user(db, current_user)
    movie =MovieService.fetch_movie(db, movie_id)

    if movie is None:
        logger.warning(f"Movie with ID={movie_id} not found. Deletion operation aborted.")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
    MovieService.ensure_user_can_modify_movie(user, movie)
    db.delete(movie)
    db.commit()
    logger.info(f"Movie with ID={movie_id} successfully deleted by user '{current_user.username}'")

   


def search_movie(db : db_dependency, title : str, offset : int = 0, limit : int =10):
    logger.info(f"Searching for movies with title '{title}' (offset={offset}, limit={limit})")
    movies = db.query(Movie_model).filter(Movie_model.title == title).offset(offset).limit(limit).all()
    if not movies:
        logger.warning(f"No movies found with title '{title}'")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No results found"
        )
    logger.info(f"Found {len(movies)} movie(s) with title '{title}'")
    return movies


def rate_movie(db : db_dependency, payload : RatingSchema, current_user : Login = Depends(get_current_user)):
    logger.info(f"User '{current_user.username}' is attempting to rate movie with ID={payload.movie_id}")

    movie =MovieService.fetch_movie(db, payload.movie_id)
    user =MovieService.fetch_user(db, current_user)
    if movie is None:
        logger.error(f"Movie with ID {payload.movie_id} not found.")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
      # Check if the user has already rated the movie
    MovieService.check_existing_rating(db, user, movie)
    is_invalid_rating = MovieService.check_rating_range(payload.rating)
    if is_invalid_rating:
                    raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Rating must be an integer between 0 and 11"
            )
    else:
        new_rating = RatingModel(
        user_id = user.id,
        movie_id = payload.movie_id,
        rating = payload.rating
            )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        logger.info(f"User {current_user.username} successfully rated movie with ID {payload.movie_id}.")
        return MovieService.average_rating(db, payload.movie_id)


def get_ratings(db : db_dependency, movie_id : int):
    logger.info(f"Fetching ratings for movie with ID={movie_id}")
    movie = MovieService.fetch_movie(db, movie_id)
    if movie is None:
        logger.error(f"Movie with ID {movie_id} not found.")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
    return MovieService.average_rating(db, movie_id)



def comment(db : db_dependency, payload : CommentSchema,  current_user : Login = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is attempting to comment on movie with ID {payload.movie_id}.")
    user = MovieService.fetch_user(db, current_user)
    movie = MovieService.fetch_movie(db, payload.movie_id)
    if movie is None:
        logger.error(f"Movie with ID {payload.movie_id} not found.")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Movie not found"
        )
    logger.info(f"User {current_user.username} successfully commented on movie with ID {payload.movie_id}.")
    new_comment = CommentModel(
        user_id = user.id,
        movie_id = payload.movie_id,
        content = payload.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def fetch_comments(db : db_dependency, movie_id : int, offset : int = 0, limit : int =10):
    logger.info(f"Fetching comments for movie with ID={movie_id}")
    comments = db.query(CommentModel).filter(CommentModel.movie_id == movie_id).offset(offset).limit(limit).all()
    logger.info(f"Found {len(comments)} comments for movie with ID={movie_id}.")
    return comments

def reply_to_comment(db : db_dependency, payload : ReplyComment,  current_user : Login = Depends(get_current_user)):
    logger.info(f"User {current_user.username} is attempting to reply to comment with ID={payload.comment_id}.")

    user = MovieService.fetch_user(db, current_user)
    comment = db.query(CommentModel).filter(CommentModel.id == payload.comment_id).first()
    if comment is None:
        logger.error(f"Comment with ID {payload.comment_id} not found.")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Comment not found"
        )
    movie = MovieService.fetch_movie(db, comment.movie_id)
    logger.info(f"Movie with ID={movie.id} found. Creating reply.")
    new_reply = CommentModel(
                    user_id = user.id,
                    movie_id = movie.id, 
                    content = payload.content,
                    parent_id = payload.comment_id
                )
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)
    logger.info(f"Reply created successfully with ID={new_reply.id} by user ID={user.id} for comment ID={payload.comment_id}.")
    return new_reply           

  

  
    
   
    
   
