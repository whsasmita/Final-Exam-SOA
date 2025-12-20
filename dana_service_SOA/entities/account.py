# project_dana/entities/account.py

class Account:
    def __init__(self, account_id, user_id, account_number, balance):
        self.id = account_id
        self.user_id = user_id
        self.account_number = account_number
        self.balance = float(balance) 
        
    def __repr__(self):
        return f"<Account(number='{self.account_number}', balance={self.balance})>"