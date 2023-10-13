
from fastapi import APIRouter, HTTPException, status, Security
from db.models.film import Film
from db.schemas.film import film_schema, films_schema
from db.schemas.rate import rate_schema
from db.models.user import User
from db.models.rate import Rate
from db.client import db_client
from routers.users import get_current_active_user
from bson import ObjectId
from typing import Annotated
import pymongo

router = APIRouter(prefix="/films",
                   tags=["films"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# , response_model=list[Film])

@router.get("/", response_model=list[Film])
async def films():
    return show_films(10)

@router.get('/name/{name}', response_model=list[Film])
async def film_name(name: str):
    return search_films('primaryTitle', name)

@router.get('/id/{id}', response_model=Film)
async def film_id(id: str):
    return search_film("_id", ObjectId(id))

@router.get("/top{limit}", response_model=list[Film])
async def top_films(limit:int = 10):
    return top_rating_films(limit)

@router.post("/id/{id}/", response_model=Rate)
async def rating_film(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["rates"])],
    id: str,
    rate: float
):
    if db_client.rates.find_one({"film_id": id, "user_id": str(current_user.id)}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Rate already exists")
    film = search_film("_id", ObjectId(id))
    user_rate_dict = {"film_id": str(film.id),
                      "primaryTitle": film.primaryTitle,
                      "user_id": str(current_user.id),
                      "username": current_user.username,
                      "rate": rate}
    id_rate = db_client.rates.insert_one(user_rate_dict).inserted_id
    new_rate = rate_schema(db_client.rates.find_one({"_id":id_rate}))
    return Rate(**new_rate)

@router.put("/id/{id}/", response_model=Rate)
async def rating_film(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["rates"])],
    id: str,
    rate: float
):
    modified_rate = db_client.rates.find_one_and_update({"film_id": id, "user_id": str(current_user.id)},
                                                        {"$set": {"rate": rate}},
                                                        return_document=pymongo.ReturnDocument.AFTER)
    return Rate(**modified_rate)

def search_film(field: str, key):
    try:
        film = db_client.films.find_one({field: key})
        rating = db_client.ratings.find_one({'tconst': film['tconst']})
        if rating == None:
            rating = {'averageRating': None}
        return Film(**film_schema(film,rating))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Film does not exist")
    
def search_films(field: str, key):
    try:
        regex_pattern = f".*{key}.*"
        films = db_client.films.find({field: {"$regex": regex_pattern, "$options": "i"}})
        films_list = list(films.clone())
        default_rating = {'averageRating': None}
        ratings = [db_client.ratings.find_one({'tconst': film['tconst']}) if db_client.ratings.find_one({'tconst': film['tconst']}) != None else default_rating for film in films]
        return [Film(**film) for film in films_schema(films_list,ratings)]
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Film does not exist")
    
def show_films(limit: int):
    films = db_client.films.find().limit(limit)
    films_list = list(films.clone())
    default_rating = {'averageRating': None}
    ratings = [db_client.ratings.find_one({'tconst': film['tconst']}) if db_client.ratings.find_one({'tconst': film['tconst']}) != None else default_rating for film in films]
    return [Film(**film) for film in films_schema(films_list,ratings)]

def top_rating_films(limit: int == 10):
    min_votes = 20000
    pipeline = [
    {
        "$match": {
            "numVotes": {"$gte": min_votes} 
        }
    },
    {
        "$sort": {
            "averageRating": pymongo.DESCENDING 
        }
    },
    {
        "$limit": limit 
    }]
    ratings = db_client.ratings.aggregate(pipeline)
    ratings_list = list(ratings)
    film_ids = [rating['tconst'] for rating in ratings_list]
    films = db_client.films.find({"tconst": {"$in": film_ids}})
    default_film = {"id": None,
                    "primaryTitle": None,
                    "startYear": None,
                    "runtimeMinutes": None,
                    "genres": None}
    film_data = [film if film is not None else default_film for film in films]
    return [Film(**film) for film in films_schema(film_data,ratings_list)]

