from fastapi import APIRouter, HTTPException
from schemas.schemas import UserCreate, UserLogin
from database.models import users
from passlib.context import CryptContext
from database.db import database

router = APIRouter()

# setting up pwd context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(user: UserCreate):
    # Check if email already exists
    query = users.select().where(users.c.email == user.email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Insert new user with role
    query = users.insert().values(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role  # store the string value of the Enum
    )
    await database.execute(query)

    return {
        "message": "User registered successfully",
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

@router.post("/login")
async def login(user: UserLogin):
    # Check user by email
    query = users.select().where(users.c.email == user.email)
    existing_user = await database.fetch_one(query)

    if not existing_user:
        raise HTTPException(status_code=404, detail="Invalid username or password")

    # Verify password
    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(status_code=404, detail="Invalid username or password")

    # Response with user details only
    return {
        "message": "Login successful",
        "user": {
            "name": existing_user["name"],
            "email": existing_user["email"],
            "role": existing_user["role"],
        }
    }
