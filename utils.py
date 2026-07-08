from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    """Menolak akses jika user belum login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Menolak akses jika user bukan admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            return redirect(url_for("dashboard.dashboard"))
        return f(*args, **kwargs)
    return decorated