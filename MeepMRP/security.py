from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

# TODO: real secure key
_jwt_secret = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
_jwt_algo = "HS256"
_jwt_expiry = 30

password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_token(username: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(days=_jwt_expiry)
    data = {
        "exp": expiry,
        "user": username
    }
    print(data)
    return jwt.encode(data, _jwt_secret, algorithm=_jwt_algo)

def get_user_from_token(token: str) -> str | None:
    payload = jwt.decode(token, _jwt_secret, algorithms=[_jwt_algo])
    username: str = payload.get("user", None)
    return username


