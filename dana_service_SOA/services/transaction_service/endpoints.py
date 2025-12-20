from zeep import Client
from .transaction import transfer_dana

class TransactionService:
    def transfer(self, sender_account_number, receiver_account_number, amount):
        """Endpoint untuk transfer dana."""
        return transfer_dana(sender_account_number, receiver_account_number, amount)