# main.py
from contextlib import asynccontextmanager
from typing import  Annotated
from app import settings
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
import asyncio
from app.db_engine import engine
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.user_consumer import consume_user
from app.models.user_model import UserLogin
from app.crud.notification_crud import delete_user_by_id, get_user

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)





@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    # task = asyncio.create_task(consume_messages("order-add-stock-response", 'broker:19092'))
    task1 = asyncio.create_task(consume_user("User-Verfication", 'broker:19092'))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )




@app.get("/")
def read_root():
    return {"Hello": "PanaCloud"}



@app.get("/manage-user/all", response_model=list[UserLogin])
def all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_user(session)

@app.delete("/delete-user/{user_id}")
def delete_user(user_idd:int, session: Annotated[Session,Depends(get_session)]):
    """ Delete user by id from the database"""
    try:
        delete_user_by_id(user_id=user_idd, session=session)
        return {"message": f"User deleted by id: {user_idd}"}
    except HTTPException as e:
        raise e

# 