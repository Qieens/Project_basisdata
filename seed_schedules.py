from pymongo import MongoClient
import random

# Koneksi ke database
client = MongoClient("mongodb://localhost:27017/")
db = client['movie_booking_db'] # Pastikan nama database sesuai

def generate_schedules():
    print("Mengambil data film dari database...")
    movies = list(db.movies.find())
    
    if not movies:
        print("Belum ada film di database! Jalankan seed_api.py terlebih dahulu.")
        return

    # Kosongkan jadwal lama agar tidak menumpuk
    db.schedules.delete_many({})
    
    schedules_to_insert = []
    
    # Opsi studio, jam tayang, dan harga
    studios = ["Studio 1", "Studio 2", "Studio Premiere", "Studio 3"]
    times = ["13:00", "15:30", "18:45", "20:00", "21:15"]
    prices = [35000, 40000, 50000]

    for movie in movies:
        # Buat 2 sampai 4 jadwal acak untuk setiap film
        num_schedules = random.randint(2, 4)
        
        # Ambil sampel jam acak yang tidak kembar
        selected_times = random.sample(times, num_schedules)
        selected_times.sort() # Urutkan jam tayang dari yang paling awal
        
        for jam in selected_times:
            schedule = {
                "judul": movie["judul"],  # Menghubungkan jadwal dengan judul film
                "studio": random.choice(studios),
                "jam": jam,
                "harga": random.choice(prices)
            }
            schedules_to_insert.append(schedule)
            print(f"Jadwal dibuat: {movie['judul']} - {jam}")

    # Masukkan semua jadwal ke MongoDB
    if schedules_to_insert:
        hasil = db.schedules.insert_many(schedules_to_insert)
        print("=================================================")
        print(f"SUKSES! {len(hasil.inserted_ids)} jadwal berhasil ditambahkan.")
        print("=================================================")

if __name__ == "__main__":
    generate_schedules()