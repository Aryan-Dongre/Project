from flask import render_template, redirect, url_for, request,flash
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor

@admin_bp.route('/booking')
@admin_required 

def bookings () :
    return redirect(url_for("admin.manage_booking"))

@admin_bp.route("/booking/manage")
@admin_required
def manage_booking():

    status_filter = request.args.get("status")
    search_query = request.args.get("search", "").strip()

    # pagination Part
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1)*per_page

    cur = mysql.connection.cursor(DictCursor)
    
    # main query
    query = """
        SELECT
            b.id,
            b.booking_date,
            b.booking_time,
            b.status,
            b.payment_status,
            b.total_amount,
            b.client_name,
            b.client_email,
            COUNT(bs.service_id) AS total_services
        FROM booking b
        LEFT JOIN booking_service bs ON b.id = bs.booking_id
    """
    params = []
    conditions = []

    # searching part
    if search_query:
        conditions.append("""
                            (
                          b.client_name LIKE %s OR
                          b.client_email LIKE %s OR
                          b.booking_date LIKE %s OR
                          b.booking_time LIKE %s
                          )
                          """)
        like_pattern = f"%{search_query}%"
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern])
    
    # status filter
    if status_filter:
        conditions.append("b.status = %s")
        params.append(status_filter)

        # combine conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)    

    query += """
        GROUP BY b.id
        ORDER BY b.booking_date DESC, b.booking_time DESC
        LIMIT %s OFFSET %s
    """

    params.extend([per_page, offset])

    cur.execute(query, params)
    bookings = cur.fetchall()

    # Pagination Count Query
    count_query = """
                  SELECT COUNT(DISTINCT b.id) AS total
                  FROM booking b
                  LEFT JOIN booking_service bs ON b.id = bs.booking_id
                  """
    
    count_params = []

    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
        count_params = params[:-2] 

    cur.execute(count_query, count_params)
    total_rows = cur.fetchone()["total"]

    total_pages = (total_rows + per_page -1) // per_page
    
    #==Summary card==#

    # ===== Summary Cards =====

    cur.execute("SELECT COUNT(*) AS total FROM booking")
    row = cur.fetchone()
    total_bookings = row["total"] if row["total"] is not None else 0

    cur.execute("SELECT COUNT(*) AS paid FROM booking WHERE payment_status='PAID'")
    row = cur.fetchone()
    paid_bookings = row["paid"] if row["paid"] is not None else 0

    cur.execute("SELECT COUNT(*) AS pending FROM booking WHERE payment_status='PENDING'")
    row = cur.fetchone()
    pending_bookings = row["pending"] if row["pending"] is not None else 0

    cur.execute("SELECT SUM(total_amount) AS revenue FROM booking WHERE payment_status='PAID'")
    row = cur.fetchone()
    revenue = row["revenue"] if row["revenue"] is not None else 0

    cur.close()

    return render_template(
        "admin/booking/manage.html",
        bookings=bookings,
        status_filter=status_filter,
        total_bookings=total_bookings,
        paid_booking=paid_bookings,
        pending_booking=pending_bookings,
        revenue=revenue,
        search_query=search_query,
        page=page,
        total_pages=total_pages
    )

@admin_bp.route("/booking/cancel/<int:id>")
@admin_required
def cancel_booking(id):

    cur = mysql.connection.cursor(DictCursor)
    cur.execute(
        "UPDATE booking SET status='CANCELLED' WHERE id=%s",
        (id,)
    )
    mysql.connection.commit()
    cur.close()

    flash("Booking cancelled successfully.", "success")

    return redirect(url_for("admin.manage_booking"))

@admin_bp.route("/booking/view/<int:id>", methods=["GET", "POST"])
def view_booking(id):

    cur = mysql.connection.cursor(DictCursor)

    # If admin submit status update
    if request.method =="POST":
        new_status = request.form.get("status")

        cur.execute("""
                    UPDATE booking
                    SET status = %s
                    WHERE id =%s
                    """, (new_status, id))
        mysql.connection.commit()
        flash("Booking Status update Successfully", "success")

    # get booking info
    cur.execute("""
                SELECT *
                FROM booking
                WHERE id = %s
                """, (id,))
    
    booking= cur.fetchone()

    if not booking:
        flash("Booking not found", "danger")
        return redirect(url_for("admin.manage_booking"))
    
    # get service details
    cur.execute("""
                SELECT s.name, s.charges
                FROM booking_service bs
                JOIN service s ON bs.service_id = s.id
                WHERE bs.booking_id = %s 
                """, (id,))
    
    services = cur.fetchall()

    cur.close()
    
    return render_template(
        "admin/booking/view.html",
        booking=booking,
        services=services
    )
