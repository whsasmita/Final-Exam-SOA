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
        """Register new user per spawn to get fresh JWT token and account."""
        # Always register fresh user with unique username
        username = f"loadtest{random.randint(10000, 99999)}"
        response = self.client.post(
            "http://localhost:8004/api/v1/register",
            json={
                "username": username,
                "password": "loadtest123"
            },
            name="Auth: Register",
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.account_number = data.get("account_number")
            # Do initial topup so transfer has balance
            self.client.post(
                "/api/v1/topup",
                json={"amount": 500000},  # Initial balance
                headers={"Authorization": f"Bearer {self.token}"},
                name="Auth: Initial Topup",
                verify=False
            )
        else:
            self.token = None
            self.account_number = None
    
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

