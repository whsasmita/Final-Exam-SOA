import os
import hashlib
import pymysql
from fastapi import FastAPI, HTTPException, Depends, Header
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .schemas import LoginSchema, RegisterSchema, Token, UpdateAccountSchema, UpdateAccountResponse

load_dotenv()

app = FastAPI(title="Auth Service")
API_V1_STR = "/api/v1"

# Konfigurasi Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Konfigurasi DB yang sama dengan SOAP
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dana_service_db")

# Helper: Buat JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def _get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.post(f"{API_V1_STR}/register", response_model=Token)
async def register(data: RegisterSchema):
    """Register user dan generate account_number, return JWT."""
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            # Cek username sudah ada
            cur.execute("SELECT id FROM users WHERE username = %s", (data.username,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username sudah terdaftar")
            
            # Insert user
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (data.username, hashed)
            )
            
            # Get user ID yang baru
            cur.execute("SELECT id FROM users WHERE username = %s", (data.username,))
            user_row = cur.fetchone()
            user_id = user_row["id"]
            
            # Generate account number (10 digit random)
            import random, string
            account_number = ''.join(random.choices(string.digits, k=10))
            while True:
                cur.execute("SELECT id FROM accounts WHERE account_number = %s", (account_number,))
                if not cur.fetchone():
                    break
                account_number = ''.join(random.choices(string.digits, k=10))
            
            # Insert account
            cur.execute(
                "INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)",
                (user_id, account_number, 0.0)
            )
            conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registrasi gagal: {str(e)}")

    # Generate JWT
    access_token = create_access_token({
        "sub": data.username,
        "account_number": account_number
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "account_number": account_number
    }

@app.post(f"{API_V1_STR}/login", response_model=Token)
async def login(data: LoginSchema):
    # Validasi username/password terhadap DB SOAP (hash SHA-256)
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.username, a.account_number
                FROM users u
                JOIN accounts a ON a.user_id = u.id
                WHERE u.username = %s AND u.password = %s
                """,
                (data.username, hashed)
            )
            row = cur.fetchone()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Koneksi DB gagal")

    if not row:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    # Generate JWT yang memuat username & account_number
    access_token = create_access_token({
        "sub": row["username"],
        "account_number": row["account_number"]
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "account_number": row["account_number"]
    }

# JWT Verification Dependency
async def verify_token(authorization: str = Header(...)):
    """Extract and verify JWT token from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.put(f"{API_V1_STR}/account/update", response_model=UpdateAccountResponse)
async def update_account(data: UpdateAccountSchema, current_username: str = Depends(verify_token)):
    """Update username dan/atau password untuk user yang sedang login."""
    if not data.username and not data.password:
        raise HTTPException(status_code=400, detail="Minimal satu field harus diisi (username atau password)")
    
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            # Validasi user exists
            cur.execute("SELECT id FROM users WHERE username = %s", (current_username,))
            user_row = cur.fetchone()
            if not user_row:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            user_id = user_row["id"]
            new_username = data.username if data.username else current_username
            
            # Jika update username, cek apakah username baru sudah dipakai user lain
            if data.username and data.username != current_username:
                cur.execute("SELECT id FROM users WHERE username = %s", (data.username,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Username sudah dipakai user lain")
            
            # Build update query
            if data.username and data.password:
                hashed = hashlib.sha256(data.password.encode()).hexdigest()
                cur.execute(
                    "UPDATE users SET username = %s, password = %s WHERE id = %s",
                    (data.username, hashed, user_id)
                )
            elif data.username:
                cur.execute(
                    "UPDATE users SET username = %s WHERE id = %s",
                    (data.username, user_id)
                )
            elif data.password:
                hashed = hashlib.sha256(data.password.encode()).hexdigest()
                cur.execute(
                    "UPDATE users SET password = %s WHERE id = %s",
                    (hashed, user_id)
                )
            
            conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update gagal: {str(e)}")
    
    return {
        "message": "Akun berhasil diupdate",
        "username": new_username
    }