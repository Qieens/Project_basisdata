from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from database import db
from utils import login_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.users.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        nama = request.form.get("nama")
        email = request.form.get("email")
        password = request.form.get("password")

        update_data = {
            "nama": nama,
            "email": email
        }

        if password:
            update_data["password"] = generate_password_hash(password)

        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )

        session["user"] = nama
        user = db.users.find_one({"_id": user["_id"]})

    return render_template(
        "profile.html",
        user=user,
        username=session["user"],
        active_page="profile"
    )