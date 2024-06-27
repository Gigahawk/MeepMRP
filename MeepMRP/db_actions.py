from pony.orm import db_session, select

from fastapi import HTTPException

from MeepMRP.db_models import User, UserGroup
from MeepMRP.security import password_ctx

@db_session
def get_user_by_username(username: str) -> User | None:
    users = list(select(u for u in User if u.username == username))
    if not users:
        return None
    return users[0]

@db_session
def get_group_by_name(group: str) -> UserGroup | None:
    groups = list(select(g for g in UserGroup if g.name == group))
    if not groups:
        return None
    return groups[0]

def user_exists(username: str) -> bool:
    return bool(get_user_by_username(username))

@db_session
def get_or_create_group(name: str) -> UserGroup:
    group = get_group_by_name(name)
    if group is None:
        group = UserGroup(name=name)
    return group

@db_session
def create_user(username: str, password_hash: str) -> User:
    user_group = get_or_create_group(username)
    if user_exists(username):
        raise ValueError(f"User '{username}' already exists")
    return User(
        username=username, password_hash=password_hash,
        user_groups=(user_group,)
    )

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
