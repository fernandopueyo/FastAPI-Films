from pydantic import BaseModel
from typing import Optional, Union


class User(BaseModel):
    id: str | None = None
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False

class UserDB(User):
    hashed_password: str | None = None

