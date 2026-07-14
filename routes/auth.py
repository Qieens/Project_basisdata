from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'user')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.users.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session["user"] = user["nama"]
            session["user_id"] = str(user["_id"])
            session["role"] = user.get("role", "user")
            if session["role"] == "admin":
                return jsonify({"status": "success", "redirect_url": url_for('admin.admin_dashboard')})
            return jsonify({"status": "success", "redirect_url": url_for('dashboard.dashboard')})
        else:
            return jsonify({"status": "error", "message": "Email atau Password salah!"})

    return render_template('login.html', login_role=role)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    role = request.args.get('role', 'user')

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
        return redirect(url_for("auth.login", role="user"))

    return render_template("register.html", login_role=role)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@auth_bp.route("/register-admin", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        kode_admin = request.form.get("kode_admin", "").strip()

        if kode_admin != Config.ADMIN_CODE:
            return jsonify({"status": "error", "message": "Kode admin salah!"})

        if db.users.find_one({"email": email}):
            return jsonify({"status": "error", "message": "Email sudah terdaftar!"})

        db.users.insert_one({
            "nama": nama,
            "email": email,
            "password": generate_password_hash(password),
            "role": "admin"
        })
        return jsonify({"status": "success", "redirect_url": url_for("auth.login", role="admin")})

    return render_template("register_admin.html")
