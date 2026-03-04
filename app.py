from flask import Flask, render_template, request , flash , url_for , session , redirect
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash , check_password_hash
from functools import wraps
from flask import jsonify
from MySQLdb.cursors import DictCursor
from admin import admin_bp
from extensions import mysql
from flask import make_response
from config import Config
from extensions import mail
from flask_mail import Mail, Message
import os
from services.email_service import EmailService
import uuid
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv


# Time formate function

def format_duration(duration):
    """
    Converts duration into 'X min' format
    Supports:
    - int (minutes)
    - datetime.timedelta
    - datetime.time
    """
    if duration is None:
        return None

    # CASE 1: duration is already INT (minutes)
    if isinstance(duration, int):
        return f"{duration} min"

    # CASE 2: MySQL returns datetime.timedelta
    if hasattr(duration, "seconds"):
        total_minutes = duration.seconds // 60
        return f"{total_minutes} min"

    # CASE 3: MySQL returns datetime.time
    if hasattr(duration, "hour"):
        total_minutes = duration.hour * 60 + duration.minute
        return f"{total_minutes} min"

    return None

#==================================================================#

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# MySQL Configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='Aryan@08'
app.config['MYSQL_DB'] = 'Beauty_Parlor'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Email Service Setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mysql =MySQL(app)
mail.init_app(app)

app.register_blueprint(admin_bp)


#Must Imp part for any website
def login_required(route_function):
        @wraps(route_function)
        def wrapper(*args , **kwargs):
            if 'user_id' not in session:
                flash("Please login first", 'error')
                return redirect(url_for('login'))
            
            return route_function(*args ,**kwargs)
        return wrapper

@app.after_request
def add_header(response):
    if session.get("user_id"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-Cache"
        response.headers["Expires"] = "0"
    return response

#=============Home==============#
@app.route('/')
def home():

    if session.pop("appointment_popup", None):
        flash(" 🎉 Your appointment is confirmed!", "success")
    return render_template('user/home.html')

#============Home over============#

#=========== Registration and Login==============#

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute("SELECT id FROM registration WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already registered", "error")
            cur.close()
            return redirect(url_for('register'))

        # Hash password
        password = generate_password_hash(password)

        # Insert into registration
        cur.execute("""
            INSERT INTO registration (full_name, email, password)
            VALUES (%s, %s, %s)
        """, (full_name, email, password))

        registration_id = cur.lastrowid

        # Insert into client table
        cur.execute("""
            INSERT INTO client (client_name, registration_id)
            VALUES (%s, %s)
        """, (full_name, registration_id))

        mysql.connection.commit()
        cur.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('user/register.html')

 
@app.route('/login' , methods=["GET","POST"])
def login():

    if request.method =='POST':
        email =request.form['email']
        password =request.form['password']

        cur=mysql.connection.cursor(DictCursor)

         # Fetch user by email
        cur.execute("""SELECT id, password, role FROM registration
                    WHERE email=%s""",
                    (email,))
        user = cur.fetchone()

         #  Validate credentials

        if not user or not check_password_hash(user['password'],password):
            flash("Invalid Email Or Password" , "error")
            cur.close()
            return redirect(url_for('login'))
        
        # create Session 
        session['user_id'] =user['id']
        session['role'] = user['role']

        cur.close()
        flash("Login Successful","success")

        if user['role'] =="ADMIN":
            return redirect(url_for("admin.dashboard"))
        
        return redirect(url_for('home'))
    
    return render_template('user/login.html')
#=========== Registration and Login over============#

#========Forgot Password Part========#

import secrets
import hashlib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from utils.password_token import generate_password_reset_token


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        cur = mysql.connection.cursor(DictCursor)
        user =None

        try :
            cur.execute("SELECT id FROM registration WHERE email = %s", (email,))
            user = cur.fetchone()

            if user:
                #Invalidate old tokens
                cur.execute("""
                            DELETE FROM password_reset_tokens
                            WHERE user_id = %s
                            """, (user["id"],))
                
                # use helper
                signed_token, hashed_token = generate_password_reset_token()

                expiry = datetime.utcnow() + timedelta(minutes=10)

                cur.execute("""
                            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
                            VALUES (%s, %s, %s)
                            """, (user["id"], hashed_token, expiry))
                
                mysql.connection.commit()

        except Exception as e :
                mysql.connection.rollback()
                print("==== FORGOT PASSWORD ERROR START ====")
                print(e)
                print("==== FORGOT PASSWORD ERROR END ====")
                flash("Something went wrong. Please try again.", "danger")
                return redirect(url_for("forgot_password"))
        
        finally:
                cur.close()

        # send email 

        if user:
                try:
                    send_reset_password(email, signed_token)
                    print("Reset Email Sent")
                except Exception as e:
                       print("Email failed but token stored:", e) 

        flash("If the email exists, a reset link has been sent.", "info")
        return redirect(url_for("login"))    

    return render_template("user/forgot_password.html")                   
                
def send_reset_password(user_email, signed_token):

    print("RESET EMAIL FUNCTION CALLED")

    reset_link = url_for(
        "reset_password",
        token=signed_token,
        _external = True
    )

    EmailService.send_email(
        subject="Password Reset - Beauty Parlor",
        recipients=[user_email],
        template_name="reset_password.html",
        reset_link=reset_link
    )

from utils.password_token import verify_signed_token, hash_token

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    # verify signature
    raw_token = verify_signed_token(token)

    if not raw_token:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("login"))
    
    # hash raw token 
    hashed_token_value = hash_token(raw_token)    

    # hashed_token = hashlib.sha256(token.encode()).hexdigest()
    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT * FROM password_reset_tokens
        WHERE token_hash=%s 
        AND expires_at > UTC_TIMESTAMP()
    """, (hashed_token_value,))
    
    token_data = cur.fetchone()

    if not token_data:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("password")

        hashed_password = generate_password_hash(new_password)

        cur.execute("""
            UPDATE registration
            SET password=%s
            WHERE id=%s
        """, (hashed_password, token_data["user_id"]))
         
        # Delete instead of mark used  
        cur.execute("""
            DELETE FROM  password_reset_tokens
            WHERE id=%s
        """, (token_data["id"],))

        mysql.connection.commit()
        cur.close()

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("user/reset_password.html")



#=========== Logout==============#
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
#=========== Logout over============#

#=========================Service part===============================#
@app.route("/services")
def services():
    gender = request.args.get("gender")        # MEN / WOMEN
    service_type = request.args.get("type")    # NORMAL / GROOM / BRIDAL

    cur = mysql.connection.cursor(DictCursor)

    
    # Get IDs from master tables
   
    cur.execute("SELECT id, name FROM gender")
    gender_map = {row["name"].upper(): row["id"] for row in cur.fetchall()}

    cur.execute("SELECT id, name FROM service_type")
    service_type_map = {row["name"].upper(): row["id"] for row in cur.fetchall()}

   
    # Fetch ALL categories
   
    cur.execute("SELECT id, name FROM category")
    categories = cur.fetchall()

    services = {}

  
    # GROOM / BRIDAL
   
    if service_type in ("GROOM", "BRIDAL"):
        st_id = service_type_map.get(service_type)

        for cat in categories:
            cur.execute("""
                SELECT s.id, s.name, s.charges, s.duration
                FROM service s
                JOIN category c ON s.category_id = c.id        
                WHERE s.category_id = %s
                  AND s.service_type_id = %s
                  AND s.status = 1
                  AND c.status = 1            
            """, (cat["id"], st_id))

            rows = cur.fetchall()
            for row in rows:
                row["duration"] = format_duration(row["duration"])

            services[cat["id"]] = rows

   
      # NORMAL (MEN / WOMEN)
   
    elif service_type == "NORMAL" and gender in ("MEN", "WOMEN"):
        st_id = service_type_map.get("NORMAL")
        g_id = gender_map.get(gender)

        for cat in categories:
            cur.execute("""
                SELECT s.id, s.name, s.charges, s.duration
                FROM service s
                JOIN category c ON s.category_id = c.id
                WHERE s.category_id = %s
                  AND s.service_type_id = %s
                   AND s.gender_id  = %s
                    AND s.status = 1
                  AND c.status = 1
            """, (cat["id"], st_id, g_id))

            rows = cur.fetchall()
            for row in rows:
                row["duration"] = format_duration(row["duration"])

            services[cat["id"]] = rows

    # =============================
    # Default empty state
    # =============================
    else:
        services = {}

    cur.close()

    return render_template(
        "user/services.html",
        categories=categories,
        services=services,
        gender=gender,
        service_type=service_type
    )


      #---Service part over---#
      
      #--- Selected Service start---#

@app.route("/set_selected_services", methods=["POST"])
@login_required
def set_selected_services():
    data = request.get_json()

    new_services = data.get("services", [])

    # IMPORTANT: convert to string (session stores strings)
    new_services = [str(s) for s in new_services]

    if not new_services:
        return{"status": "ok"}
    
    cur = mysql.connection.cursor(DictCursor)
    # valid only active status services
    format_strings =" ,".join(["%s"] * len(new_services))
    cur.execute(f"""
                SELECT id
                FROM service
                WHERE id IN ({format_strings})
                AND status = 1 
                """, tuple(new_services))
    
    valid_services = [str(row["id"]) for row in cur.fetchall()]
    cur.close()

    existing_services = session.get("selected_services", [])
    # merge old + new
    session["selected_services"] = list(set(existing_services + new_services))

    session.modified = True  # VERY IMPORTANT

    return {"status": "ok"}


 #=================== Selected Service over=======#

#==============Appointment part========================#

@app.route('/appointment', methods=["GET"])
@login_required
def appointment():

    user_id = session["user_id"]
    cur = mysql.connection.cursor(DictCursor)

    # Logged-in user
    cur.execute("""
        SELECT full_name, email
        FROM registration
        WHERE id = %s
    """, (user_id,))
    user = cur.fetchone()

    # Services from SESSION 
    selected_service_ids = session.get("selected_services", [])
    service_list = []
    total_amount = 0

    if selected_service_ids:
        placeholders = ",".join(["%s"] * len(selected_service_ids))
        cur.execute(f"""
            SELECT id, name, charges
            FROM service
            WHERE id IN ({placeholders})
        """, tuple(selected_service_ids))
        service_list = cur.fetchall()
        total_amount = sum(s["charges"] for s in service_list)

    cur.close()

    from datetime import date
    return render_template(
        "user/appointment.html",
        today=date.today().isoformat(),
        user=user,
        service_list=service_list,
        total_amount=total_amount
    )

#---- Remove button code---# 

@app.route("/remove_service",methods=["POST"])
@login_required

def remove_servce():
    service_id = str(request.json.get("id"))

    selected_services = session.get("selected_services", [])

    if service_id in selected_services :
        selected_services.remove(service_id)
        session["selected_services"] = selected_services

    return jsonify({"status":"removed"})

#---- Remove button code over---# 

#-=====================Appointment part over=========================================================================#


#================Booking Summary Part==========================================================================#
from datetime import date

@app.route("/booking-summary", methods=["POST"])
@login_required
def booking_summary():

    registration_id = session["user_id"]

    # -------- FORM DATA --------
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    booking_date = request.form.get("date")
    booking_time = request.form.get("time")
    selected_services = request.form.getlist("services")

    # -------- BASIC VALIDATION --------
    if not all([full_name, email, phone, booking_date, booking_time]):
        raise Exception("Missing booking or personal details")

    if not selected_services:
        raise Exception("No services selected")

    cur = mysql.connection.cursor(DictCursor)

    try:

         # Total active slot
        cur.execute("SELECT COUNT(*) AS total_slot FROM seat WHERE status ='active'")
        total_seats = cur.fetchone()["total_slot"]

        # already booked slot 
        cur.execute("""
                    SELECT COUNT(*) AS booked
                    FROM appointment 
                    WHERE appointment_date = %s
                    AND appointment_time = %s
                    """, (booking_date, booking_time))
        
        booked_seats = cur.fetchone()["booked"]
        if booked_seats >= total_seats:
            flash("Selected slot is fully booked. Please choose another time.", "danger")
            return redirect(url_for("appointment"))

        # -------- GET CLIENT & CONTACT --------
        cur.execute("""
            SELECT id, contact_id
            FROM client
            WHERE registration_id = %s
        """, (registration_id,))
        client = cur.fetchone()

        if not client:
            raise Exception("Client not found")

        client_id = client["id"]
        contact_id = client["contact_id"]

        # -------- UPDATE CLIENT --------
        cur.execute("""
            UPDATE client
            SET client_name = %s
            WHERE id = %s
        """, (full_name, client_id))

        # -------- UPDATE CONTACT --------
        cur.execute("""
            UPDATE contact
            SET email = %s, phone = %s
            WHERE id = %s
        """, (email, phone, contact_id))

        # -------- FETCH SERVICES --------
        placeholders = ",".join(["%s"] * len(selected_services))
        cur.execute(f"""
            SELECT s.id, s.name, s.charges
            FROM service s
            JOIN category c ON s.category_id = c.id        
            WHERE s.id IN ({placeholders})
            AND s.status = 1
            AND c.status = 1
        """, tuple(selected_services))

        services = cur.fetchall()

        if  len(services) != len(selected_services):
            raise Exception("One or more selected services are no longer available")

        # -------- CALCULATE TOTAL --------
        total_amount = sum(float(s["charges"]) for s in services)
        service_type = "MULTIPLE" if len(services) > 1 else "SINGLE"

        # -------- INSERT BOOKING --------
        cur.execute("""
            INSERT INTO booking (
                client_id,
                client_name,
                client_email,
                client_phone,
                booking_date,
                booking_time,
                service_type,
                total_amount,
                status,
                payment_status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'PENDING','PENDING')
          """, (
            client_id,
            full_name,
            email,
            phone,
            booking_date,
            booking_time,
            service_type,
            total_amount
        ))

        booking_id = cur.lastrowid

         # -------- INSERT BOOKING SERVICES (LINK ONLY) --------
        for s in services:
            cur.execute("""
                INSERT INTO booking_service (booking_id, service_id)
                VALUES (%s, %s)
            """, (booking_id, s["id"]))

        mysql.connection.commit()

        # -------- SUCCESS --------
        return render_template(
            "user/booking_summary.html",
            booking_id=booking_id,
            full_name=full_name,
            email=email,
            phone=phone,
            services=services,
            booking_date=booking_date,
            booking_time=booking_time,
            total_amount=total_amount
        )


    except Exception as e:
        mysql.connection.rollback()
        print("❌ BOOKING ERROR:", e)
        raise   # show real error during development

    finally:
        cur.close()

#====================Booking Summary Part over=========================================#

#==========================Payment Part==================================#


@app.route("/payment/<int:booking_id>")
@login_required
def payment_page(booking_id):

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT 
            b.id AS booking_id,
            b.total_amount,
            r.full_name,
            r.email
        FROM booking b
        JOIN client c ON b.client_id = c.id
        JOIN registration r ON c.registration_id = r.id
        WHERE b.id = %s
          AND r.id = %s
    """, (booking_id, session["user_id"]))

    booking = cur.fetchone()
    cur.close()

    if not booking:
        flash("Invalid booking.", "error")
        return redirect(url_for("appointment"))

    return render_template(
        "user/payment.html",
        booking=booking   
    )

 ######################################################       

