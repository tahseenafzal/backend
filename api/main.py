from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from api import settings
from sqlmodel import  Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends
from models import *

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql","postgresql+psycopg" 
)

engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)