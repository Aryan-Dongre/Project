from flask import render_template
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor



@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    cur = mysql.connection.cursor(cursorclass=DictCursor)

    cur.execute("SELECT COUNT(*) AS total_bookings FROM booking")
    total_bookings = cur.fetchone()["total_bookings"]

    cur.execute("SELECT COUNT(*) AS pending_bookings FROM booking WHERE status='PENDING'")
    pending_bookings = cur.fetchone()["pending_bookings"]

    cur.execute("SELECT COUNT(*) AS total_services FROM service")
    total_services = cur.fetchone()["total_services"]

    cur.execute("SELECT COUNT(*) AS total_products FROM product")
    total_products = cur.fetchone()["total_products"]

    # Add fetch recent booking
    cur.execute("""
                SELECT 
                b.id,
                b.client_id,
                b.client_name,
                b.booking_date,
                b.booking_time,
                b.status,
                b.payment_status
                FROM booking b
                ORDER BY b.id DESC
                LIMIT 5
                """)
    recent_booking = cur.fetchall() 


    # payment 

    cur.execute("""
               SELECT COALESCE(SUM(total_amount), 0) AS today_revenue
                FROM booking
                WHERE payment_status = 'PAID'
                AND booking_date = CURDATE()
                """)
    today_revenue = cur.fetchone()["today_revenue"]
  


    cur.close()

    

    return render_template(
        "admin/dashboard.html",
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        total_services=total_services,
        total_products=total_products,
        recent_booking=recent_booking,
        today_revenue=today_revenue
    )