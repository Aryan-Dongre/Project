from flask import render_template
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor


@admin_bp.route("/appointments")
@admin_required
def appointments():
    return render_template("admin/appointments.html")


from flask import jsonify, request
from datetime import datetime


@admin_bp.route("/api/appointments-by-date")
@admin_required
def get_appointments_by_date():

    date_str = request.args.get("date")
    search = request.args.get("search")
    status = request.args.get("status")

    cur = mysql.connection.cursor(DictCursor)

    query = """
        SELECT
            a.id,
            a.appointment_date,
            a.appointment_time,
            LOWER(a.status) AS status,
            b.client_name,
            GROUP_CONCAT(s.name SEPARATOR ', ') AS services
        FROM appointment a
        JOIN booking b ON a.booking_id = b.id
        JOIN booking_service bs ON b.id = bs.booking_id
        JOIN service s ON bs.service_id = s.id
        WHERE a.appointment_date = %s
    """

    params = [date_str]

    # ✅ Status filter
    if status:
        query += " AND a.status = %s"
        params.append(status)

    # ✅ Client name search
    if search:
        query += " AND b.client_name LIKE %s"
        params.append(f"%{search}%")

    query += """
        GROUP BY a.id
        ORDER BY a.appointment_time
    """

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "client_name": r["client_name"],
            "service_name": r["services"],
            "appointment_date": r["appointment_date"].strftime("%Y-%m-%d"),
            "appointment_time": str(r["appointment_time"]),
            "status": r["status"]  # already lowercase
        })

    return jsonify(result)

from MySQLdb.cursors import DictCursor

@admin_bp.route("/api/appointment-status-summary")
@admin_required
def appointment_status_summary():
    month = request.args.get("month")  # YYYY-MM

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT 
            DATE(appointment_date) AS date,
            LOWER(status) AS status,
            COUNT(*) AS count
        FROM appointment
        WHERE DATE_FORMAT(appointment_date, '%%Y-%%m') = %s
        GROUP BY DATE(appointment_date), LOWER(status)
    """, (month,))

    rows = cur.fetchall()

    summary = {}

    for row in rows:
        date_str = row["date"].strftime("%Y-%m-%d")

        if date_str not in summary:
            summary[date_str] = {
                "pending": 0,
                "confirmed": 0,
                "completed": 0
            }

        # Safe assignment (CANCELLED ignored for now)
        if row["status"] in summary[date_str]:
            summary[date_str][row["status"]] = row["count"]

    return jsonify(summary)


from MySQLdb.cursors import DictCursor

@admin_bp.route("/api/appointment-summary-counts")
@admin_required
def appointment_summary_counts():
    cur = mysql.connection.cursor(DictCursor)

    # Today
    cur.execute("""
        SELECT COUNT(*) AS total FROM appointment
        WHERE appointment_date = CURDATE()
    """)
    today_count = cur.fetchone()["total"]

    # This week (Mon–Sun)
    cur.execute("""
        SELECT COUNT(*) AS total FROM appointment
        WHERE YEARWEEK(appointment_date, 1) = YEARWEEK(CURDATE(), 1)
    """)
    week_count = cur.fetchone()["total"]

    # This month
    cur.execute("""
        SELECT COUNT(*) AS total FROM appointment
        WHERE DATE_FORMAT(appointment_date, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m')
    """)
    month_count = cur.fetchone()["total"]

    return jsonify({
        "today": today_count,
        "week": week_count,
        "month": month_count
    })



from flask import request, jsonify
from extensions import mysql

@admin_bp.route("/api/appointment-search-dates")
@admin_required
def search_appointment_dates():
    q = request.args.get("q", "").strip().lower()

    if not q:
        return jsonify([])

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT a.appointment_date
        FROM appointment a
        JOIN booking b ON b.id = a.booking_id
        WHERE LOWER(b.client_name) LIKE %s
    """, (f"%{q}%",))

    rows = cur.fetchall()
    cur.close()

    return jsonify([
        row["appointment_date"].strftime("%Y-%m-%d")
        for row in rows
    ])


