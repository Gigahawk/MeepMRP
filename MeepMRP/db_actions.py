from functools import cache

from pony.orm import db_session, select
from fastapi import HTTPException

from MeepMRP.db_models import User, UserGroup, Tag
from MeepMRP.security import password_ctx

__ROOT_TAG_NAME = "__MEEPMRP_TAG_ROOT__"
__ROOT_TAG = None

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

@cache
@db_session
def get_permissions(username: str):
    user = get_user_by_username(username)
    permissions = []
    for group in user.user_groups:
        if group.name == "admin":
            # Add all permissions
            permissions.extend([
                "part_read",
                "part_create",
            ])
    return permissions

def _clean_tag_name(name: str) -> str:
    return name.strip("/")

@db_session
def get_tag_by_name(name: str) -> Tag | None:
    name = _clean_tag_name(name)
    tags = list(select(
        t for t in Tag if t.name == name))
    if not tags:
        return None
    return tags[0]

@db_session
def get_tag_children_by_name(name: str) -> list[Tag]:
    name = _clean_tag_name(name)
    if not name:
        sep_count = -1
    else:
        sep_count = name.count("/")
    tags = list(
        select(
            t for t in Tag
            if t.name.startswith(name)
            # For some reason there's no count attribute?
            #and t.name.count("/") == sep_count + 1)
        )
    )
    tags = [t for t in tags if t.name.count("/") == sep_count + 1]
    return tags

@db_session
def create_tag(name: str):
    name = _clean_tag_name(name)
    if get_tag_by_name(name):
        raise ValueError(f"Tag '{name}' already exists")
    full_path = name.split("/")
    for idx in range(len(full_path)):
        path = "/".join(full_path[0:idx + 1])
        if not get_tag_by_name(path):
            Tag(name=path)

def _ensure_admin_exists():
    if not admin_exists():
        print("MEEPMRP CREATING ADMIN USER, MAKE SURE TO RESET THE PASSWORD")
        create_user("admin", password_ctx.hash("admin"))

def _ensure_starting_state():
    _ensure_admin_exists()

_ensure_starting_state()