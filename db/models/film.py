### User model ###

from pydantic import BaseModel
from typing import Optional, Union


class Film(BaseModel):
    id: Optional[str]
    # tconst: Optional[str]
    # titleType: Optional[str]
    primaryTitle: Optional[str]
    # originalTitle: Optional[str]
    # isAdult: Optional[int]
    startYear: Optional[Union[int, float]]
    # endYear: None
    runtimeMinutes: Optional[str]
    genres: Optional[str]
    averageRating: Optional[Union[int, float]]
    numVotes: Optional[int] = None

