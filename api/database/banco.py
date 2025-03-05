from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from api.database.config_db import Base
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship



class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=func.now()) 
   

    # Relacionamento com Todo
    todos = relationship("Todo", back_populates="user")


class Todo(Base):  # Agora herdando de Base
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    state: Mapped[TodoState] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Relacionamento com UserDB
    user = relationship("UserDB", back_populates="todos")