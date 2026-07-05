import requests
from pymongo import MongoClient

# ==========================================
# KONFIGURASI DATABASE & API
# ==========================================
# Koneksi ke MongoDB lokal
client = MongoClient("mongodb://localhost:27017/")
db = client['movie_booking_db'] # Pastikan nama database sesuai dengan di app.py

# TODO: Masukkan API Key TMDB kamu di sini
TMDB_API_KEY = "62efbed21d863f02bdca0614d8f2cb5c"
BASE_URL = "https://api.themoviedb.org/3"

def fetch_and_seed_movies():
    print("Mulai mengambil data dari TMDB API...")
    
    # Endpoint untuk mengambil film-film populer saat ini
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=id-ID&page=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Akan memicu error jika koneksi gagal
        data = response.json()
        
        movies_to_insert = []
        
        for item in data.get('results', [])[:20]: # Mengambil 10 film teratas saja
            # Menyiapkan URL poster (TMDB hanya memberikan path relatif)
            poster_path = item.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            
            # TMDB list tidak menyertakan durasi (runtime), jadi kita beri nilai default 120 menit
            # Untuk produksi nyata, kita harus memanggil endpoint detail per film
            movie_doc = {
                "judul": item.get('title'),
                "sinopsis": item.get('overview'),
                "durasi": 120, 
                "poster_url": poster_url,
                "rating": item.get('vote_average')
            }
            movies_to_insert.append(movie_doc)
            print(f"Mengambil data: {movie_doc['judul']}")
            
        if movies_to_insert:
            # Kosongkan koleksi lama agar tidak terjadi duplikasi saat script dijalankan ulang
            db.movies.delete_many({})
            
            # Masukkan data baru ke MongoDB
            hasil = db.movies.insert_many(movies_to_insert)
            print("=======================================")
            print(f"SUKSES! {len(hasil.inserted_ids)} film berhasil dimasukkan ke MongoDB.")
            print("=======================================")
        else:
            print("Tidak ada data film yang ditemukan.")
            
    except Exception as e:
        print(f"Terjadi kesalahan saat menghubungi API: {e}")

if __name__ == "__main__":
    fetch_and_seed_movies()