from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from capstone.database import db_dependency
from capstone.user.schemas import SignUpModel, UserResponse
import capstone.user.crud as crud 


user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@user_router.post("/signup", response_model= UserResponse, status_code= status.HTTP_201_CREATED)
def sign_up(db : db_dependency, payload : SignUpModel):

    """
    ## Creates a user
    Requires the following
    ```
    username : str
    email : str 
    password : str
    ```
    """
        
    return crud.sign_up(db, payload)

@user_router.post("/auth/login", status_code= status.HTTP_200_OK)
def login(db : db_dependency, payload : OAuth2PasswordRequestForm = Depends()):

    """
    ## Login a user
    Requires the following
    ```
    username : str
    password : str
    ```
    and returns a token pair 'access' 
    """

    return crud.login(db, payload)
