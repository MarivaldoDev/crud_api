from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.banco import UserDB
from security import verify_password, create_access_token, get_current_user
from database.config_db import get_db
from database.models.schemas import Token



router = APIRouter(prefix="/auth", tags=["auth"])
T_Session = Annotated[Session, Depends(get_db)]
T_Oauth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/token", response_model=Token)
def login_for_token(session: T_Session, form_data: T_Oauth2Form):
    
    user = session.query(UserDB).filter(UserDB.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
def refresh_access_token(user: UserDB = Depends(get_current_user)):
    new_access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": new_access_token, "token_type": "bearer"}