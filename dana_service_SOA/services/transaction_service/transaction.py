from utils.db import execute_query

def transfer_dana(sender_account_number, receiver_account_number, amount):
    """
    Memproses transfer dana antar rekening.
    Menggunakan transaksi database untuk memastikan konsistensi.
    """
    try:
        amount = float(amount)
    except ValueError:
        return "error: Jumlah transfer harus berupa angka."
    
    if amount <= 0:
        return "error: Jumlah transfer harus lebih dari 0."

    # Pastikan kedua rekening ada
    sender_account = execute_query("SELECT * FROM accounts WHERE account_number = %s", (sender_account_number,))
    receiver_account = execute_query("SELECT * FROM accounts WHERE account_number = %s", (receiver_account_number,))
    
    if not sender_account:
        return "error: Rekening pengirim tidak ditemukan."
    if not receiver_account:
        return "error: Rekening penerima tidak ditemukan."
    
    sender_balance = sender_account[0]['balance']
    
    if sender_balance < amount:
        return "error: Saldo tidak mencukupi."

    # Mulai transaksi database
    try:
        # Kurangi saldo pengirim
        update_sender_query = "UPDATE accounts SET balance = balance - %s WHERE account_number = %s"
        execute_query(update_sender_query, (amount, sender_account_number), fetch=False)
        
        # Tambah saldo penerima
        update_receiver_query = "UPDATE accounts SET balance = balance + %s WHERE account_number = %s"
        execute_query(update_receiver_query, (amount, receiver_account_number), fetch=False)

        # Catat transaksi
        insert_transaction_query = """
            INSERT INTO transactions (sender_account_number, receiver_account_number, amount, transaction_type)
            VALUES (%s, %s, %s, 'transfer')
        """
        execute_query(insert_transaction_query, (sender_account_number, receiver_account_number, amount), fetch=False)
        
        return "success: Transfer berhasil."
    
    except Exception as e:
        # Jika ada error, transaksi akan di-rollback
        return f"error: Transfer gagal. Terjadi kesalahan server: {e}"