from pony.orm import db_session, select

from fastapi import HTTPException

from MeepMRP.db_models import User
from MeepMRP.security import password_ctx

@db_session
def get_user_by_username(username: str) -> User:
    return list(select(u for u in User if u.username == username))[0]

def user_exists(username: str) -> bool:
    try:
        get_user_by_username(username)
        return True
    except IndexError:
        return False

@db_session
def create_user(username: str, password_hash: str):
    if user_exists(username):
        raise ValueError(f"User '{username}' already exists")
    User(username=username, password_hash=password_hash)

def admin_exists() -> bool:
    return user_exists("admin")

@db_session
def authenticate_user(username: str, password: str) -> User:
    err = HTTPException(
        status_code=401, detail="Invalid username or password")
    try:
        user = get_user_by_username(username)
    except IndexError:
        raise err
    if password_ctx.verify(password, user.password_hash):
        return user
    raise err

def _ensure_admin_exists():
    if not admin_exists():
        print("CREATING ADMIN USER, MAKE SURE TO RESET THE PASSWORD")
        create_user("admin", password_ctx.hash("admin"))

_ensure_admin_exists()
