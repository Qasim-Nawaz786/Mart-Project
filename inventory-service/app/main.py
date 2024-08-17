# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import add_new_inventory, delete_inventory_item_by_id, get_all_inventory_items, get_inventory_by_id
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.add_stock_consumer import consume_messages

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)





@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    # # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages("inventory-add-stock-response", 'broker:19092'))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )




@app.get("/")
def read_root():
    return {"Hello": "PanaCloud"}



@app.get("/manage-inventory/all", response_model=list[InventoryItem])
def all_inventory_items(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_all_inventory_items(session)

@app.get("/manage-inventory/{inventory_id}")
def inventory_by_id(inventory_id:int, session:Annotated[Session, Depends(get_session)]):
    """Get product by id from the database"""
    try:
        return get_inventory_by_id(inventory_id=inventory_id, session= session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/manage-inventory/", response_model=InventoryItem)
async def add_new_inventory(Inventory_item : InventoryItem, session:Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """"Create new inventory and send it to kafka for verifying"""
    item_dict = {field: getattr(Inventory_item, field) for field in Inventory_item.dict()}   #|
    item_json = json.dumps(item_dict).encode("utf-8")                                        #|
    print("product_JSON:", item_dict)                                                        #|   ## These lines send data to the kafka producer
    # Produce message                                                                        #|
    await producer.send_and_wait("Inventory-Item", item_json)                                #|
    # new_inventory = add_new_inventory(Inventory_item, session)                           ###  This line push the data directly into the database
    return Inventory_item  




# @app.patch("/manage-products/{product_id}", response_model=Product)
# def update_single_product(product_id:int, product: ProductUpdate, session:Annotated[Session, Depends(get_session)]):
#     """Update a single product by id"""
#     try:
#         return update_product_by_id(product_id=product_id, to_update_product_data=product, session = session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException (status_code=500, detail=str(e))



        
@app.delete("/manage-inventory/{inventory_id}")
def delete_inventory_by_id(inventory_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single product by id"""
    try:
        return delete_inventory_item_by_id(inventory_item_id= inventory_id, session=session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




