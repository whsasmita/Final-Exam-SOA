# project_dana/entities/user.py

class User:
    def __init__(self, user_id, username, password_hash, created_at):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
        
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"