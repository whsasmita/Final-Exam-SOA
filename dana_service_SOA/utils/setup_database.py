import sys
import os

# Pastikan bisa import utils.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import execute_query

def create_tables():
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    accounts_table = """
    CREATE TABLE IF NOT EXISTS accounts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        account_number VARCHAR(20) NOT NULL UNIQUE,
        balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_accounts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_account_number VARCHAR(20),
        receiver_account_number VARCHAR(20),
        amount DECIMAL(15,2) NOT NULL,
        transaction_type ENUM('transfer','topup') NOT NULL,
        status ENUM('pending','success','failed') NOT NULL DEFAULT 'success',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_sender (sender_account_number),
        INDEX idx_receiver (receiver_account_number),
        CONSTRAINT fk_trans_sender FOREIGN KEY (sender_account_number) REFERENCES accounts(account_number) ON DELETE SET NULL,
        CONSTRAINT fk_trans_receiver FOREIGN KEY (receiver_account_number) REFERENCES accounts(account_number) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    # Buat tabel terlebih dahulu
    for sql in (users_table, accounts_table, transactions_table):
        execute_query(sql, fetch=False)

    # Cek dan tambahkan kolom/index jika belum ada
    # Untuk MySQL, kita perlu cek manual apakah kolom/index sudah ada
    
    # Cek kolom balance
    try:
        check_balance = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'accounts' 
        AND COLUMN_NAME = 'balance';
        """
        result = execute_query(check_balance, fetch=True)
        if not result:
            execute_query("ALTER TABLE accounts ADD COLUMN balance DECIMAL(15,2) NOT NULL DEFAULT 0.00;", fetch=False)
    except Exception as e:
        print(f"Info: {e}")

    # Cek unique index account_number
    try:
        check_acc_idx = """
        SELECT INDEX_NAME 
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'accounts' 
        AND INDEX_NAME = 'ux_accounts_account_number';
        """
        result = execute_query(check_acc_idx, fetch=True)
        if not result:
            execute_query("ALTER TABLE accounts ADD UNIQUE INDEX ux_accounts_account_number (account_number);", fetch=False)
    except Exception as e:
        print(f"Info: {e}")

    # Cek unique index username
    try:
        check_user_idx = """
        SELECT INDEX_NAME 
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'users' 
        AND INDEX_NAME = 'ux_users_username';
        """
        result = execute_query(check_user_idx, fetch=True)
        if not result:
            execute_query("ALTER TABLE users ADD UNIQUE INDEX ux_users_username (username);", fetch=False)
    except Exception as e:
        print(f"Info: {e}")

if __name__ == "__main__":
    print("Setting up database schema...")
    create_tables()
    print("Done.")