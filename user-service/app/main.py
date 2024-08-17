# main.py
from contextlib import asynccontextmanager
from typing import  Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.db_engine import engine
from app.crud.user_crud import add_new_credentials, get_all_users, validate_user, create_access_token, hash_password, delete_user
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from app.models.user_model import User


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    # # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    # task = asyncio.create_task(consume_messages("inventory-add-stock-response", 'broker:19092'))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
async def login_request(data_form_user: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session), producer: AIOKafkaProducer= Depends(get_kafka_producer)):
     user = validate_user(data_form_user.username, data_form_user.password, session)
     get_access_token = timedelta(minutes=15)
     access_token = create_access_token(
        subject=user.username, expires_delta=get_access_token)
     message = {"message": "Login successful", "User_id": user.id, "email": user.email}
     message_str = json.dumps(message)
     
     await producer.send_and_wait("User-Verfication", message_str.encode("utf-8"))
     return {"UserName:":user.username, "access_token:":access_token}




@app.post("/register/")
def register_user(name:str,password: str,useremail: str, session:Session = Depends(get_session)):
    try:
        hashed_password = hash_password(password)
        user_data = User(username=name, password=hashed_password,email=useremail, created_at=datetime.now())
        data = add_new_credentials(user_data, session)
        print("Registering form user")
        return data
    except HTTPException as e:
        raise e
    

@app.get("/users", response_model=list[User])
def get_all_user(session: Annotated[Session, Depends(get_session)], token : Annotated[str , Depends(oauth2_scheme)]):
    """ Get all users from the database"""
    return get_all_users(session)


@app.delete("/delete-user/{user_id}")
def delete_users(user_idd:int, session: Annotated[Session, Depends(get_session)]):
    """ Delete user by id from the database"""
    try:
        delete_user(user_id=user_idd, session=session)
        return {"message": f"User deleted by id: {user_idd}"}
    except HTTPException as e:
        raise e
    