@app.route("/process-payment/<int:booking_id>", methods=["POST"])
@login_required
def process_payment(booking_id):

    user_id = session["user_id"]
    payment_method = request.form.get("payment_method")

    payment_email = request.form.get("payment_email")

    cur = mysql.connection.cursor(DictCursor)

    try:
        # -------- 1. Lock Booking row 
        cur.execute("""
            SELECT id, client_id, total_amount, payment_status,
                    booking_date, booking_time
                    FROM booking
                    WHERE id= %s
                    FOR UPDATE
                    """, (booking_id,))
        booking =cur.fetchone()

        if not booking:
            flash("Invalid booking.", "danger")
            return redirect(url_for("home"))
        
        # 2. Prevent Double Payment
        if booking["payment_status"] == "PAID":
            flash("This booking is already paid.", "info")
            mysql.connection.commit()
            return redirect(url_for("home"))
        
        # 3. Generate Safe Transaction Id
        transaction_id = f"TNXA-{uuid.uuid4().hex[:12].upper()}"

        # 4. Insert Payment 
        cur.execute("""
            INSERT INTO payment 
                    (booking_id,amount, payment_method,payment_email, payment_status, transaction_id)
                    VALUES (%s, %s, %s, %s,  'SUCCESS', %s)
                    """, (
                        booking_id,
                        booking["total_amount"],
                        request.form.get("payment_method"),
                        payment_email,
                        transaction_id
                    )) 
        
        payment_id =cur.lastrowid

          #5. Update Booking Status 
        cur.execute("""
                    UPDATE booking
                    SET payment_status = 'PAID',
                           status ='PAID'
                    WHERE id = %s
                    """, (booking_id,))
        
        # 6. Lock Available Seat
        cur.execute("""
                    SELECT s.id
                    FROM seat s
                    WHERE s.status = 'active'
                    AND s.id NOT IN (
                        SELECT a.seat_id
                        FROM appointment a
                        WHERE a.appointment_date = %s
                        AND a.appointment_time = %s
                    )
                    LIMIT 1
                    FOR UPDATE
                    """, (booking["booking_date"], booking["booking_time"]))
        
        seat =cur.fetchone()

        if not seat:
            mysql.connection.rollback()
            flash("Selected slot is fully booked. Payment cancelled.", "danger")
            return redirect(url_for("appointment"))

        seat_id = seat["id"]


        # 7. Create Appointment
        cur.execute("""
                INSERT INTO appointment
                (booking_id, appointment_date, appointment_time, status, payment_id, seat_id)
                VALUES (%s, %s, %s, 'CONFIRMED', %s, %s)
                """, (
                    booking_id,
                    booking["booking_date"],
                    booking["booking_time"],
                    payment_id,
                    seat_id
                ))   
    # 8. Commit Transaction
        mysql.connection.commit()

    except Exception as e:
        mysql.connection.rollback()
        print("======== ERROR START ========")
        print(e)
        print("======== ERROR END ========")
        flash("Payment failed. Please try again.", "danger")
        return redirect(url_for("payment_page", booking_id=booking_id))
    
    finally:
        cur.close()

    try :
        send_confirmation_email(booking_id)
        send_payment_success_email(booking_id)
        print("CALLING EMAIL...")
    except Exception as e:
        print("Email failed but payment succeeded:", e)

    flash("Payment successful!", "success")
    return redirect(url_for("payment_success", booking_id=booking_id))





