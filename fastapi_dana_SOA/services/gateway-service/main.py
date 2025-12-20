import os
import json
from fastapi import FastAPI, HTTPException, Depends, Header
from jose import jwt, JWTError
from pydantic import BaseModel
from zeep import Client
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv
import logging

logging.getLogger('zeep').setLevel(logging.WARNING)

load_dotenv()

app = FastAPI(title="Gateway Service")
API_V1_STR = "/api/v1"

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# SOAP URLs
SOAP_ACCOUNT_URL = "http://localhost:8001?wsdl"
SOAP_TOPUP_URL = "http://localhost:8002?wsdl"
SOAP_TRANSACTION_URL = "http://localhost:8003?wsdl"

# Kafka Config
KAFKA_NETWORK = os.getenv("KAFKA_NETWORK", "localhost:19092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "event-stream-trpl")


class TopupRequest(BaseModel):
    amount: float


class TransferRequest(BaseModel):
    receiver_account_number: str
    amount: float


def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer."""
    app.state.producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_NETWORK,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await app.state.producer.start()
    print(f"✅ Kafka producer started: {KAFKA_NETWORK}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop Kafka producer."""
    await app.state.producer.stop()


@app.get(f"{API_V1_STR}/account/info")
async def get_account_info(payload: dict = Depends(verify_token)):
    """Get account info from SOAP."""
    account_number = payload.get("account_number")
    
    try:
        client = Client(SOAP_ACCOUNT_URL)
        result = client.service.get_account_info(account_number=account_number)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SOAP error: {str(e)}")


@app.post(f"{API_V1_STR}/topup")
async def topup(data: TopupRequest, payload: dict = Depends(verify_token)):
    """Topup via SOAP and publish to Kafka."""
    account_number = payload.get("account_number")
    username = payload.get("sub")
    
    try:
        # Call SOAP
        client = Client(SOAP_TOPUP_URL)
        result = client.service.topup(
            account_number=account_number,
            amount=str(data.amount)
        )
        
        # Check if success
        if "success" not in result.lower():
            raise HTTPException(status_code=400, detail=result)
        
        # Publish to Kafka
        event = {
            "type": "TOPUP",
            "sender": None,
            "receiver": account_number,
            "amount": data.amount,
            "username": username
        }
        await app.state.producer.send_and_wait(TOPIC_NAME, event)
        
        return {"message": result, "event_published": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post(f"{API_V1_STR}/transfer")
async def transfer(data: TransferRequest, payload: dict = Depends(verify_token)):
    """Transfer via SOAP and publish to Kafka."""
    sender_account = payload.get("account_number")
    username = payload.get("sub")
    
    try:
        # Call SOAP
        client = Client(SOAP_TRANSACTION_URL)
        result = client.service.transfer(
            sender_account_number=sender_account,
            receiver_account_number=data.receiver_account_number,
            amount=str(data.amount)
        )
        
        # Check if success
        if "success" not in result.lower():
            raise HTTPException(status_code=400, detail=result)
        
        # Publish to Kafka
        event = {
            "type": "TRANSFER",
            "sender": sender_account,
            "receiver": data.receiver_account_number,
            "amount": data.amount,
            "username": username
        }
        await app.state.producer.send_and_wait(TOPIC_NAME, event)
        
        return {"message": result, "event_published": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
