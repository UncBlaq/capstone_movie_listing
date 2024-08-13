from fastapi import HTTPException, status
from capstone.user.models import User
from capstone.authentification.hash import Hash
from capstone.authentification.jwt import create_access_token
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


class UserService:

    @staticmethod
    def check_existing_email(db, email: str):
        """Check if an email is already registered in the database.
        
        Args:
            db: The database session.
            email (str): The email address to check.

        Raises:
            HTTPException: If the email is already registered, an exception with 
            status code 400 and a message "Email already exists" is raised.
        """
        db_email = db.query(User).filter(User.email == email).first()
        if db_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    @staticmethod
    def check_existing_username(db, username: str):
        """Check if a username is already taken in the database.
        
        Args:
            db: The database session.
            username (str): The username to check.

        Raises:
            HTTPException: If the username is already taken, an exception with 
            status code 400 and a message "Username already exists" is raised.
        """
        db_username = db.query(User).filter(User.username == username).first()
        if db_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

    @staticmethod
    def create_user(db, payload):
        """Create a new user after hashing the password.
        
        Args:
            db: The database session.
            payload: The data required to create a new user, including email, username, 
            and password.

        Returns:
            User: The newly created user object after being added to the database.
        """
        # Hash the user's password for secure storage
        hashed_password = Hash.bcrypt(payload.password)
        
        # Create a new user object with the hashed password
        new_user = User(
            email=payload.email,
            username=payload.username,
            password=hashed_password
        )
        
        # Add the new user to the database and commit the transaction
        db.add(new_user)
        db.commit()
        
        # Refresh the session to reflect the changes in the new user object
        db.refresh(new_user)
        
        return new_user

    @staticmethod
    def get_user_by_username(db, username: str):
        """Retrieve a user by their username from the database.
        
        Args:
            db: The database session.
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object if found.

        Raises:
            HTTPException: If the user is not found, an exception with 
            status code 404 and a message "Invalid credentials" is raised.
        """
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid credentials"
            )
        return user

    @staticmethod
    def verify_password(provided_password: str, stored_password: str):
        """Verify the provided password against the stored hashed password.
        
        Args:
            provided_password (str): The password provided by the user during login.
            stored_password (str): The hashed password stored in the database.

        Raises:
            HTTPException: If the provided password does not match the stored password, 
            an exception with status code 401 and a message "Incorrect password" is raised.
        """
        if not Hash.verify(provided_password, stored_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

