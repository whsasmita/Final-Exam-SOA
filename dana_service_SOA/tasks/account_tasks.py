import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import execute_query

def cleanup_inactive_users():
    """
    Menghapus pengguna yang tidak memiliki akun rekening.
    """
    print("Memulai tugas pembersihan pengguna tidak aktif...")
    
    query = """
    SELECT u.id, u.username
    FROM users u
    LEFT JOIN accounts a ON u.id = a.user_id
    WHERE a.user_id IS NULL;
    """
    
    inactive_users = execute_query(query)
    
    if not inactive_users:
        print("Tidak ada pengguna tidak aktif yang ditemukan.")
        return

    print(f"Ditemukan {len(inactive_users)} pengguna tidak aktif.")
    
    for user in inactive_users:
        delete_query = "DELETE FROM users WHERE id = %s"
        execute_query(delete_query, (user['id'],), fetch=False)
        print(f"  - Pengguna '{user['username']}' dengan ID {user['id']} telah dihapus.")
    
    print("Pembersihan selesai.")

if __name__ == '__main__':
    cleanup_inactive_users()