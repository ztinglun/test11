import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("請先設定 .env 的 DATABASE_URL")
    return psycopg.connect(DATABASE_URL)