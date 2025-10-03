import hashlib
import secrets

def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return f"{salt}:{pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, pwd_hash = hashed_password.split(':')
        return pwd_hash == hashlib.sha256(plain_password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    except ValueError:
        return False
