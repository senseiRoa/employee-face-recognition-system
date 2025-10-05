"""
Utilities for password handling
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Generates a secure hash of the password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Password hash as a string
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies if a password matches its hash

    Args:
        password: Plain text password
        hashed: Password hash

    Returns:
        True if the password is correct, False otherwise
    """
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


if __name__ == "__main__":
    # Generate hash for the password admin123
    print("Hash for admin123:")
    print(hash_password("admin123"))
