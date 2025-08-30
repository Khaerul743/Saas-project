from passlib.context import CryptContext

# Setup hashing dengan bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash plain password menggunakan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi apakah plain_password cocok dengan hashed_password."""
    return pwd_context.verify(plain_password, hashed_password)
