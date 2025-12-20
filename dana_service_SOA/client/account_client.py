import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.soap import get_soap_client, call_soap_method

WSDL_URL = "http://localhost:8001?wsdl"

def handle_login(username, password):
    """Login dan return token."""
    client = get_soap_client(WSDL_URL)
    if not client:
        print("❌ Koneksi gagal ke Account Service.")
        return None
        
    status, result = call_soap_method(client, "login_user", username=username, password=password)
    if status == "success" and str(result).lower().startswith("success"):
        print(f"✅ {result}")
        return result
    else:
        print(f"❌ Login gagal: {result}")
        return None

def handle_register(username, password):
    """Register dan return token."""
    client = get_soap_client(WSDL_URL)
    if not client:
        print("❌ Koneksi gagal ke Account Service.")
        return None
    
    status, result = call_soap_method(client, "register_user", username=username, password=password)
    if status == "success" and str(result).lower().startswith("success"):
        print(f"✅ {result}")
        return result
    else:
        print(f"❌ Registrasi gagal: {result}")
        return None

def handle_get_account_info(token, account_number):
    """Get account info dengan token."""
    client = get_soap_client(WSDL_URL)
    if not client:
        print("❌ Koneksi gagal ke Account Service.")
        return None
    
    status, result = call_soap_method(client, "get_account_info", token=token, account_number=account_number)
    if status == "success" and str(result).lower().startswith("success"):
        print(f"✅ {result}")
        return result
    else:
        print(f"❌ Gagal mengambil info rekening: {result}")
        return None

def validate_token(token):
    """Validasi token."""
    client = get_soap_client(WSDL_URL)
    if not client:
        return False, "Koneksi gagal"
    
    status, result = call_soap_method(client, "validate_token", token=token)
    if status == "success" and str(result).lower().startswith("success"):
        return True, result
    else:
        return False, result