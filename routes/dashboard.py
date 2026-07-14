from flask import Blueprint, render_template, session
from database import db
from utils import login_required

dashboard_bp = Blueprint('dashboard', __name__)

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
