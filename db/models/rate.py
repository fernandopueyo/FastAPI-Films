from pydantic import BaseModel
from typing import Optional, Union

class Rate(BaseModel):
    id: str | None = None
    film_id: str
    primaryTitle: str
    user_id: str
    username: str
    rate: Union[int, float]
