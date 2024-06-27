from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from MeepMRP.db_actions import (
    admin_exists, user_exists, create_user, authenticate_user
)
from MeepMRP.pydantic_models import User, Token, ServerInfo
from MeepMRP.security import password_ctx, get_token, get_user_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/info")
async def get_server_info() -> ServerInfo:
    return ServerInfo(api_version=0)

@app.get("/users/me")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    #if token == "0":
    #    return User(username="")
    username = get_user_from_token(token)
    if not user_exists(username):
        raise HTTPException(status_code=401, detail="Invalid access token")
    return User(username=username)

@app.post("/add_user")
async def add_user(
        user: User,
        current_user: Annotated[User, Depends(get_current_user)]):
    if user.password_hash is None:
        user.password_hash = password_ctx.hash(user.password)
    else:
        # TODO: auth
        raise HTTPException(
            status_code=401,
            detail=f"Must be logged in as admin to create accounts: {user}")
    return {"message": "success"}

@app.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    token = get_token(user.username)
    return Token(access_token=token, token_type="bearer")
