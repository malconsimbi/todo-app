"""
Full-Stack To-Do App — FastAPI Backend
Python 3.8+  |  Run: uvicorn main:app --reload --port 8000
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SECRET_KEY = "CHANGE-ME-IN-PRODUCTION-use-secrets-module"  # noqa: S105
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------
# { username: {"hashed_password": str, "email": str} }
users_db: Dict[str, dict] = {}

# { todo_id: {"id": str, "title": str, "completed": bool, "owner": str} }
todos_db: Dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("username cannot be blank")
        if len(v) < 3:
            raise ValueError("username must be at least 3 characters")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TodoCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: str
    title: str
    completed: bool
    owner: str


class ProtectedResponse(BaseModel):
    message: str
    username: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        logger.warning("Invalid or expired token received")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    if username not in users_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return username


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="To-Do API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    logger.info("POST /register — username=%s", body.username)
    if body.username in users_db:
        logger.warning("Register failed — username already exists: %s", body.username)
        raise HTTPException(status_code=409, detail="Username already taken")
    users_db[body.username] = {
        "hashed_password": hash_password(body.password),
        "email": body.email,
    }
    logger.info("User registered: %s", body.username)
    return {"message": "User created successfully"}


@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    logger.info("POST /login — username=%s", body.username)
    user = users_db.get(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        logger.warning("Login failed for username=%s", body.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(
        {"sub": body.username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("Login successful: %s", body.username)
    return TokenResponse(access_token=token)


@app.get("/protected", response_model=ProtectedResponse)
def protected(current_user: str = Depends(get_current_user)):
    logger.info("GET /protected — user=%s", current_user)
    return ProtectedResponse(message="Access granted", username=current_user)


# ---------------------------------------------------------------------------
# To-Do routes (all protected)
# ---------------------------------------------------------------------------

@app.get("/todos", response_model=List[TodoResponse])
def list_todos(current_user: str = Depends(get_current_user)):
    logger.info("GET /todos — user=%s", current_user)
    return [t for t in todos_db.values() if t["owner"] == current_user]


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(body: TodoCreate, current_user: str = Depends(get_current_user)):
    logger.info("POST /todos — user=%s title=%s", current_user, body.title)
    todo_id = str(uuid.uuid4())
    todo = {"id": todo_id, "title": body.title, "completed": False, "owner": current_user}
    todos_db[todo_id] = todo
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, body: TodoUpdate, current_user: str = Depends(get_current_user)):
    logger.info("PATCH /todos/%s — user=%s", todo_id, current_user)
    todo = todos_db.get(todo_id)
    if not todo or todo["owner"] != current_user:
        raise HTTPException(status_code=404, detail="Todo not found")
    if body.title is not None:
        todo["title"] = body.title.strip()
    if body.completed is not None:
        todo["completed"] = body.completed
    todos_db[todo_id] = todo
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str, current_user: str = Depends(get_current_user)):
    logger.info("DELETE /todos/%s — user=%s", todo_id, current_user)
    todo = todos_db.get(todo_id)
    if not todo or todo["owner"] != current_user:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos_db[todo_id]