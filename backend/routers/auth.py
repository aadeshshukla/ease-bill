from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
_USERS: dict[str, str] = {}


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(payload: RegisterRequest) -> dict[str, str]:
    if payload.email in _USERS:
        raise HTTPException(status_code=400, detail="User already exists")

    _USERS[payload.email] = payload.password
    return {"message": "User registered successfully"}


@router.post("/login")
def login(payload: LoginRequest) -> dict[str, str]:
    password = _USERS.get(payload.email)
    if password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": f"token-{payload.email}", "token_type": "bearer"}
