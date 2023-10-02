### Film schema ###

def film_schema(film,rating) -> dict:
    return {"id": str(film["_id"]),
            "primaryTitle": film["primaryTitle"],
            "startYear": int(film["startYear"]),
            "runtimeMinutes": film["runtimeMinutes"],
            "genres": film["genres"],
            "averageRating": rating["averageRating"],
            "numVotes": rating.get("numVotes",None)}



def films_schema(films,ratings) -> list:
    return [film_schema(film,rating) for film,rating in zip(films,ratings)]