def send_confirmation_email(booking_id):

    cur = mysql.connection.cursor(DictCursor)

    print("EMAIL FUNCTION CALLED")

    cur.execute("""
        SELECT
                a.appointment_date,
                a.appointment_time,
                a.seat_id,
                b.client_name,
                b.client_email,
                GROUP_CONCAT(s.name SEPARATOR ' , ') AS services
                FROM appointment a
                JOIN booking b ON a.booking_id =b.id
                JOIN booking_service bs ON b.id = bs.booking_id
                JOIN service s ON bs.service_id = s.id
                WHERE a.booking_id = %s
                GROUP BY a.id
                """, (booking_id,))
    appointment_data = cur.fetchone()
    cur.close()


    if not appointment_data:
        print("No appointment Data found for email.")
        return
    
    EmailService.send_email(
        subject="Appointment Confirmation - Beauty Parlor",
        recipients=[appointment_data["client_email"]],
        template_name="appointment_confirmation.html",
        user_name=appointment_data["client_name"],
        appointment_date=appointment_data["appointment_date"],
        appointment_time=appointment_data["appointment_time"],
        booking_id=booking_id,
        service_name=appointment_data["services"],
        seat_id=f"Seat-{appointment_data['seat_id']}"
    )

def send_payment_success_email(booking_id):

    cur = mysql.connection.cursor(DictCursor)

    print("PAYMENT EMAIL FUNCTION CALLED")

    payment_data = None   # Prevent unbound variable error

    try:
        cur.execute("""
            SELECT
                b.client_name,
                p.payment_email,
                p.amount,
                p.payment_method,
                p.transaction_id,
                p.payment_time,
                b.booking_date,
                b.booking_time,
                GROUP_CONCAT(DISTINCT s.name SEPARATOR ', ') AS services
            FROM payment p
            JOIN booking b ON p.booking_id = b.id
            JOIN booking_service bs ON b.id = bs.booking_id
            JOIN service s ON bs.service_id = s.id
            WHERE p.booking_id = %s
            GROUP BY p.id
        """, (booking_id,))

        payment_data = cur.fetchone()

    except Exception as e:
        print("Payment email query error:", e)

    finally:
        cur.close()

    if not payment_data:
        print("No payment data found for email.")
        return

    EmailService.send_email(
        subject="Payment Successful - Beauty Parlor",
        recipients=[payment_data["payment_email"]],
        template_name="payment_success.html",
        user_name=payment_data["client_name"],
        booking_id=booking_id,
        amount=payment_data["amount"],
        payment_method=payment_data["payment_method"],
        transaction_id=payment_data["transaction_id"],
        payment_time=payment_data["payment_time"],
        booking_date=payment_data["booking_date"],
        booking_time=payment_data["booking_time"],
        services=payment_data["services"]
    )

