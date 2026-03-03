
CREATE DATABASE BEAUTY_PARLOR;
USE BEAUTY_PARLOR;


/* =========================
   MASTER TABLES
========================= */

-- 1. Gender (ONLY Men & Women)
CREATE TABLE gender (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO gender (name) VALUES
('Men'),
('Women');

-- 2. Service Type (NORMAL / GROOM / BRIDAL)
CREATE TABLE service_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO service_type (name) VALUES
('NORMAL'),
('GROOM'),
('BRIDAL');

-- 3. Category (common across Men, Women, Groom, Bridal)
CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

INSERT INTO category (name) VALUES
('Hair Cut'),
('Hair Styling'),
('Skin Care'),
('Face Care'),
('Massage'),
('Makeup'),
('Packages');

-- 4. Address
CREATE TABLE address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    street VARCHAR(150),
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10)
) ENGINE=InnoDB;


-- 5. Contact
CREATE TABLE contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15),
    email VARCHAR(100)
) ENGINE=InnoDB;


/* =========================
   USER & STAFF TABLES
========================= */

-- 6. Registration (Login table)
CREATE TABLE registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('CLIENT', 'STAFF', 'ADMIN') NOT NULL
) ENGINE=InnoDB;

INSERT INTO registration (full_name, email, password, role)
VALUES ('Aryan', 'admin@beautyparlor.com', 'admin123', 'ADMIN');


-- 7. Client
CREATE TABLE client (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id INT NOT NULL,
    address_id INT,
    contact_id INT,
    FOREIGN KEY (registration_id) REFERENCES registration(id),
    FOREIGN KEY (address_id) REFERENCES address(id),
    FOREIGN KEY (contact_id) REFERENCES contact(id)
) ENGINE=InnoDB;

ALTER TABLE client
ADD COLUMN client_name VARCHAR(100) NOT NULL AFTER id;

-- 8. Staff
CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    address_id INT,
    contact_id INT,
    FOREIGN KEY (address_id) REFERENCES address(id),
    FOREIGN KEY (contact_id) REFERENCES contact(id)
) ENGINE=InnoDB;


-- 9. Seller
CREATE TABLE seller (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_id INT,
    FOREIGN KEY (contact_id) REFERENCES contact(id)
) ENGINE=InnoDB;


/* =========================
   BUSINESS TABLES
========================= */

-- 10. Service
CREATE TABLE service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    charges DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL, -- in minutes
    gender_id INT,              -- ONLY for NORMAL services
    category_id INT NOT NULL,
    service_type_id INT NOT NULL,
    FOREIGN KEY (gender_id) REFERENCES gender(id),
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (service_type_id) REFERENCES service_type(id)
) ENGINE=InnoDB;

