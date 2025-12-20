from zeep import Client
import requests
import logging

# Set logging level
logging.getLogger('zeep').setLevel(logging.WARNING)

def get_soap_client(wsdl_url):
    try:
        # Check if service is running
        response = requests.get(wsdl_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Service tidak dapat diakses: {wsdl_url}")
            return None
            
        client = Client(wsdl_url)
        print(f"✅ Berhasil terhubung ke service: {wsdl_url}")
        return client
    except Exception as e:
        print(f"❌ Error connecting to {wsdl_url}: {e}")
        return None

def call_soap_method(client, method_name, **kwargs):
    try:
        # Get the service
        service = client.service
        method = getattr(service, method_name)
        
        # Call the method
        result = method(**kwargs)
        
        if result and "error:" in str(result):
            return "error", result
        else:
            return "success", result
            
    except Exception as e:
        return "error", f"SOAP call failed: {e}"