################################################################################################

@app.route("/payment_success/<int:booking_id>")
@login_required
def payment_success(booking_id):

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT 
            b.id AS booking_id,
            b.total_amount,
            p.payment_email,
            p.transaction_id
        FROM booking b
        JOIN payment p ON b.id = p.booking_id
        WHERE b.id = %s
        ORDER BY p.id DESC
        LIMIT 1
    """, (booking_id,))

    payment = cur.fetchone()
    cur.close()

    if not payment:
        flash("Invalid payment access", "error")
        return redirect(url_for("home"))
    
    session.pop("booking_id", None)
    session.pop("booking_data", None)
    session.pop("booking_services", None)

    session["appointment_popup"] = True

    return render_template("user/payment_success.html", payment=payment)


#==================================================================Payment Part Over==========================================================================#

#===================================================================my Appointment page======================================================================#

@app.route("/my_appointments")
@login_required
def my_appointments():

    user_id = session["user_id"]  # registration.id

    cur = mysql.connection.cursor(DictCursor)

    # -------- FETCH UPCOMING BOOKINGS --------
    cur.execute("""
        SELECT
            b.id AS booking_id,
            b.booking_date,
            b.booking_time,
            b.status AS booking_status,
            b.total_amount,

            
            b.client_name,
            b.client_email,
            b.client_phone,

            p.payment_status,
            p.payment_method,
            p.transaction_id

        FROM booking b
        JOIN client c ON c.id = b.client_id
        JOIN registration r ON r.id = c.registration_id
        LEFT JOIN payment p ON p.booking_id = b.id

        WHERE r.id = %s
          AND (
                b.booking_date > CURDATE()
                OR b.booking_date = CURDATE()
          )

        ORDER BY b.booking_date, b.booking_time
    """, (user_id,))

    bookings = cur.fetchall()

    # -------- FETCH SERVICES FOR EACH BOOKING --------
    for booking in bookings:
        cur.execute("""
            SELECT
                s.name AS service_name,
                st.name AS service_type
            FROM booking_service bs
            JOIN service s ON s.id = bs.service_id
            JOIN service_type st ON st.id = s.service_type_id
            WHERE bs.booking_id = %s
        """, (booking["booking_id"],))

        services = cur.fetchall()
        booking["services"] = [s["service_name"] for s in services]
        booking["service_type"] = services[0]["service_type"] if services else ""

    cur.close()

    return render_template(
        "user/my_appointments.html",
        bookings=bookings
    )

                  

#============================================================ my appointment page over =======================================================================#

#=============================================================History Part ===================================================================================#

@app.route("/appointment_history")
@login_required
def appointment_history():

    user_id = session["user_id"]  # registration.id
    cur = mysql.connection.cursor(DictCursor)

    # Fetch PAST bookings
    cur.execute("""
        SELECT
            b.id AS booking_id,
            b.booking_date,
            b.booking_time,
            b.status AS appointment_status,
            b.total_amount,

            b.client_name,
            b.client_email,
            b.client_phone,

            p.payment_status,
            p.payment_method,
            p.transaction_id

        FROM booking b
        JOIN client c ON c.id = b.client_id
        JOIN registration r ON r.id = c.registration_id
        LEFT JOIN contact ct ON ct.id = c.contact_id
        LEFT JOIN payment p ON p.booking_id = b.id

        WHERE r.id = %s
          AND (
                b.booking_date < CURDATE()
                OR (b.booking_date = CURDATE() AND b.booking_time < CURTIME())
          )
             
        ORDER BY b.booking_date DESC, b.booking_time DESC
    """, (user_id,))

    bookings = cur.fetchall()

    #  Fetch services for each booking
    for booking in bookings:
        cur.execute("""
            SELECT
                s.name AS service_name,
                st.name AS service_type
            FROM booking_service bs
            JOIN service s ON s.id = bs.service_id
            JOIN service_type st ON st.id = s.service_type_id
            WHERE bs.booking_id = %s
        """, (booking["booking_id"],))

        services = cur.fetchall()
        booking["services"] = [s["service_name"] for s in services]
        booking["service_type"] = services[0]["service_type"] if services else ""

    cur.close()

    return render_template(
        "user/appointment_history.html",
        bookings=bookings
    )
#================================= History Part Over ========================================================================#

#============================= Book Again Part ==============#

@app.route("/book-again/<int:booking_id>")
@login_required
def book_again(booking_id):

    user_id = session["user_id"]
    cur = mysql.connection.cursor(DictCursor)

    # Validate booking belongs to logged-in user
    cur.execute("""
        SELECT b.id
        FROM booking b
        JOIN client c ON b.client_id = c.id
        WHERE b.id = %s
          AND c.registration_id = %s
    """, (booking_id, user_id))

    booking = cur.fetchone()
    if not booking:
        cur.close()
        flash("Invalid booking.", "error")
        return redirect(url_for("appointment_history"))

    #  Fetch services from previous booking
    cur.execute("""
        SELECT service_id
        FROM booking_service
        WHERE booking_id = %s
    """, (booking_id,))

    services = cur.fetchall()
    cur.close()

    #  Store services in session
    session["selected_services"] = [str(s["service_id"]) for s in services]

    #  Clear old date & time 
    session.pop("booking_date", None)
    session.pop("booking_time", None)

    flash("Previous services selected. Choose date & time.", "success")

    #  Redirect to appointment page
    return redirect(url_for("appointment"))

#=========================== Book Again Part Over =============================#
   


#================================ Products ==========================#

@app.route('/products')
def products():
    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
            SELECT id, name, brand_name, price, image
                FROM product
                WHERE status = 'ACTIVE'
                ORDER BY id DESC
                """)
    products= cur.fetchall()
    cur.close()

    
    return render_template('products/products.html', products=products)
