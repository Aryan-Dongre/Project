from flask import render_template, jsonify
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor

# ===============================
# Analytics Page
# ===============================
@admin_bp.route('/services/analytics')
@admin_required
def services_analytics():
    return render_template('admin/service/analytics.html')


# ===============================
# Service Type Distribution API
# ===============================
@admin_bp.route('/services/analytics/service-type')
@admin_required
def service_type_distribution():
    cur = mysql.connection.cursor(DictCursor)

    query = """
        SELECT st.name AS service_type, COUNT(s.id) AS total
        FROM service s
        JOIN service_type st ON s.service_type_id = st.id
        WHERE s.status = 1
        GROUP BY st.name
    """

    cur.execute(query)
    result = cur.fetchall()

    data = {row['service_type']: row['total'] for row in result}

    return jsonify(data)

@admin_bp.route('/services/analytics/status')
@admin_required
def service_status_distribution():
    cur = mysql.connection.cursor(DictCursor) 

    query = """
        SELECT 
            IF(`status` = 1, 'Active', 'Inactive') AS label,
            COUNT(*) AS total
        FROM service
        GROUP BY `status`
    """

    cur.execute(query)
    result = cur.fetchall()

    data = {row['label']: row['total'] for row in result}

    return jsonify(data)



@admin_bp.route('/services/analytics/most-booked')
@admin_required

def most_booked_services():
    cur = mysql.connection.cursor(DictCursor)

    query = """ 
          SELECT 
          s.name AS service_name,
          COUNT(bs.service_id) AS booking_count
          FROM booking_service bs
          JOIN service s ON bs.service_id = s.id
          GROUP BY bs.service_id
          ORDER BY booking_count DESC
          LIMIT 8
          """
    
    cur.execute(query)
    result = cur.fetchall()

    data = {
        "labels": [row['service_name'] for row in result],
        "values": [row['booking_count'] for row in result]
    }
    
    return jsonify(data)
