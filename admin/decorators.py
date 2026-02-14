from functools import wraps
from flask import session, redirect, url_for, flash


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first", "error")
            return redirect(url_for("login"))

        if session.get("role", "").upper() != "ADMIN":
            flash("Access denied. Admins only.", "error")
            return redirect(url_for("home"))

        return route_function(*args, **kwargs)

    return wrapper

