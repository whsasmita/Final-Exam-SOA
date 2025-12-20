from locust import HttpUser, task, between
import random


class DanaServiceHTTP2User(HttpUser):
    """
    Load test for Dana Service HTTP/2 Gateway
    Target: https://localhost:8006 (TLS + HTTP/2)
    
    Note: Requires Hypercorn running with TLS cert
    """
    host = "https://localhost:8006"
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    # Disable SSL verification for self-signed cert
    insecure = True
    
    def on_start(self):
        """Login once per user to get JWT token."""
        # Register/Login to get token (Auth service on HTTP/1.1)
        response = self.client.post(
            "http://localhost:8004/api/v1/login",
            json={
                "username": "loadtest",
                "password": "loadtest123"
            },
            name="Auth: Login",
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.account_number = data.get("account_number")
        else:
            # Try register if login fails
            response = self.client.post(
                "http://localhost:8004/api/v1/register",
                json={
                    "username": f"loadtest{random.randint(1000, 9999)}",
                    "password": "loadtest123"
                },
                name="Auth: Register",
                verify=False
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.account_number = data.get("account_number")
            else:
                self.token = None
    
    @task(3)
    def get_account_info(self):
        """Get account info (most frequent operation)."""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/account/info",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Gateway: Get Account Info",
            verify=False
        )
    
    @task(1)
    def topup(self):
        """Topup dana."""
        if not self.token:
            return
        
        self.client.post(
            "/api/v1/topup",
            json={"amount": random.randint(10000, 100000)},
            headers={"Authorization": f"Bearer {self.token}"},
            name="Gateway: Topup",
            verify=False
        )
    
    @task(1)
    def transfer(self):
        """Transfer dana (self-transfer for testing)."""
        if not self.token or not self.account_number:
            return
        
        # Use own account number for self-transfer (guaranteed to exist)
        # In production, you'd query real receiver accounts from DB
        
        self.client.post(
            "/api/v1/transfer",
            json={
                "receiver_account_number": self.account_number,
                "amount": random.randint(5000, 50000)
            },
            headers={"Authorization": f"Bearer {self.token}"},
            name="Gateway: Transfer",
            verify=False
        )

