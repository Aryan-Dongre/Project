from flask import render_template, redirect, url_for, request,flash
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor


@admin_bp.route("/products")
@admin_required
def products():

    cur = mysql.connection.cursor(DictCursor)

    # Fetch all products
    cur.execute("SELECT * FROM product ORDER BY id DESC")
    products = cur.fetchall()

    # Total Products
    cur.execute("SELECT COUNT(*) AS total FROM product")
    total_products = cur.fetchone()['total']

    # Active Products
    cur.execute("SELECT COUNT(*) AS active FROM product WHERE status = 'ACTIVE'")
    active_products = cur.fetchone()['active']

    # Inactive Products
    cur.execute("SELECT COUNT(*) AS inactive FROM product WHERE status = 'INACTIVE'")
    inactive_products = cur.fetchone()['inactive']

    cur.close()

    return render_template(
        'admin/products/list.html',
        products=products,
        total_products=total_products,
        active_products=active_products,
        inactive_products=inactive_products
    )

import os
from werkzeug.utils import secure_filename

@admin_bp.route("/product/form", methods=["GET", "POST"])
@admin_required
def product_form():

    cur = mysql.connection.cursor(DictCursor)
    product_id = request.args.get("id")
    product = None

    # If editing → fetch product
    if product_id:
        cur.execute("SELECT * FROM product WHERE id=%s", (product_id,))
        product = cur.fetchone()

    if request.method == "POST":

        name = request.form.get("name")
        brand_name = request.form.get("brand_name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")  # ✅ FIXED
        description = request.form.get("description")
        status = request.form.get("status")

        image_file = request.files.get("image")

        # ---------------- ADD MODE ----------------
        if not product_id:

            if not image_file or image_file.filename == "":
                flash("Image is Required!", "danger")
                return redirect(request.url)

            filename = secure_filename(image_file.filename)
            image_path = os.path.join("static/uploads/products", filename)
            image_file.save(image_path)

            cur.execute("""
                INSERT INTO product
                (name, brand_name, price, quantity, description, image, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, brand_name, price, quantity, description, filename, status))

            mysql.connection.commit()
            flash("Product added successfully!", "success")

        # ---------------- UPDATE MODE ----------------
        else:

            if image_file and image_file.filename != "":
                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads/products", filename)
                image_file.save(image_path)
            else:
                filename = product["image"]

            cur.execute("""
                UPDATE product SET
                name=%s,
                brand_name=%s,
                price=%s,
                quantity=%s,
                description=%s,
                image=%s,
                status=%s
                WHERE id=%s
            """, (name, brand_name, price, quantity, description, filename, status, product_id))

            mysql.connection.commit()
            flash("Product updated successfully!", "success")

        cur.close()
        return redirect(url_for("admin.products"))

    cur.close()
    return render_template("admin/products/form.html", product=product)


@admin_bp.route("/product/toggle/<int:id>")
@admin_required
def toggle_product(id):

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("SELECT status FROM product WHERE id=%s", (id,))
    product = cur.fetchone()

    if product["status"] == "ACTIVE":
        new_status = "INACTIVE"
    else:
        new_status = "ACTIVE"

    cur.execute("UPDATE product SET status=%s WHERE id=%s", (new_status, id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("admin.products"))

@admin_bp.route("/product/delete/<int:id>")
@admin_required
def delete_product(id):

    cur = mysql.connection.cursor()
    cur.execute("UPDATE product SET status='INACTIVE' WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Product moved to inactive!", "warning")
    return redirect(url_for("admin.products"))
