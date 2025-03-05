from fastapi import FastAPI, Request
from api.database.models.schemas import Message
from http import HTTPStatus
from api.database.config_db import SessionLocal, engine, Base
from api.routers import users, auth, todos
from pathlib import Path
from fastapi.templating import Jinja2Templates


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
app.include_router(todos.router)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# PÁGINA INICIAL
@app.get("/",
    status_code=HTTPStatus.OK,
    response_model=Message
)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
