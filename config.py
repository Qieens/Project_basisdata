import os
from dotenv import load_dotenv

# Membaca file .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    ADMIN_CODE = os.getenv("ADMIN_CODE", "MOVETIX2026")