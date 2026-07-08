from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from database import db

# 1. Deklarasi Blueprint untuk Dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# --- DECORATOR (Sebaiknya dipindahkan juga jika dibutuhkan di file ini) ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            # PENTING: Karena login ada di blueprint 'auth', arahkan ke 'auth.login'
            return redirect(url_for("auth.login")) 
        return f(*args, **kwargs)
    return decorated

# 2. Pindahkan fungsi dashboard ke sini, ubah @app.route menjadi @dashboard_bp.route
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    movies = list(db.movies.find())

    return render_template(
        "dashboard.html",
        movies=movies,
        username=session["user"],
        active_page="dashboard"
    )