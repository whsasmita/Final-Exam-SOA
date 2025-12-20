import sys
import os
import hashlib
import random

# Tambahkan root project ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.db import execute_query
from utils.helpers import generate_account_number, hash_password


def register(username, password):
    try:
        hashed_password = hash_password(password)

        existing_user = execute_query("SELECT id FROM users WHERE username = %s", (username,))
        if existing_user:
            return "error: Username sudah terdaftar."

        account_number = generate_account_number()
        while execute_query("SELECT id FROM accounts WHERE account_number = %s", (account_number,)):
            account_number = generate_account_number()

        user_q = "INSERT INTO users (username, password) VALUES (%s, %s)"
        user_res = execute_query(user_q, (username, hashed_password), fetch=False)
        if not user_res:
            return "error: Gagal membuat user."

        user_row = execute_query("SELECT id FROM users WHERE username = %s", (username,))
        if not user_row:
            return "error: Gagal mengambil data user."
        user_id = user_row[0]['id']

        acc_q = "INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)"
        acc_res = execute_query(acc_q, (user_id, account_number, 0.00), fetch=False)
        if not acc_res:
            return "error: Gagal membuat akun."

        return f"success: Registrasi berhasil. Nomor rekening: {account_number}"
    except Exception as e:
        return f"error: Registrasi gagal. {e}"

def login(username, password):
    try:
        hashed_password = hash_password(password)
        q = """
            SELECT u.id, u.username, a.account_number, a.balance, a.created_at
            FROM users u
            JOIN accounts a ON a.user_id = u.id
            WHERE u.username = %s AND u.password = %s
        """
        rows = execute_query(q, (username, hashed_password))
        if not rows:
            return "error: Username atau password salah."
        r = rows[0]
        return f"success: Login berhasil. Rekening: {r['account_number']}, Saldo: Rp {float(r['balance']):.2f}, Dibuat: {r['created_at']}"
    except Exception as e:
        return f"error: Login gagal. {e}"

def get_account_info(account_number):
    try:
        q = """
            SELECT u.username, a.account_number, a.balance, a.created_at
            FROM accounts a
            JOIN users u ON u.id = a.user_id
            WHERE a.account_number = %s
        """
        rows = execute_query(q, (account_number,))
        if not rows:
            return "error: Rekening tidak ditemukan."
        r = rows[0]
        return (
            f"success: username={r['username']}, "
            f"account_number={r['account_number']}, "
            f"balance={float(r['balance']):.2f}, "
            f"created_at={r['created_at']}"
        )
    except Exception as e:
        return f"error: Gagal mengambil info rekening. {e}"