import json
from aiokafka import  AIOKafkaConsumer
from app.crud.inventory_crud import add_new_inventory
from app.models.inventory_model import InventoryItem
from app.deps import get_session
from app import inventory_pb2
from google.protobuf.json_format import MessageToDict

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="add-stock-consumer-group",
        request_timeout_ms=60000,

        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            # inventory_data = json.loads(message.value.decode())
            # print("TYPE", (type(inventory_data)))
            inventory = inventory_pb2.InventoryItem()
            inventory.ParseFromString(message.value)
            print(f"Received inventory: {inventory}")
            
            inventory_dict = MessageToDict(inventory)
            print("Inventory Dict:", inventory_dict)

            id = inventory_dict.get('id')
            product_id = inventory_dict.get('productId')
            variant_id = inventory_dict.get('variantId')
            quantity = inventory_dict.get('quantity')
            status = inventory_dict.get('status')
            price = inventory_dict.get('price')

            if product_id is None or variant_id is None:
                print(f"Missing required fields: product_id or variant_id. Skipping entry.")
                continue

                

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")

                inventory_data = InventoryItem(
                        id=id,
                        product_id=product_id,
                        variant_id=variant_id,
                        quantity=quantity,
                        status=status,
                        price=price
                    )
                # inventory_item_data: InventoryItem
                db_insert_product = add_new_inventory(
                    inventory_data=inventory_data, 
                    session=session)
                
                print("DB_INSERT_STOCK", db_insert_product)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()