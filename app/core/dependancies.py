# core/dependencies.py
from fastapi import Depends, HTTPException, status
from app.core.security import oauth2_scheme, decode_access_token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Authenticate the user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    user_id = payload.get("sub")
    # Here you would fetch the user from the database (omitted for brevity)
    # For now, just return the user identifier:
    return {"user_id": user_id}
