# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json
from app.db_engine import engine
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session, get_kafka_producer
from fastapi import HTTPException
from app.consumer.product_consumer import consume_messages
from app.consumer.inventory_consumer import consume_inventory_messages
from app import product_pb2
from app import settings



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)



@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating...!")
    # print("Creating tables..")
    # # loop.run_until_complete(consume_messages('todos', 'broker:19092'))  
    asyncio.create_task(consume_messages("product", settings.BOOTSTRAP_SERVER))
    asyncio.create_task(consume_inventory_messages("Inventory-Item", settings.BOOTSTRAP_SERVER))
    

    print("Strartup complete")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    )




@app.get("/")
def read_root():
    return {"Hello": "This is Product service"}


@app.get("/manage-products-all")
def call_all_products(session:Annotated[Session, Depends(get_session)]):
    """Get all products from the database"""
    return get_all_products(session)

@app.get("/manage-products/{product_id}")
def call_product_by_id(product_id:int, session:Annotated[Session, Depends(get_session)]):
    """Get product by id from the database"""
    try:
        return get_product_by_id(product_id = product_id, session= session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/manage-products/", response_model=Product)
async def create_new_product(product : Product, session:Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """"Create new product and send it to kafka"""
    # product_dict = {field: getattr(product, field) for field in product.dict()}   #|
    # product_json = json.dumps(product_dict).encode("utf-8")                       #|
    # print("product_JSON:", product_json)        
    product_protobuf = product_pb2.Product(
        id=product.id, 
        name=product.name, 
        description = product.description, 
        price = product.price, 
        expirey = product.expirey, 
        brand = product.brand, 
        weight = product.weignt, 
        category = product.category, 
        sku = product.sku)                                  #|   ## These lines send data to the kafka producer
    serialized_product = product_protobuf.SerializeToString()
    print(f"serialized_product: {serialized_product}")
    # Produce message                                                             #|
    await producer.send_and_wait("product", serialized_product)      #|
    # new_product = add_new_product(product, session)                           ###  This line push the data directly into the database
    return product

@app.patch("/manage-products/{product_id}", response_model=Product)
def update_single_product(product_id:int, product: ProductUpdate, session:Annotated[Session, Depends(get_session)]):
    """Update a single product by id"""
    try:
        return update_product_by_id(product_id=product_id, to_update_product_data=product, session = session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException (status_code=500, detail=str(e))
        
@app.delete("/manage-product/{product_id}", response_model=dict)
def delete_single_product(product_ids: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single product by id"""
    try:
        return delete_product_by_id(product_id=product_ids, session=session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




