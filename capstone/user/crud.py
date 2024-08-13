from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from capstone.database import db_dependency
from capstone.user.schemas import SignUpModel
from capstone.authentification.hash import Hash
from capstone.user.models import User 
from capstone.authentification.jwt import create_access_token
from capstone.user.service import UserService

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




def sign_up(db : db_dependency, payload : SignUpModel):
    logger.info("Creating a new user: %s", payload.username)

    UserService.check_existing_email(db, payload.email)
    UserService.check_existing_username(db, payload.username)
    
    hashed_password = Hash.bcrypt(payload.password)
    new_user = User(
        email = payload.email,
        username = payload.username,
        password = hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User {payload.username} has been created")
    return new_user


def login(db : db_dependency, payload : OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for user: {payload.username}")

        # Fetch the user, and handle "user not found" error
    user = UserService.get_user_by_username(db, payload.username)
    logger.info(f"User found: {payload.username}")

        # Verify the password, and handle "incorrect password" error
    UserService.verify_password(payload.password, user.password)
    logger.info(f"Password verified for user: {payload.username}")

    access_token =  create_access_token(data = {
        "sub" : user.username
    })
    logger.info(f"User {payload.username} logged in successfully")
    
    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }