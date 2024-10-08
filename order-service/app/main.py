# main.py
from contextlib import asynccontextmanager
from typing import  Annotated
from app import settings
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.models.order_model import Order
from app.crud.order_crud import cancle_order_by_id, get_all_orders, get_order_by_id
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.add_stock_consumer import consume_messages
from app import order_pb2
from app.consumer.validate_user_order import consume_user_login, valid_user_ids
def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)





@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    asyncio.create_task(consume_messages("order-add-stock-response", settings.BOOTSTRAP_SERVER))
    # asyncio.create_task(consume_item_messages("Order-Item", 'broker:19092'))
    asyncio.create_task(consume_user_login("user-verfication", settings.BOOTSTRAP_SERVER))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )





@app.get("/")
def read_root():
    return {"Hello": "This is Order service"}



@app.get("/manage-order/all", response_model=list[Order])
def all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_all_orders(session)


@app.get("/manage-order/{order_id}")
def inventory_by_id(order_id:int, session:Annotated[Session, Depends(get_session)]):
    """Get product by id from the database"""
    try:
        return get_order_by_id(order_id=order_id, session= session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/create-order/", response_model=Order)
async def add_new_order(Order_item: Order, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """Create a new order and send it to Kafka for verification."""

    user_id = Order_item.user_id
    print(f"Checking user ID: {user_id}")

    # Retrieve user_email using user_id from valid_user_ids
    user_email = valid_user_ids.get(user_id)
    encode_user_email = user_email.encode("utf-8")
    delimiter = b'||'
    
    try:
        if user_email:
            print(f"User ID {user_id} is valid, proceeding to create order with email {user_email}.")
            
            # Create an order protobuf object
            order_protobuf = order_pb2.Order(
                id=Order_item.id,
                user_id=Order_item.user_id,
                product_id=Order_item.product_id,
                variant_id=Order_item.variant_id,
                quantity=Order_item.quantity,
                total_price=Order_item.total_price,
                created_at=Order_item.created_at
            )
            print("Order_item before serialization:", order_protobuf)

            # Serialize the order
            serialized_order = order_protobuf.SerializeToString()
            order_with_email = serialized_order + delimiter + encode_user_email
            print(f"Serialized Order with Email: {order_with_email}")

            # Send the serialized order with email to Kafka
            await producer.send_and_wait("Order", order_with_email)
            return Order_item
        else:
            print(f"User ID {user_id} not found in valid_user_ids.")
            raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist.")
    except Exception as e:
        print(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the order for user id {user_id}.")





        
@app.delete("/manage-order/{order_id}")
def delete_order_by_id(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single product by id"""
    try:
        return cancle_order_by_id(order_item_id= order_id, session=session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




