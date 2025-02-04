from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None


class Token(BaseModel):
    access_token: str
    token_type: str
