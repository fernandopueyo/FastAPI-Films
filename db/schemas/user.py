### User schema ###

def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "disabled": user.get("disabled",False),
            "hashed_password": user["hashed_password"]}

