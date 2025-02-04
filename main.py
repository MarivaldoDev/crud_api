from fastapi import FastAPI, HTTPException, Depends
from database.models.schemas import Message, User, UserPublic, UserUpdate, Token
from http import HTTPStatus
from sqlalchemy.orm import Session
from database.config_db import SessionLocal, engine, Base
from database.banco import UserDB
from security import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI(title="API de Usuários",)



# PÁGINA INICIAL
@app.get("/",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def home():
    return {"message": "A API tá no ar. Acesse /docs para ver a documentação"}


# CRIAR USUÁRIO
@app.post("/users/",
    status_code=HTTPStatus.CREATED,
    response_model=Message
)
def create(user: User, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email já registrado")

    
    new_user = UserDB(**user.model_dump())
    new_user.password = get_password_hash(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"Usuário {user.username} foi CRIADO com sucesso"}


# VER USUÁRIOS
@app.get("/list_users/", status_code=HTTPStatus.OK, response_model=list[UserPublic])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = db.query(UserDB).all()
    
    return users


# ATUALIZAR USUÁRIO
@app.put("/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def update(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Você não tem permissão para atualizar este usuário")
    
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
@app.delete("/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def delete(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Você não tem permissão para deletar este usuário")

    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user_db)
    db.commit()
    
    return {"message": f"Usuário com ID {user_id} foi DELETADO com sucesso"}


@app.post("/token", response_model=Token)
def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_db)):
    
    user = session.query(UserDB).filter(UserDB.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}