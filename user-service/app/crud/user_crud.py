from datetime import datetime, timedelta
from app.models.user_model import User
from sqlmodel import Session, select
from fastapi import HTTPException
from jose import jwt, JWTError
from app import settings
from passlib.context import CryptContext
from aiokafka import AIOKafkaProducer
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def add_new_credentials(user_data:User, session: Session):
    print("adding new credentials")
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


def get_all_users(session: Session):
    all_users = session.exec(select(User)).all()
    return all_users


def validate_user(username: str, password:str, session: Session)-> User:
    user = session.exec(select(User).where(User.username == username)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user


def create_access_token(subject: str , expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY , algorithm=settings.ALGORITHM)
    return encoded_jwt

def delete_user(user_id:int, session:Session):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def produce_user_login_message(user):
    producer = AIOKafkaProducer(bootstrap_servers='localhost:19092')
    await producer.start()
    try:
        message = json.dumps({"username": user.username, "email": user.email})
        await producer.send_and_wait("user-login-topic", message.encode('utf-8'))
    finally:
        await producer.stop()


