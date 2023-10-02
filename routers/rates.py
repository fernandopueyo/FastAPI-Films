from fastapi import Depends, APIRouter, HTTPException, status, Security
from fastapi.security import SecurityScopes

from db.client import db_client
from routers.users import get_current_active_user
from db.models.user import User, UserDB
from routers.films import search_film

from bson import ObjectId
import pymongo
from typing import Annotated


router = APIRouter(prefix="/rates",
                   tags=["rates"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})



@router.get("/rate/{id}")
async def vote_film(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["rates"])],
    id: str
):
    film = search_film("_id", ObjectId(id))
    
    return [{"item_id": "Foo", "owner": current_user.username}]