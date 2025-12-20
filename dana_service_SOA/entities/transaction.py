# project_dana/entities/transaction.py

class Transaction:
    def __init__(self, transaction_id, sender_acc_num, receiver_acc_num, amount, trans_type, status, created_at):
        self.id = transaction_id
        self.sender_account_number = sender_acc_num
        self.receiver_account_number = receiver_acc_num
        self.amount = float(amount)
        self.transaction_type = trans_type
        self.status = status
        self.created_at = created_at
        
    def __repr__(self):
        return f"<Transaction(type='{self.transaction_type}', amount={self.amount})>"