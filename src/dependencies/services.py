from fastapi import Request, Depends, status
from fastapi.exceptions import HTTPException
from .database import get_db_connection
from jose import jwt
from icecream import ic
import logging

SECRET_KEY = "clave"
ALGORITHM = "HS256"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_user_info(request: Request, db: tuple = Depends(get_db_connection)):
    token = request.headers["Authorization"].split(" ")[1]
    ic(token)
    if not token:
        raise HTTPException(status_code=400, detail='Token is missing')

    payload = decode_token(token)
    connection, cursor = db

    ic(payload)
    cursor.execute('SELECT * FROM users WHERE id = %s', (payload['user_id'],))

    user = cursor.fetchone()

    return user
