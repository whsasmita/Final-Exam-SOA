from utils.db import execute_query

def topup_dana(account_number, amount):
    """
    Memproses topup dana ke rekening yang ditentukan.
    """
    try:
        amount = float(amount)
    except ValueError:
        return "error: Jumlah topup harus berupa angka."
    
    if amount <= 0:
        return "error: Jumlah topup harus lebih dari 0."

    # Pastikan rekening ada
    account = execute_query("SELECT * FROM accounts WHERE account_number = %s", (account_number,))
    
    if not account:
        return "error: Nomor rekening tidak ditemukan."

    try:
        # Tambah saldo
        update_query = "UPDATE accounts SET balance = balance + %s WHERE account_number = %s"
        execute_query(update_query, (amount, account_number), fetch=False)

        # Catat transaksi
        insert_transaction_query = """
            INSERT INTO transactions (sender_account_number, receiver_account_number, amount, transaction_type)
            VALUES (NULL, %s, %s, 'topup')
        """
        execute_query(insert_transaction_query, (account_number, amount), fetch=False)
        
        return "success: Topup berhasil."
    
    except Exception as e:
        return f"error: Topup gagal. Terjadi kesalahan server: {e}"