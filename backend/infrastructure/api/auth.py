import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import requests

# Get configuration from environment variables
INTROSPECTION_URL = os.getenv("INTROSPECTION_URL", "http://localhost:8080/connect/introspect")
# The Basic auth header for the introspection endpoint
INTROSPECTION_AUTH_HEADER = os.getenv("INTROSPECTION_AUTH_HEADER", "Basic RVNEQVZBUElSZXNvdXJjZTpwcnVlYmFkZWZ1ZWdv")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to validate a JWT token using an introspection endpoint.

    - Extracts the token from the Authorization header.
    - Sends it to the introspection endpoint.
    - Checks for an active token in the response.
    - Returns the JSON payload from the introspection endpoint if the token is active.
    - Raises HTTPException for invalid tokens or communication errors.
    """
    try:
        response = requests.post(
            INTROSPECTION_URL,
            headers={"Authorization": INTROSPECTION_AUTH_HEADER},
            data={"token": token}
        )
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        introspection_data = response.json()

        if not introspection_data.get("active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is inactive or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return introspection_data

    except requests.exceptions.RequestException as e:
        # Handle network errors or non-2xx responses from the introspection endpoint
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Introspection endpoint is unavailable: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
