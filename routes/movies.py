from flask import Blueprint, render_template, request, session, redirect, url_for
from bson.objectid import ObjectId
from database import db
from utils import login_required
from datetime import datetime

movies_bp = Blueprint('movies', __name__)

@movies_bp.route("/movies")
@login_required
def movies():
    query = request.args.get("q", "").strip()
    selected_genre = request.args.get("genre", "").strip()

    filter_query = {}
    if query:
        filter_query["judul"] = {"$regex": query, "$options": "i"}
    if selected_genre:
        filter_query["genre"] = selected_genre

    movies_list = list(db.movies.find(filter_query))
    genres = [g for g in db.movies.distinct("genre") if g]

    return render_template(
        "movies.html",
        movies=movies_list,
        genres=genres,
        query=query,
        selected_genre=selected_genre,
        username=session["user"],
        active_page="movies"
    )

@movies_bp.route("/movie/<id>")
@login_required
def movie_detail(id):
    movie = db.movies.find_one({"_id": ObjectId(id)})
    if not movie:
        return redirect(url_for("dashboard.dashboard"))

    schedules = list(db.schedules.find({"judul": movie["judul"]}))
    
    # ==========================================================
    # LOGIKA PERBANDINGAN WAKTU YANG PRESISI
    # ==========================================================
    # Mengambil objek waktu saat ini
    waktu_sekarang_obj = datetime.now().time()

    for schedule in schedules:
        # Mengubah string jam dari database ("18:45") menjadi objek waktu
        jam_jadwal_obj = datetime.strptime(schedule["jam"], "%H:%M").time()
        
        # Bandingkan secara matematis
        if waktu_sekarang_obj > jam_jadwal_obj:
            schedule["is_passed"] = True
        else:
            schedule["is_passed"] = False
    # ==========================================================

    return render_template(
        "detail_movie.html",
        movie=movie,
        schedules=schedules,
        username=session["user"]
    )