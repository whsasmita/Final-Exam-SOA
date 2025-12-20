import random, string
from fastapi import FastAPI, Depends
from .models import User
from .schemas import UserCreate, UserResponse
# ... (setup database session)

app = FastAPI()
API_V1_STR = "/api/v1"

def generate_acc_num():
    return ''.join(random.choices(string.digits, k=10))

@app.post(f"{API_V1_STR}/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    # Logic: Simpan User ke DB dan generate account_number
    acc_num = generate_acc_num()
    return {"email": user_in.email, "account_number": acc_num}