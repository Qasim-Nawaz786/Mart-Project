# import json
# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
# from app.crud.product_crud import add_new_product, validate_product_id
# from app.models.product_model import Product
# from app.deps import get_session
# from app import inventory_pb2
# from google.protobuf.json_format import MessageToDict

# async def consume_inventory_messages(topic, bootstrap_servers):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="inventory-add-group",
#         request_timeout_ms=60000,
#         # session_timeout_ms=60000,
#         # auto_offset_reset='earliest'
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         async for message in consumer:
#             print(f"Received message on topic {message.topic}")

#             inventory = inventory_pb2.InventoryItem()
#             inventory.ParseFromString(message.value)
#             print(f"Received inventory: {inventory}")

#             inventory_dict = MessageToDict(inventory)
#             print("Inventory Dict:", inventory_dict)

#             # Access product_id safely
#             product_id = inventory_dict.get('productId')
#             print("Found PRODUCT ID", product_id)

#             # No need to raise an exception since product_id is found
#             if not product_id:
#                 raise Exception("product_id is missing in the inventory message")

#             with next(get_session()) as session:
#                 product = validate_product_id(Product_id=product_id, session=session)
#                 print(f"Validated product check: {product}")

#                 if product is None:
#                     raise Exception(f"Product with id {product_id} not found in the database")

#                 print(f"Product with id {product_id} is found in the database")

#                 producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
#                 await producer.start()
#                 try:
#                     await producer.send_and_wait("inventory-add-stock-response", message.value)
#                 finally:
#                     await producer.stop()

#     finally:
#         await consumer.stop()