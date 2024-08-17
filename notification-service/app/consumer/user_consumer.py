import json
from sqlmodel import select
from aiokafka import  AIOKafkaConsumer
from app.crud.notification_crud import add_login_user_data
from app.models.user_model import UserLogin
from app.deps import get_session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from app.settings import APP_PASSWORD
from app import settings




async def consume_user(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-login-notification-consumer",
        request_timeout_ms=120000,
        session_timeout_ms=60000,
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message on topic {message.topic}")

            User_data = json.loads(message.value.decode())
            # data = User_data.get('User_id', 'message')
            print("TYPE", (type(User_data)))
            print(f"User Data {User_data}")
            

            with next(get_session()) as session:
                try:

                    print("SAVING DATA TO DATABSE")
                    # inventory_item_data: InventoryItem
                    db_insert_product = add_login_user_data(
                        user_data=UserLogin(**User_data), 
                        session=session)
                    
                    
                    print("DB_INSERT_USER", db_insert_product)
                except Exception as e:
                    print(f"Error while saving data: {str(e)}")
                
                try:

                    # user = session.exec(select(UserLogin).where(UserLogin.User_id == User_data["id"])).first()
                    user_id = db_insert_product.User_id
                    user_message = db_insert_product.message
                    user_email = User_data['email']
                    if user_id:
                        # user_message = user.message
                        # user_email = user.email
                        print(f"User found: Email = {user_email}, Message = {user_message}")

                        def send_email(subject:str):
                            smtp_server = "smtp.gmail.com"
                            smtp_port = 587
                            smtp_user = "qnawaz857@gmail.com"
                            smtp_password = settings.APP_PASSWORD  ## This is the 16 digit code that can access the gmail app password

                            msg = MIMEMultipart()
                            msg["From"] = smtp_user
                            msg["To"] = user_email
                            msg["Subject"] = subject

                            msg.attach(MIMEText(user_message, 'plain'))
                            print("Sending email to", user_email)
                            try:

                                with smtplib.SMTP(smtp_server, smtp_port) as server:
                                    server.starttls()
                                    server.login(smtp_user, smtp_password)
                                    server.send_message(msg)
                                print("Email sent successfully")
                            except Exception as e:
                                print(f"Failed to send email: {str(e)}")
                        send_email(subject='User verified Notifications')
                        print("EMAIL SENT")
                    else:
                        print("User not found, email not sent.")
                except: 
                    print("Message","User not found")

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()





