import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.crud.product_crud import add_new_product, validate_product_id
from app.models.product_model import Product
from app.deps import get_session

async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order-add-group",
        # auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW ORDER MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            order_data = json.loads(message.value.decode())
            product_id = order_data["product_id"]
            print("PRODUCT ID", product_id)

            with next(get_session()) as session:
                product = validate_product_id(product_id= product_id, session=session)
                print(f"Validated product check: {product}")

                if product is None:
                    raise Exception(f"Product with id {product_id} not found in the database")
                
                if product is not None:
                    print(f"Product with id is found in the database")

                    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait("order-add-stock-response", message.value)
                    finally:
                        await producer.stop()

                
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()