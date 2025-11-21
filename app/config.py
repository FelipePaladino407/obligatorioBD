from dataclasses import dataclass
import os
import dotenv

dotenv_path = '.env' 
dotenv.load_dotenv()

@dataclass(frozen=True)

class Config:
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_NAME = os.getenv("DB_NAME", "reservas_salas_estuido")

    DB_USER_ADMIN = os.getenv("DB_USER_ADMIN")
    DB_PASS_ADMIN = os.getenv("DB_PASS_ADMIN")

    DB_USER_APP = os.getenv("DB_USER_APP")
    DB_PASS_APP = os.getenv("DB_PASS_APP")

    SECRET_KEY = os.getenv("SECRET_KEY", "lamentable")

