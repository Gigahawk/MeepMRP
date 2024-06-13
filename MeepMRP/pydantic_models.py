from pydantic import BaseModel

class User(BaseModel):
    username: str
    # TODO: ALWAYS REQUIRE HASHING OF PASSWORD LOCALLY
    password: str | None = None
    password_hash: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str