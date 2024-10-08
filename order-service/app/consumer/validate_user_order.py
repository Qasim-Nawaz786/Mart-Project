from aiokafka import AIOKafkaConsumer
import json

# Initialize valid_user_ids as a dictionary
valid_user_ids = {}

async def consume_user_login(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-login-validation",
        request_timeout_ms=6000,
    )

    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            user = json.loads(message.value.decode('utf-8'))
            
            print(f"User_data: {user}")
            print(f"Decoded message from topic {message.topic}")
            user_id = user.get('User_id')
            user_email = user.get('email')
            print(f"Received user: {user_id}")
            print(f"User_email: {user_email}")

            if user_id and user_email:
                # Store user_id as key and user_email as value in the dictionary
                valid_user_ids[user_id] = user_email
                print(f"User ID {user_id} added with email {user_email}.")

            if not user_id:
                print(f"Missing required field: user_id. Skipping entry.")
                continue
    finally:
        await consumer.stop()
