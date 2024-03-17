from contextlib import asynccontextmanager
from typing import  Annotated
from api import settings
from sqlmodel import  Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends
from .models import *

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql","postgresql+psycopg" 
)

engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Creating tables...')
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Todo app with db",
              version="0.0.1",
              servers=[
                  {
                      "url": "http://0.0.0.0:8000",
                      "description": "Development server"
                  }
              ]
              )

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/", response_model=Task)
def create_task(task: Task, session: Annotated[Session, Depends(get_session)]):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/todos/", response_model=list[Task])
def read_tasks(session: Annotated[Session, Depends(get_session)]):
    tasks = session.exec(select(Task)).all()
    return tasks