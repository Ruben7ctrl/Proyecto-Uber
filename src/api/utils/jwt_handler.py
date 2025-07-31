import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "your_secret_key_here"  # Cambia esto por una clave segura y secreta
ALGORITHM = "HS256"
EXPIRATION_HOURS = 24


def create_token(email):
    payload = {
        "email": email,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT >= 2.0 devuelve string, si tienes versión antigua puede ser bytes, ajusta si necesario
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError as e:
        raise e
    except InvalidTokenError as e:
        raise e
