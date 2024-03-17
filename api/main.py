from contextlib import asynccontextmanager
from typing import  Annotated
from api import settings
from sqlmodel import  Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, HTTPException
from .models import *

# getting connection string from settings
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql","postgresql+psycopg" 
)

# create engine based on connectin string
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)

# Create all tables based on metadata of SQLModel function
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Creating tables...')
    create_db_and_tables()
    yield

# Creating app based on FastAPI with lifespan function
app = FastAPI(lifespan=lifespan, title="Todo app with db",
              version="0.0.1",
              servers=[
                  {
                      "url": "http://0.0.0.0:8000",
                      "description": "Development server"
                  }
              ]
              )

# Create session
def get_session():
    with Session(engine) as session:
        yield session


# Root api for server testing
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Create task
@app.post("/todos/", response_model=Task)
def create_task(task: Task, session: Annotated[Session, Depends(get_session)]):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Get all tasks
@app.get("/todos/", response_model=list[Task])
def read_tasks(session: Annotated[Session, Depends(get_session)]):
    tasks = session.exec(select(Task)).all()
    return tasks

# Get task by id
@app.get("/todos/{task_id}", response_model=Task)
def get_task_by_id(task_id: int, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update task
@app.put("/todos/{task_id}", response_model=Task)
def update_task(task_id: int, content: str, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.content = content
    session.add(task)
    session.commit()
    return task

# Delete task
@app.delete("/todos/{task_id}", response_model=Task)
def delete_task(task_id: int, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}