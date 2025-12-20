from zeep import Client
from .account import register, login

class AccountService:
    def login_user(self, username, password):
        """Endpoint untuk login."""
        return login(username, password)
    
    def register_user(self, username, password):
        """Endpoint untuk registrasi."""
        return register(username, password)