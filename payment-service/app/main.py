from contextlib import asynccontextmanager
import json
from typing import Annotated, AsyncGenerator
from sqlmodel import Session, SQLModel, select
from fastapi import FastAPI, Depends, HTTPException
from app.db_engine import engine
from app.deps import get_session
from app.models.payment_model import PaymentToken, Transaction
from app.crud.payment_crud import create_payment_intent, retrieve_payment_intent
from aiokafka import AIOKafkaProducer
from app.deps import get_kafka_producer

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Stripe Payment API", version="0.0.1")


@app.get("/")
def read_root():
    return {"message": "This is the Stripe Payment service"}


@app.post("/stripe/payment-intent")
async def create_transaction(
    basket_id: str,
    amount: float,
    currency: str,
    customer_email: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    # Create a payment intent (assuming `create_payment_intent` is an async function)
    payment_intent = await create_payment_intent(int(amount * 100), currency, customer_email)  # Amount in cents

    try:
        if payment_intent.get("error"):
            raise HTTPException(status_code=400, detail=payment_intent["error"])

        # Create a transaction object
        transaction = Transaction(
            stripe_transaction_id=payment_intent["id"],
            basket_id=basket_id,
            amount=amount,
            customer_email=customer_email,
            customer_mobile="N/A",  # Adjust this as needed
            status=payment_intent["status"]
        )

        # Convert the transaction object to a dict and then serialize it to JSON
        data_json = transaction.json().encode('utf8')

        # Send the transaction data to the Kafka topic
        await producer.send_and_wait("Transaction_", data_json)

        # Return the JSON data as a response
        return json.loads(data_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stripe/payment-intent/{payment_intent_id}")
async def retrieve_transaction(payment_intent_id: str, session: Session = Depends(get_session)):
    payment_intent = await retrieve_payment_intent(payment_intent_id)

    if payment_intent.get("error"):
        raise HTTPException(status_code=400, detail=payment_intent["error"])

    transaction = session.exec(select(Transaction).where(Transaction.stripe_transaction_id == payment_intent_id)).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {"payment_intent": payment_intent, "transaction": transaction}