#===================================== Products over ===================================#

#===================================== About and Contact ===============================#
@app.route('/about')
def about():
    return render_template('user/about.html')

@app.route("/contact")
def contact():

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT 
            r.review_text,
            r.rating,
            r.created_at,
            reg.full_name AS client_name
        FROM review r
        JOIN client c ON c.id = r.client_id
        JOIN registration reg ON reg.id = c.registration_id
        WHERE r.status = 'APPROVED'
        ORDER BY r.created_at DESC
    """)

    reviews = cur.fetchall()
    cur.close()

    return render_template("user/contact.html", reviews=reviews)

    return render_template('user/contact.html')
#=================================================================== About and Contact over ================================================================#

#=================================================================== Review part Start =====================================================================#

@app.route("/submit-review", methods=["POST"])
@login_required
def submit_review():

    rating = request.form.get("rating")
    review_text = request.form.get("review_text")

    if not rating:
        flash("Please select a star rating", "error")
        return redirect(url_for("contact"))

    if not review_text or not review_text.strip():
        flash("Review cannot be empty", "error")
        return redirect(url_for("contact"))

    rating = int(rating)
    registration_id = session["user_id"]

    cur = mysql.connection.cursor(DictCursor)

    
    cur.execute("""
        SELECT id
        FROM client
        WHERE registration_id = %s
    """, (registration_id,))

    client = cur.fetchone()

    if not client:
        flash("Client profile not found. Please book an appointment first.", "error")
        cur.close()
        return redirect(url_for("contact"))

    client_id = client["id"]

    cur.execute("""
        INSERT INTO review (client_id, rating, review_text, status)
        VALUES (%s, %s, %s, 'PENDING')
    """, (client_id, rating, review_text))

    mysql.connection.commit()
    cur.close()

    flash("Thank you! Your review will be visible after approval.", "success")
    return redirect(url_for("contact"))
#===================================================================== Review Part Over ======================================================================#


#============================== TEST EMAIL ==============================#  

if __name__ == "__main__":
    app.run(debug=True)
