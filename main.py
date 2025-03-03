from fastapi import FastAPI
from database.models.schemas import Message
from http import HTTPStatus
from database.config_db import SessionLocal, engine, Base
from routers import users, auth


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="API de Usuários")
app.include_router(users.router)
app.include_router(auth.router)


# PÁGINA INICIAL
@app.get("/",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def home():
    return {"message": "A API tá no ar. Acesse /docs para ver a documentação"}
