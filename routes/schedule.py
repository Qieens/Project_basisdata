from flask import Blueprint, request, redirect, url_for, session, jsonify
from bson.objectid import ObjectId
from database import db
from utils import admin_required, login_required

# 1. Deklarasi Blueprint
schedule_bp = Blueprint('schedule', __name__)

# ==========================================
# TAMBAH JADWAL (Hanya Admin)
# ==========================================
@schedule_bp.route("/admin/schedule/add", methods=["POST"])
@admin_required
def add_schedule():
    """
    Fungsi untuk menambahkan jadwal tayang baru ke database.
    Dilengkapi dengan validasi untuk mencegah jadwal bentrok.
    """
    judul = request.form.get("judul")
    studio = request.form.get("studio")
    jam = request.form.get("jam")
    
    # Mengambil harga dan memastikan tipenya adalah integer (angka)
    try:
        harga = int(request.form.get("harga") or 0)
    except ValueError:
        harga = 0

    # ---------------------------------------------------------
    # VALIDASI BACKEND: MENCEGAH JADWAL BENTROK
    # ---------------------------------------------------------
    # Sistem mencari apakah ada jadwal di studio dan jam yang sama
    jadwal_bentrok = db.schedules.find_one({
        "studio": studio,
        "jam": jam
    })

    if jadwal_bentrok:
        # Jika ditemukan jadwal yang sama, gagalkan proses simpan
        # dan beritahu Admin film apa yang sedang tayang di jam tersebut.
        return f"GAGAL: {studio} sudah digunakan untuk pemutaran film '{jadwal_bentrok['judul']}' pada jam {jam}. Silakan kembali dan pilih jam atau studio lain.", 400
    # ---------------------------------------------------------

    # Jika aman (tidak ada yang bentrok), simpan jadwal baru ke koleksi 'schedules'
    db.schedules.insert_one({
        "judul": judul,
        "studio": studio,
        "jam": jam,
        "harga": harga
    })

    # Setelah berhasil ditambah, kembalikan admin ke halaman dashboard
    return redirect(url_for("admin.admin_dashboard"))


# ==========================================
# HAPUS JADWAL (Hanya Admin)
# ==========================================
@schedule_bp.route("/admin/schedule/delete/<id>", methods=["POST"])
@admin_required
def delete_schedule(id):
    """
    Fungsi untuk menghapus jadwal tayang berdasarkan ID.
    """
    # Menghapus dari koleksi 'schedules'
    db.schedules.delete_one({"_id": ObjectId(id)})
    
    # Opsional: Jika Anda ingin menghapus semua tiket booking yang 
    # terkait dengan jadwal ini agar database tetap bersih (Cascade Delete)
    # db.bookings.delete_many({"schedule_id": str(id)})

    return redirect(url_for("admin.admin_dashboard"))


# ==========================================
# EDIT JADWAL (Hanya Admin)
# ==========================================
@schedule_bp.route("/admin/schedule/edit/<id>", methods=["POST"])
@admin_required
def edit_schedule(id):
    """
    Fungsi untuk mengedit jadwal tayang berdasarkan ID.
    Dilengkapi dengan validasi agar jadwal tidak bentrok.
    """
    judul = request.form.get("judul")
    studio = request.form.get("studio")
    jam = request.form.get("jam")
    
    try:
        harga = int(request.form.get("harga") or 0)
    except ValueError:
        harga = 0

    # Validasi bentrok (kecuali jadwal yang sedang diedit ini sendiri)
    jadwal_bentrok = db.schedules.find_one({
        "_id": {"$ne": ObjectId(id)},
        "studio": studio,
        "jam": jam
    })

    if jadwal_bentrok:
        return f"GAGAL: {studio} sudah digunakan untuk pemutaran film '{jadwal_bentrok['judul']}' pada jam {jam}. Silakan kembali dan pilih jam atau studio lain.", 400

    db.schedules.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "judul": judul,
            "studio": studio,
            "jam": jam,
            "harga": harga
        }}
    )

    return redirect(url_for("admin.admin_dashboard"))


# ==========================================
# API GET JADWAL 
# ==========================================
@schedule_bp.route("/api/schedules/<judul_film>")
@login_required
def get_schedules_by_movie(judul_film):
    """
    Rute tambahan jika Anda ingin mengambil jadwal menggunakan AJAX/Fetch API
    di tampilan Front-End tanpa perlu reload halaman.
    """
    schedules = list(db.schedules.find({"judul": judul_film}))
    
    # Karena ObjectId tidak bisa diubah otomatis ke JSON, kita ubah ke string
    for s in schedules:
        s["_id"] = str(s["_id"])
        
    return jsonify({
        "status": "success",
        "data": schedules
    })