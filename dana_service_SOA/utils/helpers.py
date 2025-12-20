import random
import string
import hashlib

def generate_account_number():
    """Menghasilkan nomor rekening acak dengan 10 digit."""
    return ''.join(random.choices(string.digits, k=10))

def hash_password(password):
    """Mengenkripsi password menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()