from flask import render_template, redirect, url_for, request,flash
from admin import admin_bp
from admin.decorators import admin_required
from extensions import mysql
from MySQLdb.cursors import DictCursor



@admin_bp.route('/categories')
def manage_categories():
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
                SELECT id, name, status
                FROM category
                ORDER BY id DESC
                """)
    categories = cur.fetchall()
    cur.close()

    return render_template(
        'admin/category/manage.html',
        categories=categories
    )

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash("Category name is required", "danger")
            return redirect(url_for('admin_bp.add_category'))
        
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO category (name, status) VALUES (%s, 1)",
            (name,)
        )
        mysql.connection.commit()
        cur.close()

        flash("Category added successfully", "success")
        return redirect(url_for('admin_bp.manage_categories'))
    
    return render_template('admin/category/add.html')


@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    cur = mysql.connection.cursor(DictCursor)

    cur.execute("SELECT * FROM category WHERE id = %s", (id,))
    category = cur.fetchone()

    if not category:
        flash("Category not found", "danger")
        return redirect(url_for('admin.manage_categories'))

    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash("Category name is required", "danger")
            return redirect(url_for('admin.edit_category', id=id))

        cur.execute(
            "UPDATE category SET name = %s WHERE id = %s",
            (name, id)
        )
        mysql.connection.commit()
        cur.close()

        flash("Category updated successfully", "success")
        return redirect(url_for('admin.manage_categories'))

    cur.close()

    return render_template(
        'admin/category/add.html',  
        is_edit=True,
        category=category
    )


from flask import jsonify

@admin_bp.route('/categories/toggle-status', methods=['POST'])
def toggle_category_status():
    category_id = request.form.get('category_id')
    status = request.form.get('status')

    if not category_id:
        return jsonify({'success':False})
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE category SET status = %s WHERE id = %s",
                (status, category_id)
                )
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})



