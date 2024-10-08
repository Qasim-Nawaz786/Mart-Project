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
from app.crud.inventory_crud import delete_inventory_item_by_id, get_all_inventory_items, get_inventory_by_id
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.add_stock_consumer import consume_messages
from app import inventory_pb2
from pydantic import BaseModel
from app.consumer.order_consumer import consume_order_messages

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)





@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    asyncio.create_task(consume_messages("inventory-add-stock-response", settings.BOOTSTRAP_SERVER))
    asyncio.create_task(consume_order_messages("Order", settings.BOOTSTRAP_SERVER))
    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )




@app.get("/")
def read_root():
    return {"Hello": "This is Inventory service"}



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
async def add_new_inventory(
    inventory_item: InventoryItem, 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """Create new inventory and send it to kafka for verifying"""
    try:
        inventory_protobuf = inventory_pb2.InventoryItem(
            id=inventory_item.id,
            product_id=inventory_item.product_id,
            variant_id=inventory_item.variant_id,
            quantity=inventory_item.quantity,
            status=inventory_item.status,
            price=inventory_item.price
        )
        print("Inventory_item before serialized",inventory_item)
        serialized_inventory = inventory_protobuf.SerializeToString()
        print(f"Serialized Inventory: {serialized_inventory}")
        
        # Produce the serialized message to Kafka
        await producer.send_and_wait("Inventory-Item", serialized_inventory)
        
        # Return the inventory item itself as required by FastAPI
        return inventory_item
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
 



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




