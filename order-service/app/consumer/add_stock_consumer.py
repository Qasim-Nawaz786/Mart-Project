import json
from aiokafka import  AIOKafkaConsumer
from app.crud.order_crud import add_new_order
from app.models.order_model import Order
from app.deps import get_session

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="add-stock-order-consumer-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            Order_data = json.loads(message.value.decode())
            print("TYPE", (type(Order_data)))
            print(f"Order Data {Order_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                # inventory_item_data: InventoryItem
                db_insert_product = add_new_order(
                    order_data=Order(**Order_data), 
                    session=session)
                
                print("DB_INSERT_STOCK", db_insert_product)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()