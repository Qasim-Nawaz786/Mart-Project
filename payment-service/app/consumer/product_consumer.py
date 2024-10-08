# import json
# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
# from app.crud.product_crud import add_new_product
# from app.models.product_model import Product
# from app.deps import get_session
# from app import product_pb2
# from google.protobuf.json_format import MessageToDict

# async def consume_messages(topic, bootstrap_servers):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="my-group",
#         request_timeout_ms=60000,
#         # auto_offset_reset='earliest'
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         # Continuously listen for messages.
#         async for message in consumer:
#             print(f"Recieved message in topic: {message.topic}")
#             # product_data = json.loads(message.value.decode())
#             # print(f"Product data: {product_data}")
#             products = product_pb2.Product()
#             products.ParseFromString(message.value)
#             print(f"Products: {products}")
#             product_dict = MessageToDict(products)   ## This line should be replaced with a dictionary that contains information about the products
#             print("PRODUCT_DICT", product_dict)

#             with next(get_session()) as session:
#                 print("Saving data to database...")
#                 db_insert_product = add_new_product(
#                     product_data = Product(**product_dict), session = session)
#                 print("DB_INSERT_PRODUCT", db_insert_product)
#             # Here you can add code to process each message.
#             # Example: parse the message, store it in a database, etc.
#     finally:
#         # Ensure to close the consumer when done.
#         await consumer.stop()