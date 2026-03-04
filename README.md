<h1>Beauty Parlor Management System</h1>
A full-stack web application built using Flask and MySQL that helps manage beauty parlor appointments, bookings, and payments efficiently.
<br>
This system allows clients to book services, make payments, and receive confirmation emails, while the admin can manage appointments and services from the backend.
<hr>
<h2>Tech Stack</h2>

<b>Backend</b>

  Python

   Flask

<b>Database</b>

  MySQL

<b>Frontend</b>

  HTML
  
  CSS

  Bootstrap

  Basic JavaScript

<b>Other Tools</b>

  Flask-Mail

  Git & GitHub

  <hr>

  <h2>Installation</h2>
  1. Clone the repository

git clone https://github.com/Aryan-Dongre/Beauty-Parlor-Management-Systems-.git

2. Navigate to project folder

cd Beauty-Parlor-Management-System

3. Create virtual environment

python -m venv venv

4. Activate virtual environment

Windows:
venv\Scripts\activate

5. Install dependencies

pip install -r requirements.txt

6. Configure environment variables

Create a .env file and add:

SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_email_password

7. Run the application

python app.py

<hr>

<h2>System Development Phases</h2>

<h4>Level 1 – Core Booking & Payment System</h4>
The First phase focuses on building the core functionality required for managing appointments.
<br>
Features implement in this phase:
<br>
 1.Authentication with proper login system
 <br>
 2. User booking system
 <br>
 3.Service selection
 <br>
 4.Multiple service booking
 <br>
 5.Booking database management
 <br>
 6.Payment transaction storage
 <br>
 7.Seat allocation for appointments
 <br>
 8.Appointment creation after successful payment
 <br>
 9.View appointments functionality
 <br>
 10.Admin management of services and bookings, payment.

 At this stage, system successfully handles the complete workflow:

 Client Booking → Payment → Appointment Creation.

 <h4>Level 2 – Email Notification System</h4>

 The second phase introduces automation through an email notification sustem.
 <br>
 Email notification are implemented  using Flask-Mail with Gmail SMTP.

 Features implementd in this phase:
<br>
 1.Appointment confirmation email
 <br>
 2.Payment success email
 <br>
 3.Password reset email
 <br>
 4.HTML email templates
 <br>
 5.Secure email integration

 Email notifications are triggered automatically after specific events such as:

Successful payment

Appointment confirmation

Password reset request

 
