#!/usr/bin/env python3
"""
Dana Service CLI App
=====================
Login/Register via FastAPI Auth, then access SOAP services (Topup/Transfer) via menu.
"""

import requests
import json
import sys
from pathlib import Path
from zeep import Client
import logging

# Disable zeep logging
logging.getLogger('zeep').setLevel(logging.WARNING)

# Configuration
FASTAPI_AUTH_URL = "http://localhost:8004/api/v1"
FASTAPI_GATEWAY_URL = "http://localhost:8005/api/v1"
SOAP_ACCOUNT_URL = "http://localhost:8001?wsdl"
SOAP_TOPUP_URL = "http://localhost:8002?wsdl"
SOAP_TRANSACTION_URL = "http://localhost:8003?wsdl"

# Global state
current_user = None
current_token = None
current_account = None


def get_soap_client(wsdl_url):
    """Get SOAP client from WSDL."""
    try:
        return Client(wsdl_url)
    except Exception as e:
        print(f"❌ Error connecting to SOAP service: {e}")
        return None


def register_user():
    """Register new user via FastAPI."""
    print("\n" + "=" * 50)
    print("REGISTER")
    print("=" * 50)
    username = input("Username: ").strip()
    if not username:
        print("❌ Username tidak boleh kosong")
        return False

    password = input("Password: ").strip()
    if not password:
        print("❌ Password tidak boleh kosong")
        return False

    try:
        resp = requests.post(
            f"{FASTAPI_AUTH_URL}/register",
            json={"username": username, "password": password},
            timeout=5
        )
        data = resp.json()

        if resp.status_code != 200:
            print(f"❌ Register gagal: {data.get('detail', 'Unknown error')}")
            return False

        global current_user, current_token, current_account
        current_user = username
        current_token = data.get("access_token")
        current_account = data.get("account_number")

        print(f"✅ Registrasi berhasil!")
        print(f"   Username: {current_user}")
        print(f"   Account Number: {current_account}")
        print(f"   Token: {current_token[:20]}...")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def login_user():
    """Login user via FastAPI auth."""
    print("\n" + "=" * 50)
    print("LOGIN")
    print("=" * 50)
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    try:
        resp = requests.post(
            f"{FASTAPI_AUTH_URL}/login",
            json={"username": username, "password": password},
            timeout=5
        )
        data = resp.json()

        if resp.status_code != 200:
            print(f"❌ Login gagal: {data.get('detail', 'Unknown error')}")
            return False

        global current_user, current_token, current_account
        current_user = username
        current_token = data.get("access_token")
        current_account = data.get("account_number")

        print(f"✅ Login berhasil!")
        print(f"   Username: {current_user}")
        print(f"   Account: {current_account}")
        print(f"   Token: {current_token[:20]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_account_info():
    """Get account info from FastAPI Gateway."""
    print("\n" + "=" * 50)
    print("INFORMASI REKENING")
    print("=" * 50)

    try:
        headers = {"Authorization": f"Bearer {current_token}"}
        resp = requests.get(
            f"{FASTAPI_GATEWAY_URL}/account/info",
            headers=headers,
            timeout=5
        )
        
        if resp.status_code != 200:
            data = resp.json()
            print(f"❌ Error: {data.get('detail', 'Unknown error')}")
            return
        
        data = resp.json()
        print(f"\n✅ {data.get('message')}")

    except Exception as e:
        print(f"❌ Error: {e}")


def topup_menu():
    """Topup dana via FastAPI Gateway."""
    print("\n" + "=" * 50)
    print("TOPUP DANA")
    print("=" * 50)

    try:
        amount = input("Jumlah topup (Rp): ").strip()
        if not amount:
            print("❌ Jumlah topup tidak boleh kosong")
            return

        headers = {"Authorization": f"Bearer {current_token}"}
        resp = requests.post(
            f"{FASTAPI_GATEWAY_URL}/topup",
            json={"amount": float(amount)},
            headers=headers,
            timeout=5
        )
        
        data = resp.json()
        
        if resp.status_code != 200:
            print(f"❌ Error: {data.get('detail', 'Unknown error')}")
            return
        
        print(f"\n✅ {data.get('message')}")
        if data.get('event_published'):
            print("📨 Event notifikasi telah dikirim ke Kafka")

    except Exception as e:
        print(f"❌ Error: {e}")


def transfer_menu():
    """Transfer dana via FastAPI Gateway."""
    print("\n" + "=" * 50)
    print("TRANSFER DANA")
    print("=" * 50)

    try:
        receiver = input("Nomor rekening penerima: ").strip()
        if not receiver:
            print("❌ Nomor rekening penerima tidak boleh kosong")
            return

        amount = input("Jumlah transfer (Rp): ").strip()
        if not amount:
            print("❌ Jumlah transfer tidak boleh kosong")
            return

        headers = {"Authorization": f"Bearer {current_token}"}
        resp = requests.post(
            f"{FASTAPI_GATEWAY_URL}/transfer",
            json={
                "receiver_account_number": receiver,
                "amount": float(amount)
            },
            headers=headers,
            timeout=5
        )
        
        data = resp.json()
        
        if resp.status_code != 200:
            print(f"❌ Error: {data.get('detail', 'Unknown error')}")
            return
        
        print(f"\n✅ {data.get('message')}")
        if data.get('event_published'):
            print("📨 Event notifikasi telah dikirim ke Kafka")

    except Exception as e:
        print(f"❌ Error: {e}")


def edit_account_menu():
    """Edit account (username/password) via FastAPI Auth."""
    print("\n" + "=" * 50)
    print("EDIT ACCOUNT")
    print("=" * 50)
    print("Kosongkan field jika tidak ingin diubah")
    print("=" * 50)

    try:
        new_username = input("Username baru (kosongkan jika tidak diubah): ").strip()
        new_password = input("Password baru (kosongkan jika tidak diubah): ").strip()

        if not new_username and not new_password:
            print("❌ Minimal satu field harus diisi")
            return

        payload = {}
        if new_username:
            payload["username"] = new_username
        if new_password:
            payload["password"] = new_password

        headers = {"Authorization": f"Bearer {current_token}"}
        resp = requests.put(
            f"{FASTAPI_AUTH_URL}/account/update",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        data = resp.json()
        
        if resp.status_code != 200:
            print(f"❌ Error: {data.get('detail', 'Unknown error')}")
            return
        
        # Update global username if changed
        global current_user
        if new_username:
            current_user = new_username
        
        print(f"\n✅ {data.get('message')}")
        print(f"   Username sekarang: {data.get('username')}")
        if new_password:
            print("   Password berhasil diubah")

    except Exception as e:
        print(f"❌ Error: {e}")


def show_menu():
    """Show main menu."""
    print("\n" + "=" * 50)
    if current_user:
        print(f"DANA SERVICE CLI - User: {current_user} ({current_account})")
        print("=" * 50)
        print("1. Get Account Info")
        print("2. Topup Dana")
        print("3. Transfer Dana")
        print("4. Edit Account")
        print("5. Logout")
        print("0. Exit")
    else:
        print("DANA SERVICE CLI - NOT LOGGED IN")
        print("=" * 50)
        print("1. Register")
        print("2. Login")
        print("0. Exit")
    print("=" * 50)


def logout():
    """Logout user."""
    global current_user, current_token, current_account
    current_user = None
    current_token = None
    current_account = None
    print("\n✅ Logout berhasil!")


def main():
    """Main CLI loop."""
    print("\n" + "=" * 50)
    print("SELAMAT DATANG DI DANA SERVICE CLI")
    print("=" * 50)
    print("Pastikan services sedang berjalan:")
    print("  - SOAP: ports 8001, 8002, 8003")
    print("  - FastAPI Auth: port 8004")
    print("  - FastAPI Gateway: port 8005")
    print("  - Kafka Consumer: event-consumer")
    print("=" * 50)

    while True:
        show_menu()
        
        if current_user:
            # Authenticated menu
            choice = input("Pilih menu (0-5): ").strip()
            
            if choice == "1":
                get_account_info()
            elif choice == "2":
                topup_menu()
            elif choice == "3":
                transfer_menu()
            elif choice == "4":
                edit_account_menu()
            elif choice == "5":
                logout()
            elif choice == "0":
                print("\n👋 Terima kasih! Sampai jumpa.")
                break
            else:
                print("❌ Menu tidak valid")
        else:
            # Pre-authentication menu
            choice = input("Pilih menu (0-2): ").strip()
            
            if choice == "1":
                if register_user():
                    print("\n✅ Anda sekarang sudah login!")
            elif choice == "2":
                login_user()
            elif choice == "0":
                print("\n👋 Terima kasih! Sampai jumpa.")
                break
            else:
                print("❌ Menu tidak valid")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan.")
        sys.exit(0)
