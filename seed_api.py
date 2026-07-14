import requests
import sys
from pymongo import MongoClient

sys.stdout.reconfigure(encoding='utf-8')

client = MongoClient("mongodb://localhost:27017/")
db = client['movie_booking_db']

TMDB_API_KEY = "62efbed21d863f02bdca0614d8f2cb5c"
BASE_URL = "https://api.themoviedb.org/3"

def get_genre_map():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=id-ID"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {g["id"]: g["name"] for g in data.get("genres", [])}

def fetch_and_seed_movies():
    print("Mulai mengambil data dari TMDB API...")

    genre_map = get_genre_map()
    print(f"Berhasil mengambil {len(genre_map)} genre dari TMDB.")

    url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=id-ID&page=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        movies_to_insert = []

        for item in data.get('results', [])[:20]:
            poster_path = item.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

            genre_ids = item.get('genre_ids', [])
            genre_names = [genre_map[gid] for gid in genre_ids if gid in genre_map]
            genre_str = genre_names[0] if genre_names else ""

            movie_doc = {
                "judul": item.get('title'),
                "sinopsis": item.get('overview'),
                "durasi": 120,
                "genre": genre_str,
                "poster_url": poster_url,
                "rating": item.get('vote_average')
            }
            movies_to_insert.append(movie_doc)
            print(f"Mengambil data: {movie_doc['judul']} | Genre: {genre_str}")

        if movies_to_insert:
            db.movies.delete_many({})
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
