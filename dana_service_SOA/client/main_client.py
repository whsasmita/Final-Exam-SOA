import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.account_client import handle_login, handle_register, handle_get_account_info, validate_token
from client.topup_client import handle_topup
from client.transaction_client import handle_transfer

# Session user dengan JWT token
current_user = {
    'username': None,
    'account_number': None,
    'token': None,
    'logged_in': False
}

def display_main_menu():
    """Menu awal sebelum login/register."""
    print("\n===============================")
    print("      DANA SERVICE CLIENT      ")
    print("===============================")
    print("1. Login Akun")
    print("2. Register Akun")
    print("3. Keluar")
    print("===============================")

def display_user_menu():
    """Menu setelah login/register."""
    print(f"\n===============================")
    print(f"   Selamat datang, {current_user['username']}!")
    print(f"   Rekening: {current_user['account_number']}")
    print("===============================")
    print("1. Cek Saldo & Info Rekening")
    print("2. Top Up Saldo")
    print("3. Transfer Dana")
    print("4. Logout")
    print("===============================")

def parse_token_from_response(msg: str):
    """Extract JWT token dari response."""
    try:
        if "Token:" in msg:
            return msg.split("Token:")[-1].strip()
        return None
    except Exception:
        return None

def parse_account_from_register(msg: str):
    """Extract nomor rekening dari response register."""
    try:
        if "Nomor rekening:" in msg:
            part = msg.split("Nomor rekening:")[1]
            return part.split(".")[0].strip()
        return None
    except Exception:
        return None

def check_token_validity():
    """Cek apakah token masih valid."""
    if not current_user['token']:
        return False
    
    valid, result = validate_token(current_user['token'])
    if not valid:
        print(f"⚠️ Session expired: {result}")
        print("Silakan login kembali.")
        logout()
        return False
    return True

def handle_register_flow():
    print("\n--- REGISTER AKUN ---")
    username = input("Masukkan username: ").strip()
    password = input("Masukkan password: ").strip()

    result = handle_register(username, password)
    if result and str(result).lower().startswith("success"):
        # Extract token dan account number
        token = parse_token_from_response(str(result))
        account_number = parse_account_from_register(str(result))
        
        if token and account_number:
            current_user['username'] = username
            current_user['account_number'] = account_number
            current_user['token'] = token
            current_user['logged_in'] = True
            print("✅ Registrasi & login berhasil dengan JWT token!")
            return True
        else:
            print("⚠️ Tidak bisa mengambil token atau nomor rekening dari response.")
    
    print("❌ Registrasi gagal.")
    return False

def handle_login_flow():
    print("\n--- LOGIN AKUN ---")
    username = input("Masukkan username: ").strip()
    password = input("Masukkan password: ").strip()

    result = handle_login(username, password)
    if result and str(result).lower().startswith("success"):
        # Extract token dari response
        token = parse_token_from_response(str(result))
        
        if token:
            # Validasi token untuk mendapatkan account info
            valid, token_info = validate_token(token)
            if valid and "Account:" in token_info:
                account_number = token_info.split("Account:")[-1].strip()
                
                current_user['username'] = username
                current_user['account_number'] = account_number
                current_user['token'] = token
                current_user['logged_in'] = True
                print("✅ Login berhasil dengan JWT token!")
                return True
            else:
                print("⚠️ Token tidak valid atau tidak bisa extract account info.")
        else:
            print("⚠️ Tidak bisa mengambil token dari response.")
    
    print("❌ Login gagal.")
    return False

def handle_check_balance():
    """Menampilkan info rekening dari service dengan JWT token."""
    # Cek token validity dulu
    if not check_token_validity():
        return
    
    print(f"\n--- INFO REKENING ---")
    print(f"👤 Username: {current_user['username']}")
    print(f"📋 Nomor Rekening: {current_user['account_number']}")
    
    # Panggil dengan token dan account_number
    resp = handle_get_account_info(current_user['token'], current_user['account_number'])
    if not resp:
        input("\nTekan Enter untuk kembali ke menu...")
        return
    
    try:
        data_part = str(resp).split("success:")[-1].strip()
        kv = {}
        for part in data_part.split(","):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                kv[k.strip()] = v.strip()
        saldo = float(kv.get('balance', '0'))
        created = kv.get('created_at', '-')
        print(f"💰 Saldo: Rp. {saldo:,.2f}")
        print(f"📅 Tanggal Buat: {created}")
    except Exception:
        print(resp)
    
    input("\nTekan Enter untuk kembali ke menu...")

def handle_topup_flow():
    """Handle topup dengan JWT token validation."""
    if not check_token_validity():
        return
    
    print("\n--- TOP UP SALDO ---")
    amount = input("Masukkan jumlah top up: ").strip()
    handle_topup(current_user['token'], current_user['account_number'], amount)

def handle_transfer_flow():
    """Handle transfer dengan JWT token validation."""
    if not check_token_validity():
        return
    
    print("\n--- TRANSFER DANA ---")
    receiver_account = input("Nomor rekening penerima: ").strip()
    amount = input("Masukkan jumlah transfer: ").strip()
    handle_transfer(current_user['token'], current_user['account_number'], receiver_account, amount)

def logout():
    """Logout dan clear session."""
    current_user['username'] = None
    current_user['account_number'] = None
    current_user['token'] = None
    current_user['logged_in'] = False
    print("✅ Logout berhasil.")

def main():
    while True:
        if not current_user['logged_in']:
            display_main_menu()
            choice = input("Pilih opsi (1-3): ").strip()
            if choice == '1':
                handle_login_flow()
            elif choice == '2':
                handle_register_flow()
            elif choice == '3':
                print("Terima kasih, sampai jumpa!")
                break
            else:
                print("❌ Pilihan tidak valid. Silakan coba lagi.")
        else:
            display_user_menu()
            choice = input("Pilih opsi (1-4): ").strip()
            if choice == '1':
                handle_check_balance()
            elif choice == '2':
                handle_topup_flow()
            elif choice == '3':
                handle_transfer_flow()
            elif choice == '4':
                logout()
            else:
                print("❌ Pilihan tidak valid. Silakan coba lagi.")

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🚀 Memulai DANA Service Client dengan JWT Authentication...")
    main()