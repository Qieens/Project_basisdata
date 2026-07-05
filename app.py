from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from config import Config
from database import db
from bson.objectid import ObjectId

# Membuat aplikasi Flask
app = Flask(__name__)

# Mengambil konfigurasi
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# ===========================
# HOME
# ===========================

@app.route("/")
def home():
    return render_template("home.html")


# ===========================
# LOGIN
# ===========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.users.find_one({"email": email})

        if user and str(user['password']) == str(password):
            # Menyimpan sesi agar user tidak dilempar balik ke login
            session["user"] = user["nama"]
            
            # Berhasil
            return jsonify({
                "status": "success", 
                "redirect_url": url_for('dashboard')
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Email atau Password yang kamu masukkan salah!"
            })

    # Jika user baru membuka halaman (GET)
    return render_template('login.html')

# ===========================
# REGISTER
# ===========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        print("===== REGISTER DIJALANKAN =====")

        nama = request.form["nama"]
        email = request.form["email"]
        password = request.form["password"]

        print("Nama :", nama)
        print("Email :", email)
        print("Password :", password)

        hasil = db.users.insert_one({
            "nama": nama,
            "email": email,
            "password": password
        })

        print("BERHASIL INSERT")
        print("ID :", hasil.inserted_id)

        return redirect(url_for("login"))

    return render_template("register.html")

# ===========================
# DASHBOARD
# ===========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    movies = list(db.movies.find())

    return render_template(
        "dashboard.html",
        movies=movies,
        username=session["user"]
    )

# ===========================
# MOVIE DETAIL
# ===========================
@app.route("/movie/<id>")
def movie_detail(id):

    if "user" not in session:
        return redirect(url_for("login"))

    movie = db.movies.find_one({"_id": ObjectId(id)})

    schedules = list(
        db.schedules.find(
            {"judul": movie["judul"]}
        )
    )

    return render_template(
        "detail_movie.html",
        movie=movie,
        schedules=schedules,
        username=session["user"]
    )

# ===========================
# BOOKING
# ===========================

@app.route("/booking/<schedule_id>")
def booking(schedule_id):

    if "user" not in session:
        return redirect(url_for("login"))

    schedule = db.schedules.find_one({
        "_id": ObjectId(schedule_id)
    })

    movie = db.movies.find_one({
        "judul": schedule["judul"]
    })

    return render_template(
        "booking.html",
        movie=movie,
        schedule=schedule,
        username=session["user"]
    )

# ===========================
# LOGOUT
# ===========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ===========================
# RUN
# ===========================

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)