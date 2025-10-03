# WARNING: This is a placeholder implementation and is NOT a secure JWT implementation.
# It is used to fulfill the project structure requirements without adding new dependencies.
# For a production environment, a proper JWT library (like python-jose or PyJWT) should be used.

import time
from typing import Dict

# This would normally be a securely stored secret key
SECRET_KEY = "a_very_insecure_secret_key"

def create_access_token(data: dict, expires_delta: int = 3600) -> str:
    """Creates a simple, insecure token."""
    payload = data.copy()
    expiration = int(time.time()) + expires_delta
    payload["exp"] = expiration
    # In a real JWT, this would be a signed, base64-encoded string.
    # Here, we are just joining the dictionary items.
    token_str = ",".join([f"{k}={v}" for k, v in payload.items()])
    return f"{token_str}.{SECRET_KEY}" # Unsigned, just appended secret

def decode_token(token: str) -> Dict[str, any]:
    """Decodes a simple, insecure token."""
    try:
        token_parts = token.split('.')
        if len(token_parts) != 2 or token_parts[1] != SECRET_KEY:
            return None # Invalid token format or secret

        payload_str = token_parts[0]
        payload = dict(item.split('=') for item in payload_str.split(','))

        if int(payload.get("exp", 0)) < int(time.time()):
            return None # Token has expired

        return payload
    except Exception:
        return None
