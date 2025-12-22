from pydantic import BaseModel
from typing import Optional

class LoginSchema(BaseModel):
    username: str
    password: str

class RegisterSchema(BaseModel):
    username: str
    password: str

class UpdateAccountSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    account_number: str

class UpdateAccountResponse(BaseModel):
    message: str
    username: str