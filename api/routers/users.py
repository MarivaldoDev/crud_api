from fastapi import APIRouter
from fastapi import HTTPException, Depends
from api.database.models.schemas import Message, User, UserPublic, UserUpdate
from api.database.banco import UserDB
from sqlalchemy.orm import Session
from http import HTTPStatus
from typing import Annotated
from api.security import get_password_hash, verify_password, create_access_token, get_current_user
from api.database.config_db import get_db


router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_db)]
T_CurrentUser = Annotated[UserDB, Depends(get_current_user)]

# CRIAR USUÁRIO
@router.post("/",
    status_code=HTTPStatus.CREATED,
    response_model=Message
)
def create(user: User, db: T_Session):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email já registrado")

    
    new_user = UserDB(**user.model_dump())
    new_user.password = get_password_hash(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"Usuário {user.username} foi CRIADO com sucesso"}


# VER USUÁRIOS
@router.get("/list_users/", status_code=HTTPStatus.OK, response_model=list[UserPublic])
def list_users(db: T_Session, current_user: T_CurrentUser):
    users = db.query(UserDB).all()
    
    return users


@router.put("/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def update(user_id: int, user: UserUpdate, db: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Você não tem permissão para atualizar este usuário")
    
    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in user.model_dump(exclude_unset=True).items():
        if key == "password":
            value = get_password_hash(value)
        setattr(user_db, key, value)

    db.commit()
    db.refresh(user_db)
    
    return {"message": f"Usuário com ID {user_id} foi ATUALIZADO com sucesso"}


# DELETAR USUÁRIO
@router.delete("/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def delete(user_id: int, db: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Você não tem permissão para deletar este usuário")

    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user_db)
    db.commit()
    
    return {"message": f"Usuário com ID {user_id} foi DELETADO com sucesso"}
