import json
from sqlmodel import select
from aiokafka import AIOKafkaConsumer
from app.crud.notification_crud import add_login_user_data
from app.models.user_model import UserLogin
from app.deps import get_session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import settings

async def consume_user(topics, bootstrap_servers):
    # Create a consumer instance with multiple topics.
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id="user-login-notification-consumer",
        # request_timeout_ms=120000,
        session_timeout_ms=60000,
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message on topic {message.topic}")

            # Handle messages from the user-verification topic
            if message.topic == "user-verfication":
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
            
            # Handle messages from the order-confirm-notification topic
            elif message.topic == "order-add-stock-response":
                print(f"Received message on topic {message.topic}")
                print(f"Message Value {message.value}")

                combined_message = message.value
                email_separator = b'||'
                serialized_order, user_email_bytes = combined_message.rsplit(email_separator, 1)

                print(f"User Email: {user_email_bytes.decode('utf-8')}")

                user_email = user_email_bytes.decode('utf-8')
                order_message = "Order Confirm"
                
                if user_email:
                    def send_email(subject:str):
                        smtp_server = "smtp.gmail.com"
                        smtp_port = 587
                        smtp_user = "qnawaz857@gmail.com"
                        smtp_password = settings.APP_PASSWORD
                        
                        msg = MIMEMultipart()
                        msg["From"] = smtp_user
                        msg["To"] = user_email
                        msg["Subject"] = subject

                        msg.attach(MIMEText(order_message, 'plain'))
                        print("Sending email to", user_email)
                        try:
                            with smtplib.SMTP(smtp_server, smtp_port) as server:
                                server.starttls()
                                server.login(smtp_user, smtp_password)
                                server.send_message(msg)
                            print("Email sent successfully")
                        except Exception as e:
                            print(f"Failed to send email: {str(e)}")
                    send_email(subject='Order Confirmation Notification')
                    print("EMAIL SENT")
            


            elif message.topic == "Transaction_":
                print(f"Received message on topic {message.topic}")
                print(f"Message Value {message.value}")

                decoded_message = message.value.decode("utf-8")

                try:
                    transaction_data = json.loads(decoded_message)
                    print("Transaction data:", transaction_data)
                    user_email = transaction_data.get('customer_email')
                    if user_email:
                        print(f"User Email: {user_email}")
                    else:
                        print("customer_email not found in the transaction data.")
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON: {e}")

              
                payment_message = "Payment confirmation"
                
                if user_email:
                    def send_email(subject:str):
                        smtp_server = "smtp.gmail.com"
                        smtp_port = 587
                        smtp_user = "qnawaz857@gmail.com"
                        smtp_password = settings.APP_PASSWORD
                        
                        msg = MIMEMultipart()
                        msg["From"] = smtp_user
                        msg["To"] = user_email
                        msg["Subject"] = subject

                        msg.attach(MIMEText(payment_message, 'plain'))
                        print("Sending email to", user_email)
                        try:
                            with smtplib.SMTP(smtp_server, smtp_port) as server:
                                server.starttls()
                                server.login(smtp_user, smtp_password)
                                server.send_message(msg)
                            print("Email sent successfully")
                        except Exception as e:
                            print(f"Failed to send email: {str(e)}")
                    send_email(subject='Payment Confirmation Notification')
                    print("EMAIL SENT")

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()







