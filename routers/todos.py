from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from database.config_db import get_db
from typing import Annotated
from http import HTTPStatus 
from sqlalchemy.orm import Session
from database.banco import UserDB, Todo
from sqlalchemy import select
from security import get_current_user
from database.models.schemas import TodoPublic, TodoSchema, TodoList, Message, TodoUpdate


router = APIRouter(prefix="/todos", tags=["todos"])
T_Session = Annotated[Session, Depends(get_db)]
T_User = Annotated[UserDB, Depends(get_current_user)]


@router.post("/", response_model=TodoPublic)
def create_todo(user: T_User, session: T_Session, todo: TodoSchema):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo

@router.get("/", response_model=TodoList)
def list_todos(
    session: T_Session,
    user: T_User,
    title: str | None = None,
    description: str | None = None,
    state: str | None = None,
    offset: int | None = None,
    limit: int | None = None
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))

    if description:
        query = query.filter(Todo.description.contains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {"todos": todos}


@router.delete("/{todo_id}", response_model=Message)
def delete_todo(todo_id: int, session: T_Session, user: T_User):
    todo = session.scalar(select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found")


    session.delete(todo)
    session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{todo_id}", response_model=TodoPublic)
def patch_todo(todo_id: int, session: T_Session, user: T_User, todo: TodoUpdate):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo