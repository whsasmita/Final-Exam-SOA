import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'dana_service_db')

# Service ports
ACCOUNT_SERVICE_PORT = 8001
TOPUP_SERVICE_PORT = 8002
TRANSACTION_SERVICE_PORT = 8003