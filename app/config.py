from dataclasses import dataclass
import os
import dotenv

dotenv_path = '.env' 
dotenv.load_dotenv()

@dataclass(frozen=True)
class Config:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "gestion_salas")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "shhh")
