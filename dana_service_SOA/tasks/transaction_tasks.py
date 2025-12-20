import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import execute_query

def check_and_log_transactions():
    """
    Memeriksa semua transaksi dan mencatatnya ke konsol.
    Ini adalah contoh tugas untuk memverifikasi riwayat transaksi.
    """
    print("Memulai verifikasi transaksi...")

    query = "SELECT * FROM transactions ORDER BY created_at DESC;"
    transactions = execute_query(query)
    
    if not transactions:
        print("Tidak ada transaksi yang ditemukan.")
        return
        
    print(f"Total {len(transactions)} transaksi ditemukan.")

    for trans in transactions:
        print("---")
        print(f"ID Transaksi: {trans['id']}")
        print(f"Tipe: {trans['transaction_type'].upper()}")
        print(f"Dari: {trans['sender_account_number'] or 'N/A'}")
        print(f"Ke: {trans['receiver_account_number']}")
        print(f"Jumlah: {trans['amount']}")
        print(f"Status: {trans['status']}")
        print(f"Waktu: {trans['created_at']}")
        
    print("---")
    print("Verifikasi selesai.")

if __name__ == '__main__':
    check_and_log_transactions()