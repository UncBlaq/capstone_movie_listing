from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import capstone.authentification.jwt as jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "user/auth/login")

def get_current_user(data : str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return jwt.verify_token(data, credentials_exception)