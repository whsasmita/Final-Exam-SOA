import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.soap import get_soap_client, call_soap_method

WSDL_URL = "http://localhost:8002?wsdl"

def handle_topup(token, account_number, amount):
    """Topup dengan token validation."""
    client = get_soap_client(WSDL_URL)
    if not client:
        print("❌ Koneksi gagal ke Topup Service.")
        return None

    status, result = call_soap_method(client, "topup", token=token, account_number=account_number, amount=str(amount))
    
    if status == "success" and str(result).lower().startswith("success"):
        print(f"✅ {result}")
        return result
    else:
        print(f"❌ Topup gagal: {result}")
        return None