-- .MEN
INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Men Basic Hair Cut', 150, 30, 1, 1, 1),
('Men Fade Hair Cut', 200, 40, 1, 1, 1),
('Men Premium Hair Cut', 300, 45, 1, 1, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Men Hair Styling', 200, 30, 1, 2, 1),
('Men Hair Spa', 500, 45, 1, 2, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Men Basic Facial', 600, 45, 1, 3, 1),
('Men Premium Facial', 900, 60, 1, 3, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Men Head Massage', 300, 30, 1, 5, 1),
('Men Full Body Massage', 1200, 90, 1, 5, 1);

-- .WOMEN

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Women Layer Hair Cut', 400, 60, 2, 1, 1),
('Women Bob Hair Cut', 350, 50, 2, 1, 1),
('Women Step Hair Cut', 450, 65, 2, 1, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Women Hair Styling', 500, 45, 2, 2, 1),
('Women Hair Spa', 800, 60, 2, 2, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Women Basic Facial', 800, 60, 2, 3, 1),
('Women Premium Facial', 1200, 75, 2, 3, 1);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Women Head Massage', 400, 30, 2, 5, 1),
('Women Full Body Massage', 1500, 90, 2, 5, 1);

-- .GROOM
INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Groom Classic Hair Cut', 1200, 60, NULL, 1, 2),
('Groom Premium Hair Cut', 1800, 75, NULL, 1, 2);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Groom Hair Styling', 1500, 60, NULL, 2, 2),
('Groom Hair Spa', 2000, 75, NULL, 2, 2);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Groom Facial', 2500, 90, NULL, 3, 2),
('Groom Skin Treatment', 3000, 120, NULL, 3, 2);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Groom Basic Package', 5000, 180, NULL, 7, 2),
('Groom Premium Package', 8000, 240, NULL, 7, 2);

-- .BRIDAL

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Bridal Hair Design', 3500, 120, NULL, 1, 3),
('Bridal Advanced Hair Styling', 5000, 150, NULL, 2, 3);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Bridal Makeup', 8000, 180, NULL, 6, 3),
('Bridal Engageement Makeup', 10000, 180, NULL, 6, 3),
('Bridal HD Makeup', 12000, 240, NULL, 6, 3);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Bridal Skin Care', 6000, 120, NULL, 3, 3);

INSERT INTO service (name, charges, duration, gender_id, category_id, service_type_id)
VALUES
('Bridal Basic Package', 15000, 300, NULL, 7, 3),
('Bridal Premium Package', 25000, 420, NULL, 7, 3);




-- 11. Product
CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand_name VARCHAR(100),
    price DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;


/* =========================
   TRANSACTION TABLES
========================= */

-- 12. Booking
CREATE TABLE booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'CANCELLED') DEFAULT 'PENDING',
    FOREIGN KEY (client_id) REFERENCES client(id)
) ENGINE=InnoDB;

ALTER TABLE booking
MODIFY status ENUM('PENDING', 'PAID', 'CANCELLED') DEFAULT 'PENDING';
ALTER TABLE booking
ADD COLUMN payment_status ENUM('PENDING', 'PAID') DEFAULT 'PENDING';



ALTER TABLE booking
ADD COLUMN total_amount DECIMAL(10,2) NOT NULL AFTER booking_time;




-- 13. Booking Service (Many-to-Many)
CREATE TABLE booking_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
) ENGINE=InnoDB;


-- 14. Payment
CREATE TABLE payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status ENUM('PENDING', 'SUCCESS', 'FAILED') DEFAULT 'PENDING',
    FOREIGN KEY (booking_id) REFERENCES booking(id)
) ENGINE=InnoDB;

ALTER TABLE payment
ADD COLUMN payment_email VARCHAR(150) NOT NULL AFTER amount,
ADD COLUMN payment_time DATETIME DEFAULT CURRENT_TIMESTAMP AFTER payment_method;

ALTER TABLE payment
ADD COLUMN transaction_id VARCHAR(100) AFTER payment_status;

ALTER TABLE payment
MODIFY payment_status 
ENUM('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED') DEFAULT 'PENDING';

ALTER TABLE payment
DROP FOREIGN KEY payment_ibfk_1;

ALTER TABLE payment
ADD CONSTRAINT fk_payment_booking
FOREIGN KEY (booking_id) REFERENCES booking(id)
ON DELETE CASCADE;

ALTER TABLE payment
ADD COLUMN updated_at DATETIME 
DEFAULT CURRENT_TIMESTAMP 
ON UPDATE CURRENT_TIMESTAMP;







-- 15. Appointment
CREATE TABLE appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_id INT NOT NULL,
    staff_id INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (payment_id) REFERENCES payment(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
) ENGINE=InnoDB;

ALTER TABLE appointment
ADD COLUMN  status ENUM( 'CONFIRMED',
    'COMPLETED',
    'CANCELLED',
    'NO_SHOW')DEFAULT 'CONFIRMED';



-- 16. Review
CREATE TABLE review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    service_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (client_id) REFERENCES client(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
) ENGINE=InnoDB;





