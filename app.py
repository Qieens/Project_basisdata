from flask import Flask
from config import Config
from database import db

# 1. Impor semua blueprint dari folder routes
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.movies import movies_bp
from routes.booking import booking_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.schedule import schedule_bp

# 2. Inisialisasi Aplikasi
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# ===========================
# TEMPLATE FILTER
# ===========================
@app.template_filter('rupiah')
def rupiah_filter(number):
    try:
        return "{:,.0f}".format(int(number)).replace(',', '.')
    except (ValueError, TypeError):
        return number

# ===========================
# HOME ROUTE (Opsional: Jika ada halaman landing page di luar sistem login)
# ===========================
@app.route("/")
def home():
    # Jika tidak ada landing page khusus, bisa langsung dialihkan ke login
    from flask import redirect, url_for
    return redirect(url_for('auth.login'))

# 3. Daftarkan (Register) Blueprint ke aplikasi utama
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(movies_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(schedule_bp)

# 4. Jalankan Aplikasi
if __name__ == "__main__":
    app.run(debug=True)