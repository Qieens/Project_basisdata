from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
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

@admin_bp.route("/admin/movie/edit/<id>", methods=["POST"])
@admin_required
def admin_edit_movie(id):
    db.movies.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "judul": request.form.get("judul"),
            "genre": request.form.get("genre"),
            "durasi": int(request.form.get("durasi") or 0),
            "rating": float(request.form.get("rating") or 0),
            "poster_url": request.form.get("poster_url"),
            "sinopsis": request.form.get("sinopsis")
        }}
    )
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/bookings")
@admin_required
def admin_bookings():
    bookings = list(db.bookings.find().sort("_id", -1))
    return render_template(
        "admin_bookings.html",
        bookings=bookings,
        username=session["user"],
        active_page="bookings"
    )


@admin_bp.route("/admin/booking/status/<id>", methods=["POST"])
@admin_required
def admin_update_booking_status(id):
    new_status = request.form.get("status") or request.json.get("status")
    if new_status not in ["confirmed", "pending", "cancelled"]:
        return jsonify({"status": "error", "message": "Status tidak valid."}), 400
    db.bookings.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": new_status}}
    )
    return redirect(url_for("admin.admin_bookings"))


@admin_bp.route("/admin/booking/delete/<id>", methods=["POST"])
@admin_required
def admin_delete_booking(id):
    db.bookings.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin.admin_bookings"))


@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    users = list(db.users.find())
    return render_template(
        "admin_users.html",
        users=users,
        username=session["user"],
        active_page="users"
    )


@admin_bp.route("/admin/user/delete/<id>", methods=["POST"])
@admin_required
def admin_delete_user(id):
    if session.get("user_id") == id:
        return redirect(url_for("admin.admin_users"))
    db.users.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin.admin_users"))