import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.crud.inventory_crud import validate_product_id
from app.deps import get_session
from app import order_pb2
from google.protobuf.json_format import MessageToDict


async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="validate-order-in-inventory",
        auto_offset_reset='earliest',
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW ORDER MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # Assuming the email is at the end and separated by known length
            combined_message = message.value
            email_separator = b'||'
            serialized_order, user_email_bytes = combined_message.rsplit(email_separator, 1)

            print(f"Serialized Order: {serialized_order}")
            print(f"User Email: {user_email_bytes.decode('utf-8')}")

            # # Deserialize the order
            try:
                order_data = order_pb2.Order()
                order_data.ParseFromString(serialized_order)
                product_id = order_data.product_id
                print(f"Product ID: {product_id}")
                print(f"Deserialized Order: {order_data}")
            except Exception as e:
                print(f"Failed to deserialize the order: {e}")
                continue

            # # Validate the product ID using the user_id
            with next(get_session()) as session:
                product = validate_product_id(Product_id=product_id, session=session)
                print(f"Validated product check: {product}")

                if product is None:
                    raise Exception(f"Product with id {product_id} not found in the database")
                
                if product is not None:
                    print(f"Product with id {product_id} is found in the database")
                    delimiter = b'||'
                    # user_email = user_email_bytes.encode("utf-8")
                    send_data = serialized_order + delimiter + user_email_bytes
                    print(f"Serialized Order with Email: {send_data}")


                    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait("order-add-stock-response", send_data)
                        print("Order confirm")
                    finally:
                        await producer.stop()

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
