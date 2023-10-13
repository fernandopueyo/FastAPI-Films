
from fastapi import Depends, APIRouter, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer, 
    OAuth2PasswordRequestForm,
    SecurityScopes
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from datetime import datetime, timedelta
from typing import Annotated

from keys.user import security
from db.models.user import User, UserDB
from db.models.token import Token, TokenData
from db.models.rate import Rate
from db.schemas.user import user_schema
from db.schemas.rate import rate_schema, rates_schema
from db.client import db_client
from bson import ObjectId
import pymongo

router = APIRouter(prefix="/users",
                   tags=["users"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = security.SECRET_KEY
ALGORITHM = security.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = security.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", 
            "items": "Read items.",
            "rates": "Rate films.",
            "admin": "Delete users."}
    )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_dict = db_client.users.find_one({"username": username})
    if user_dict is not None:
        return UserDB(**user_schema(user_dict))
    
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError) as error:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value}
            )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@router.get("/me/rates", response_model=list[Rate])
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["rates"])]
):
    rates = db_client.rates.find({"user_id": str(current_user.id)})
    return [Rate(**rate) for rate in rates_schema(rates)]

@router.get("/status")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserDB):
    if db_client.users.find_one({"$or": [{"username": user.username}, {"email": user.email}]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user.hashed_password = get_password_hash(user.hashed_password)
    del user.id
    user_dict = dict(user)
    id = db_client.users.insert_one(user_dict).inserted_id
    new_user = user_schema(db_client.users.find_one({"_id":id}))
    return UserDB(**new_user)

@router.put("/me", response_model=User, status_code=status.HTTP_200_OK)
async def edit_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    modify_user: UserDB
):
    modify_user.hashed_password = get_password_hash(modify_user.hashed_password)
    del modify_user.id
    modify_user = dict(modify_user)
    modified_user = db_client.users.find_one_and_update({"_id": ObjectId(current_user.id)},
                                                         {"$set": modify_user},
                                                         return_document=pymongo.ReturnDocument.AFTER)
    return UserDB(**user_schema(modified_user))


@router.delete("/delete/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def delete_user(
    id: str,
    current_user: Annotated[User, Security(get_current_active_user, scopes=["admin"])]
):
    deleted_user = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    if not deleted_user:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )
    return User(**user_schema(deleted_user))
