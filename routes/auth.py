from fastapi import APIRouter, HTTPException, Depends, status
from schemas.schemas import UserCreate , UserLogin
from database.models import users
from passlib.context import CryptContext
from database.db import database
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# keys and parameters for jwt 
SECRET_KEY = "supersecretkey"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# setting up pwd context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Create refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verify token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

@router.post("/register")
async def register(user: UserCreate):
    # Check if email already exists
    query = users.select().where(users.c.email == user.email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Insert new user with role
    query = users.insert().values(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role # store the string value of the Enum
    )
    await database.execute(query)

    return {
        "message": "user registered successfully",
        "name": user.name,
        "email": user.email,
        "role": user.role  # return role in response too
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

    # # Claims for JWT
    # claims = {
    #     "sub": str(existing_user["id"]),
    #     "email": existing_user["email"],
    #     "role": existing_user["role"],
    # }

    # # Tokens
    # access_token = create_access_token(claims)
    # refresh_token = create_refresh_token(claims)

    # Response with tokens + user details
    return {
        "message": "Login successful",
        "user": {
            "name": existing_user["name"],
            "email": existing_user["email"],
            "role": existing_user["role"],
        }
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # New access token
    new_access_token = create_access_token(
        {"sub": payload["sub"], "email": payload["email"], "role": payload["role"]}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user": {
            "id": payload["sub"],
            "email": payload["email"],
            "role": payload["role"],
        }
    }
