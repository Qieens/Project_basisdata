from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from bson.objectid import ObjectId
from database import db
from utils import login_required
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking/<schedule_id>")
@login_required
def booking(schedule_id):
    schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        return redirect(url_for("dashboard.dashboard"))

    # --- PERBAIKAN LOGIKA WAKTU ---
    # Ubah string jam tayang menjadi objek waktu (time)
    jam_jadwal_obj = datetime.strptime(schedule["jam"], "%H:%M").time()
    waktu_sekarang_obj = datetime.now().time()

    # Bandingkan objek waktu
    if waktu_sekarang_obj > jam_jadwal_obj:
        return "Akses Ditolak: Jadwal sudah berakhir.", 403
    # ------------------------------

    movie = db.movies.find_one({"judul": schedule["judul"]})

    booked_seats = []
    for b in db.bookings.find({"schedule_id": str(schedule_id)}):
        booked_seats.extend(b.get("seats", []))

    return render_template(
        "booking.html",
        movie=movie,
        schedule=schedule,
        booked_seats=booked_seats,
        username=session["user"]
    )

@booking_bp.route("/booking/confirm/<schedule_id>", methods=["POST"])
@login_required
def booking_confirm(schedule_id):
    schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})

    waktu_sekarang = datetime.now().strftime("%H:%M")
    if schedule["jam"] < waktu_sekarang:
        return jsonify({"status": "error", "message": "Maaf, waktu pemesanan sudah habis."})

    if not schedule:
        return jsonify({"status": "error", "message": "Jadwal tidak ditemukan."})

    data = request.get_json(silent=True) or {}
    seats = data.get("seats", [])
    nama_pemesan = (data.get("nama_pemesan") or "").strip()
    metode_pembayaran = (data.get("metode_pembayaran") or "").strip()

    if not seats:
        return jsonify({"status": "error", "message": "Pilih minimal 1 kursi terlebih dahulu."})
    if not nama_pemesan:
        return jsonify({"status": "error", "message": "Nama pemesan wajib diisi."})
    if not metode_pembayaran:
        return jsonify({"status": "error", "message": "Pilih metode pembayaran terlebih dahulu."})

    already_booked = []
    for b in db.bookings.find({"schedule_id": str(schedule_id)}):
        already_booked.extend(b.get("seats", []))

    bentrok = [s for s in seats if s in already_booked]
    if bentrok:
        return jsonify({
            "status": "error",
            "message": f"Kursi {', '.join(bentrok)} sudah dipesan orang lain. Silakan pilih kursi lain."
        })

    movie = db.movies.find_one({"judul": schedule["judul"]})
    harga = schedule.get("harga", 0)
    total = harga * len(seats)

    db.bookings.insert_one({
        "user_id": session["user_id"],
        "schedule_id": str(schedule_id),
        "judul": schedule["judul"],
        "poster_url": movie["poster_url"] if movie else "",
        "studio": schedule.get("studio"),
        "jam": schedule.get("jam"),
        "seats": seats,
        "total": total,
        "nama_pemesan": nama_pemesan,
        "metode_pembayaran": metode_pembayaran,
        "status": "confirmed"
    })

    return jsonify({
        "status": "success",
        "message": "Booking berhasil!",
        "redirect_url": url_for("booking.history")
    })

@booking_bp.route("/history")
@login_required
def history():
    bookings = list(db.bookings.find({"user_id": session["user_id"]}).sort("_id", -1))
    return render_template(
        "history.html",
        bookings=bookings,
        username=session["user"],
        active_page="history"
    )