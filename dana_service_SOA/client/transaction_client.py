import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.soap import get_soap_client, call_soap_method

WSDL_URL = "http://localhost:8003?wsdl"

def handle_transfer(token, sender_account, receiver_account, amount):
    """Transfer dengan token validation."""
    client = get_soap_client(WSDL_URL)
    if not client:
        print("❌ Koneksi gagal ke Transaction Service.")
        return None
        
    status, result = call_soap_method(client, "transfer", 
                                    token=token,
                                    sender_account_number=sender_account, 
                                    receiver_account_number=receiver_account, 
                                    amount=amount)
    
    if status == "success" and str(result).lower().startswith("success"):
        print(f"✅ {result}")
        return result
    else:
        print(f"❌ Transfer gagal: {result}")
        return None