import jwt
import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dana-service-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def generate_jwt_token(username, account_number):
    """Generate JWT token dengan expiration."""
    payload = {
        'username': username,
        'account_number': account_number,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_jwt_token(token):
    """Validate JWT token dan return payload jika valid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token telah expired"
    except jwt.InvalidTokenError:
        return False, "Token tidak valid"
    except Exception as e:
        return False, f"Error validating token: {e}"

def get_token_info(token):
    """Get token info tanpa validasi expiry (untuk debug)."""
    try:
        # Decode tanpa verify untuk melihat payload
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        return None

if __name__ == "__main__":
    # Test JWT functions
    print("Testing JWT Helper...")
    
    # Generate token
    token = generate_jwt_token("testuser", "1234567890")
    print(f"Generated Token: {token}")
    
    # Validate token
    valid, result = validate_jwt_token(token)
    print(f"Token Valid: {valid}")
    print(f"Payload: {result}")
    
    # Get token info
    info = get_token_info(token)
    print(f"Token Info: {info}")