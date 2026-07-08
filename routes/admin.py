from flask import Blueprint, render_template, request, session, redirect, url_for
from bson.objectid import ObjectId
from database import db
from utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    movies_list = list(db.movies.find())
    schedules_list = list(db.schedules.find())
    total_users = db.users.count_documents({})
    total_bookings = db.bookings.count_documents({})

    revenue_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    revenue_result = list(db.bookings.aggregate(revenue_pipeline))
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    return render_template(
        "admin_dashboard.html",
        movies=movies_list,
        schedules=schedules_list,
        total_movies=len(movies_list),
        total_users=total_users,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        username=session["user"]
    )

@admin_bp.route("/admin/movie/add", methods=["POST"])
@admin_required
def admin_add_movie():
    movie_doc = {
        "judul": request.form.get("judul"),
        "genre": request.form.get("genre"),
        "durasi": int(request.form.get("durasi") or 0),
        "rating": float(request.form.get("rating") or 0),
        "poster_url": request.form.get("poster_url"),
        "sinopsis": request.form.get("sinopsis")
    }
    db.movies.insert_one(movie_doc)
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin/movie/delete/<id>", methods=["POST"])
@admin_required
def admin_delete_movie(id):
    db.movies.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin.admin_dashboard"))