from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client["movie_booking_db"]

admin_email = "admin@movietix.com"
admin_password = "admin123"

if db.users.find_one({"email": admin_email}):
    print(f"Akun admin '{admin_email}' sudah ada di database.")
else:
    db.users.insert_one({
        "nama": "Admin MovieTix",
        "email": admin_email,
        "password": generate_password_hash(admin_password),
        "role": "admin"
    })
    print("Akun admin berhasil dibuat!")
    print(f"Email    : {admin_email}")
    print(f"Password : {admin_password}")
