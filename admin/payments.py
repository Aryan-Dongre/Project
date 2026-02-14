from flask import render_template, redirect, url_for, request,flash
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor

@admin_bp.route("/payments")
@admin_required
def payments():

    cur = mysql.connection.cursor(DictCursor)

    # total revenue
    cur.execute ("""
                SELECT IFNULL(SUM(amount),0) AS total_revenue
                 FROM payment
                 WHERE payment_status ='SUCCESS'
                 """)
    total_revenue = cur.fetchone()["total_revenue"]

    # Today Revenue

    cur.execute("""
                SELECT IFNULL(SUM(AMOUNT),0) AS today_revenue
                FROM payment
                WHERE payment_status = 'SUCCESS'
                AND DATE(payment_time)=CURDATE()
                """)
    today_revenue = cur.fetchone()["today_revenue"]
    

     # month Revenue

    cur.execute("""
                SELECT IFNULL(SUM(AMOUNT),0) AS month_revenue
                FROM payment
                WHERE payment_status = 'SUCCESS'
                AND MONTH(payment_time)=MONTH(CURDATE())
                AND YEAR(payment_time)=YEAR(CURDATE())
                """)
    month_revenue = cur.fetchone()["month_revenue"]

    cur.execute("""
                SELECT COUNT(*) AS total_transactions
                FROM payment
                WHERE payment_status='SUCCESS'
                """)
    total_transactions = cur.fetchone()["total_transactions"]

    # recent 10 payment

    cur.execute("""
                    SELECT id, booking_id, amount, payment_method, payment_status, payment_time
                    FROM payment
                    ORDER BY payment_time DESC
                    LIMIT 10
                """)
    
    recent_payments = cur.fetchall()

    cur.close()


    return render_template(
        "payment/payments.html",
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        month_revenue=month_revenue,
        total_transactions=total_transactions,
        recent_payments=recent_payments
        )

# Analytics Part
from flask import jsonify

@admin_bp.route("/payments/analytics-data")
@admin_required
def payments_analytics_data():
    year = int(request.args.get("year"))

    cur = mysql.connection.cursor(DictCursor)

    # Monthly Revenue
    cur.execute("""
        SELECT 
            MONTH(payment_time) AS month,
            SUM(amount) AS total
        FROM payment
        WHERE payment_status = 'SUCCESS'
        AND YEAR(payment_time) = %s
        GROUP BY MONTH(payment_time)
        ORDER BY MONTH(payment_time)
    """, (year,))
    
    monthly_raw = cur.fetchall()
    monthly_data = {row["month"]: float(row["total"]) for row in monthly_raw}

    # Service Type Revenue
    cur.execute("""
        SELECT
            st.name AS service_type,
            SUM(s.charges) AS total_revenue
        FROM payment p
        JOIN booking b ON p.booking_id = b.id
        JOIN booking_service bs ON b.id = bs.booking_id
        JOIN service s ON bs.service_id = s.id
        JOIN service_type st ON s.service_type_id = st.id
        WHERE p.payment_status = 'SUCCESS'
        AND YEAR(p.payment_time) = %s
        GROUP BY st.name
    """, (year,))
    
    service_raw = cur.fetchall()
    service_data = {row["service_type"]: float(row["total_revenue"]) for row in service_raw}

    cur.close()

    return jsonify({
        "monthly": monthly_data,
        "service_type": service_data
    })

# Transaction Part
@admin_bp.route("/payments/client-transactions")
@admin_required

def client_transactions():

    page =int(request.args.get("page", 1))
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    per_page = 10
    offset = (page -1) * per_page

    cur = mysql.connection.cursor(DictCursor)

    base_query = """
                FROM payment p
                INNER JOIN booking b ON p.booking_id
                INNER JOIN appointment a ON a.booking_id = b.id
                WHERE 1=1
                """
    
    filters = []
    values = []

    if search:
        filters.append("AND b.client_name LIKE %s")
        values.append(f"%{search}%")
  

    if status:
        filters.append("AND p.payment_status = %s")
        values.append(status)

    filter_query = " ".join(filters)    

    # get total count

    count_query = ("SELECT COUNT(*) AS total " + base_query + " " + filter_query)
    cur.execute(count_query, values)
    total = cur.fetchone()["total"]

    total_pages = (total + per_page -1) // per_page

    # pagination
    data_query = """ 
            SELECT
            b.client_name,
            a.appointment_time,
            a.appointment_date,
            a.status AS appointment_status,
            p.payment_status,
            p.amount
         """ + base_query + " " + filter_query + """
            ORDER BY p.payment_time DESC
            LIMIT %s OFFSET %s
            """        
    cur.execute(data_query, values + [per_page, offset])
    transactions = cur.fetchall()
    cur.close()

    # Convert time and date
    for row in transactions:
        if row["appointment_date"]:
            row["appointment_date"] = row["appointment_date"].strftime("%Y-%m-%d")

        if row["appointment_time"] :
            row["appointment_time"] = str(row["appointment_time"])   

    return jsonify({
        "data": transactions,
        "total": total,
        "page":page,
        "pages": total_pages,
        "total":total
    
    })