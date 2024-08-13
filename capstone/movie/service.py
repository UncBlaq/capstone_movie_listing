from datetime import datetime, timezone
from fastapi import HTTPException, status

from capstone.movie.models import Rating as RatingModel
from capstone.logger import get_logger
from capstone.movie.models import Movie
from capstone.user.models import User

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

class MovieService:

    # Creates a new movie entry in the database
    def create_new_movie(db, payload, user_id):
        # Initialize a new movie instance with the provided payload and user_id
        new_movie = Movie(
            title=payload.title,
            description=payload.description,
            release_date=datetime.now(timezone.utc),  # Set the release date to the current time in UTC
            updated_at=datetime.now(timezone.utc),    # Set the updated_at field to the current time in UTC
            user_id=user_id  # Associate the movie with the user who created it
        )
        db.add(new_movie)  # Add the new movie instance to the database session
        db.commit()  # Commit the session to save the movie in the database
        db.refresh(new_movie)  # Refresh the instance with the latest data from the database
        return new_movie  # Return the newly created movie instance

    # Calculates and returns the average rating for a movie
    def average_rating(db, movie_id) -> str:
        # Query the database for all ratings associated with the given movie ID
        ratings = db.query(RatingModel).filter(RatingModel.movie_id == movie_id).all()
        if not ratings:  # If no ratings are found, raise a 404 error
            logger.warning(f"No ratings found for movie with ID {movie_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ratings found for this movie"
            )
        # Extract rating values directly from the ORM objects
        rating_values = [rating.rating for rating in ratings]
        logger.info(f"Ratings for movie with ID {movie_id} retrieved successfully.")
        # Calculate the sum of rating values and the number of ratings
        total_rating = sum(rating_values)
        len_ratings = len(rating_values)

        # Return the average rating as a string formatted to one decimal place
        return (f"average_rating : {total_rating / len_ratings:.1f}")

    # Fetches the user from the database based on the current session's user
    def fetch_user(db, current_user) -> str:
        # Query the database for a user with the same username as the current user
        user = db.query(User).filter(User.username == current_user.username).first()
        return user  # Return the user instance

    # Fetches the movie from the database based on the given movie ID
    def fetch_movie(db, movie_id) -> str:
        # Query the database for a movie with the given movie ID
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        return movie  # Return the movie instance

    # Checks if the user has already rated the movie
    def check_existing_rating(db, user, movie) -> str:
        # Query the database for an existing rating from the user for the given movie
        existing_rating = db.query(RatingModel).filter(
            RatingModel.movie_id == movie.id,
            RatingModel.user_id == user.id
        ).first()
        if existing_rating:  # If a rating already exists, raise a 400 error
            logger.warning(f"User has already rated movie with ID {movie.id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already rated this movie"
            )

    # Checks if a movie with the same description already exists in the database
    def check_db_description(db, payload) -> str:
        # Query the database for a movie with the same description as the provided payload
        db_description = db.query(Movie).filter(Movie.description == payload.description).first()
        if db_description:  # If a matching movie is found, raise a 406 error
            logger.warning("Listing failed for user, A movie with a similar description already exists.")
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Similar Movie already exists, Contact Support to make complaints."
            )

    # Validates the rating value to ensure it is within the acceptable range (1 to 10)
    def check_rating_range(rating) -> bool:
        # Check if the rating is outside the acceptable range
        if rating not in range(1, 10):
            logger.error(f"Invalid rating value: {rating}. Must be an integer between 1 and 10.")
            return True  # Return True if the rating is invalid
        else:
            return False  # Return False if the rating is valid

    # Checks if the current user is the owner of the movie
    def check_movie_ownership(user, movie):
        # Compare the user's ID with the movie's user_id to verify ownership
        if user.id != movie.user_id:
            logger.warning(f"User '{user.username}' is not authorized to update movie with ID={movie.id}. Forbidden action.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this movie"
            )

    # Updates the details of a movie with the new payload data
    def update_movie_details(movie, payload):
        movie.title = payload.title  # Update the movie's title
        movie.description = payload.description  # Update the movie's description
        movie.updated_at = datetime.now(timezone.utc)  # Update the movie's updated_at field to the current time
        return movie  # Return the updated movie instance

    # Ensures that the current user is authorized to modify the movie
    def ensure_user_can_modify_movie(user, movie):
        # Check if the user is not the owner of the movie
        if user.id != movie.user_id:
            logger.warning(f"User '{user.username}' is not authorized to modify movie with ID={movie.id}.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this movie"
            )


