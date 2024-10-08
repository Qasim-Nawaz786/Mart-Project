import json
from aiokafka import  AIOKafkaConsumer
from app.crud.order_crud import add_new_order
from app.models.order_model import Order
from app.deps import get_session
from app import order_pb2
from google.protobuf.json_format import MessageToDict
from datetime import datetime
from aiokafka import AIOKafkaProducer
async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="add-stock-order-consumer-group",
        request_timeout_ms=6000,
        # session_timeout_ms=60000,
        auto_offset_reset='earliest',
        # consumer_timeout_ms=30000,
        
    )

    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            combined_message = message.value
            email_separator = b'||'
            serialized_order, user_email_bytes = combined_message.rsplit(email_separator, 1)

            print(f"Serialized Order: {serialized_order}")
            print(f"User Email: {user_email_bytes.decode('utf-8')}")


            order_data = order_pb2.Order()
            order_data.ParseFromString(serialized_order)
            print(f"Received Order: {order_data}")

            order_dict = MessageToDict(order_data)
            print("ORDER Dict:", order_dict)

            id = order_dict.get('id')
            user_id = order_dict.get('userId')
            product_id = order_dict.get('productId')
            variant_id = order_dict.get('variantId')
            quantity = order_dict.get('quantity')
            total_price = order_dict.get('totalPrice')

            # Convert status from string to OrderStatus enum
            
            
            # Convert created_at from string to datetime object
            created_at_str = order_dict.get('createdAt')
            Created_at = datetime.fromisoformat(created_at_str) if created_at_str else None

            print("Created At:", Created_at)


            with next(get_session()) as session:
                order_item_data = Order(
                    id=id,
                    user_id=user_id,
                    product_id=product_id,
                    variant_id=variant_id,
                    quantity=quantity,
                    total_price=total_price,
                    created_at=Created_at,
                )
                print("SAVING DATA TO DATABASE")
                db_insert_product = add_new_order(order_data=order_item_data, session=session)
                
                print("DB_INSERT_STOCK", db_insert_product)

                # if db_insert_product is not None:
                #     print("Trying to send notification order successful")
                #     producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
                #     message = {"message":"Successfully sent notification order"}
                #     message_str = json.dumps(message)
                #     await producer.start()
                #     try:
                #         await producer.send_and_wait("order-confirm-notification", message_str)
                #     finally:
                #         await producer.stop()

                
                    
    finally:
        await consumer.stop()