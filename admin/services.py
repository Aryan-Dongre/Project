from flask import render_template, redirect, url_for, request,flash
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor



# ENTRY POINT (REDIRECT ONLY)

@admin_bp.route("/services")
@admin_required
def services():
    return redirect(url_for("admin.manage_services"))


# MANAGE SERVICES (REAL PAGE)

@admin_bp.route("/services/manage")
@admin_required
def manage_services():
    cur = mysql.connection.cursor(DictCursor)

    # for filter part
    search = request.args.get("search")
    category_id = request.args.get("category_id")
    service_type_id = request.args.get("service_type_id")
    status = request.args.get("status")
    
    
    query ="""
        SELECT
            s.id,
            s.name,
            s.charges,
            s.duration,
            s.category_id,
            s.service_type_id,
            s.status,
            c.name AS category_name    
            FROM service s
            LEFT JOIN category c ON c.id = s.category_id
            WHERE 1=1
               
    """
                
    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"{search}%")

    if category_id:
        query += " AND s.category_id = %s"
        params.append(category_id)

    if service_type_id:
        query += " AND s.service_type_id = %s"
        params.append(service_type_id)

    if status != None and status != "":
        query += " AND s.status = %s"
        params.append(status)

    query += " ORDER BY s.id DESC"

    cur.execute(query, params)
    services = cur.fetchall()

    cur.execute("SELECT id, name FROM category")
    categories = cur.fetchall()

    cur.close()

    SERVICE_TYPE_MAP = {
        1:"NORMAL",
        2:"GROOM",
        3:"BRIDAL"
    }

    return render_template(
        "service/manage.html",
        services=services,
        categories=categories,
        service_type_map=SERVICE_TYPE_MAP
    )

# =========================
# ADD PAGE
# =========================

@admin_bp.route("/services/add", methods=["GET", "POST"])
@admin_required
def add_service():

    cur = mysql.connection.cursor(DictCursor)

    # FETCH DROPDOWN DATA
    cur.execute("SELECT id, name FROM category")
    categories = cur.fetchall()

    cur.execute("SELECT id, name FROM service_type")
    service_types = cur.fetchall()

    if request.method == "POST":
        name = request.form.get("name")
        charges = request.form.get("charges")
        duration = request.form.get("duration")
        category_id = request.form.get("category_id")
        service_type_id = request.form.get("service_type_id")
        gender_id = request.form.get("gender_id")
        
        # VALIDATION INSIDE POST
        if not name or not charges or not duration or not category_id or not service_type_id:
            flash("All fileds are required", "danger")
            return redirect(request.url)
        # Enforce gender rule 

        cur.execute(
        "SELECT name FROM service_type WHERE id = %s",
        (service_type_id,)
    )
        service_type = cur.fetchone()

        if service_type and service_type["name"].lower() != "normal":
         gender_id = None
  

        # INSERT INTO DB
        cur.execute("""
            INSERT INTO service (name, charges, duration, category_id, service_type_id, gender_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, charges, duration, category_id, service_type_id, gender_id))

        mysql.connection.commit()
        cur.close()

        flash("Service added successfully", "success")
        return redirect(url_for("admin.manage_services"))

    cur.close()
    return render_template(
        "service/add.html",
        categories=categories,
        service_types=service_types
    )  

@admin_bp.route("/services/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_service(id):
    cur = mysql.connection.cursor(DictCursor)

    # =========================
    # FETCH EXISTING SERVICE
    # =========================
    cur.execute("SELECT * FROM service WHERE id = %s", (id,))
    service = cur.fetchone()

    if not service:
        cur.close()
        flash("Service not found", "danger")
        return redirect(url_for("admin.manage_services"))

    # =========================
    # FETCH DROPDOWNS
    # =========================
    cur.execute("SELECT id, name FROM category")
    categories = cur.fetchall()

    cur.execute("SELECT id, name FROM service_type")
    service_types = cur.fetchall()

    # =========================
    # HANDLE UPDATE
    # =========================
    if request.method == "POST":
        name = request.form.get("name")
        charges = request.form.get("charges")
        duration = request.form.get("duration")
        category_id = request.form.get("category_id")
        service_type_id = request.form.get("service_type_id")
        gender_id = request.form.get("gender_id")

        # -------------------------
        # BASIC VALIDATION
        # -------------------------
        if not name or not charges or not duration:
            cur.close()
            flash("All fields are required", "danger")
            return redirect(request.url)

        # -------------------------
        # ENFORCE GENDER RULE
        # -------------------------
        cur.execute(
            "SELECT name FROM service_type WHERE id = %s",
            (service_type_id,)
        )
        service_type = cur.fetchone()

        if service_type and service_type["name"].lower() != "normal":
            gender_id = None

        # -------------------------
        # UPDATE DB
        # -------------------------
        cur.execute("""
            UPDATE service
            SET name=%s,
                charges=%s,
                duration=%s,
                category_id=%s,
                service_type_id=%s,
                gender_id=%s
            WHERE id=%s
        """, (
            name,
            charges,
            duration,
            category_id,
            service_type_id,
            gender_id,
            id
        ))

        mysql.connection.commit()
        cur.close()

        flash("Service updated successfully", "success")
        return redirect(url_for("admin.manage_services"))

    # =========================
    # RENDER EDIT FORM
    # =========================
    cur.close()
    return render_template(
        "service/add.html",
        service=service,
        categories=categories,
        service_types=service_types,
        is_edit=True
    )



@admin_bp.route("/services/delete/<int:id>", methods=["POST"])
@admin_required

def delete_service(id):
     cur = mysql.connection.cursor(DictCursor)
     cur.execute("DELETE FROM service WHERE id =%s", (id,))
     mysql.connection.commit()
     cur.close()

     flash("Service deleted successfully", "success")
     return redirect(url_for("admin.manage_services")) 

#================ TOGGEL================ 

from flask import request, jsonify

@admin_bp.route('/services/toggle-status', methods=['POST'])
def toggle_service_status():

   
    service_id = request.form.get('service_id')
    new_status = request.form.get('status')

    if not service_id:
        return jsonify({'success': False})

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE service SET status = %s WHERE id = %s",
        (new_status, service_id)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})



    