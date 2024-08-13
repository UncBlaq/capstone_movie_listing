from fastapi import FastAPI

from capstone.user.routers import user_router
from capstone.movie.routers import movie_router
import capstone.user.models as user_models
import capstone.movie.models as movie_models
from capstone.database import engine

app = FastAPI()


user_models.Base.metadata.create_all(bind = engine)
movie_models.Base.metadata.create_all(bind = engine)


app.include_router(user_router)
app.include_router(movie_router)


