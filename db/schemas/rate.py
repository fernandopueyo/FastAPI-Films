### Rating schema ###

def rate_schema(user_rate) -> dict:
    return {"id": str(user_rate["_id"]),
            "film_id": user_rate["film_id"],
            "primaryTitle": user_rate["primaryTitle"],
            "user_id": user_rate["user_id"],
            "username": user_rate["username"],
            "rate": user_rate["rate"]} 

def rates_schema(rates) -> list:
    return [rate_schema(rate) for rate in rates]