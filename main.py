from fastapi import FastAPI, HTTPException, Depends
from database.models.schemas import Message, User, UserPublic, UserUpdate
from http import HTTPStatus
from sqlalchemy.orm import Session
from database.config_db import SessionLocal, engine, Base
from database.banco import UserDB


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI()



# PÁGINA INICIAL
@app.get("/",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def home():
    return {"message": "A API tá no ar"}


# CRIAR USUÁRIO
@app.post("/users/",
    status_code=HTTPStatus.CREATED,
    response_model=Message
)
def create(user: User, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    new_user = UserDB(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"Usuário {user.username} foi CRIADO com sucesso"}


# VER USUÁRIOS
@app.get("/list_users/", status_code=HTTPStatus.OK, response_model=list[UserPublic])
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    
    return users


# ATUALIZAR USUÁRIO
@app.put("/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def update(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    user_email = db.query(UserDB).filter(UserDB.email == user.email).first()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    elif user_email:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(user_db, key, value)
    
    user_update = db.query(UserDB).filter(UserDB.id == user_id).first()

    db.commit()
    db.refresh(user_update)
    
    return {"message": f"Usuário com ID {user_id} foi ATUALIZADO com sucesso"}


# DELETAR USUÁRIO
@app.delete("/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def delete(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(user_db)
    db.commit()
    
    return {"message": f"Usuário com ID {user_id} foi DELETADO com sucesso"}