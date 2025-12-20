from zeep import Client
from .topup import topup_dana

class TopupService:
    def topup(self, account_number, amount):
        """Endpoint untuk topup dana."""
        return topup_dana(account_number, amount)