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
from app.models.order_model import Order, OrderItem
from app.crud.order_crud import cancle_order_by_id, get_all_orders, get_item, get_order_by_id
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.add_stock_consumer import consume_messages
from app.consumer.item_consumer import consume_item_messages

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)





@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    task = asyncio.create_task(consume_messages("order-add-stock-response", 'broker:19092'))
    task1 = asyncio.create_task(consume_item_messages("Order-Item", 'broker:19092'))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )




@app.get("/")
def read_root():
    return {"Hello": "PanaCloud"}



@app.get("/manage-order/all", response_model=list[Order])
def all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_all_orders(session)


@app.get("/manage-item/all", response_model=list[OrderItem])
def all_items(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_item(session)

@app.get("/manage-order/{order_id}")
def inventory_by_id(order_id:int, session:Annotated[Session, Depends(get_session)]):
    """Get product by id from the database"""
    try:
        return get_order_by_id(order_id=order_id, session= session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/manage-order/", response_model=Order)
async def add_new_order(Order_item : Order, session:Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """"Create new inventory and send it to kafka for verifying"""
    item_dict = {field: getattr(Order_item, field) for field in Order_item.dict()}   #|
    item_json = json.dumps(item_dict).encode("utf-8")                                        #|
    print("product_JSON:", item_dict)                                                        #|   ## These lines send data to the kafka producer
    # Produce message                                                                        #|
    await producer.send_and_wait("Order", item_json)                                #|
    # new_inventory = add_new_inventory(Inventory_item, session)                           ###  This line push the data directly into the database
    return Order_item  


@app.post("/manage-item/", response_model=OrderItem)
async def add_new_item(item : OrderItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """"Create new item and send it to kafka for verifying"""
    item_dict = {field: getattr(item, field) for field in item.dict()}   #|
    item_json = json.dumps(item_dict).encode('utf-8')
    print("item_JSON:", item_dict)                                        
    # Produce message
    await producer.send_and_wait("Order-Item", item_json)
    # new_inventory = add_new_inventory(Inventory_item, session)                           ###  This line push the data directly into the database
    return item
        
@app.delete("/manage-order/{order_id}")
def delete_order_by_id(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single product by id"""
    try:
        return cancle_order_by_id(order_item_id= order_id, session=session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




