from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db  # Pastikan ini mengarah ke koneksi database Anda

# 1. Deklarasi Blueprint
# Parameter pertama 'auth' adalah nama blueprint
auth_bp = Blueprint('auth', __name__)

# 2. Ganti @app.route menjadi @nama_blueprint.route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.users.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session["user"] = user["nama"]
            session["user_id"] = str(user["_id"])
            session["role"] = user.get("role", "user")
            # Perhatikan perubahan pada url_for di bawah ini
            return jsonify({"status": "success", "redirect_url": url_for('dashboard.dashboard')})
        else:
            return jsonify({"status": "error", "message": "Email atau Password salah!"})

    return render_template('login.html')

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nama = request.form["nama"]
        email = request.form["email"]
        password = request.form["password"]

        if db.users.find_one({"email": email}):
            return "Email sudah terdaftar!", 400

        db.users.insert_one({
            "nama": nama,
            "email": email,
            "password": generate_password_hash(password),
            "role": "user"
        })
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))