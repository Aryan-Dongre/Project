
CREATE DATABASE BEAUTY_PARLOR;
USE BEAUTY_PARLOR;

DESCRIBE service;

SELECT status, COUNT(*) 
FROM service
GROUP BY status;




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

UPDATE registration 
set password = 'scrypt:32768:8:1$bqst6k6cSyMyCCc3$2dfed0af4afcaab469d64121cdd1ac3cb7141c2815c3b2df37a36668ad3392f0db77e826db5b50d0901a0db09abbfd21d430b9291aebca177c25444daa466e26'
where email = 'admin@beautyparlor.com';

/*Reset password table*/
CREATE TABLE password_reset_tokens(
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  
  user_id INT NOT NULL,
  token_hash CHAR(64) NOT NULL,
  
  expires_at DATETIME NOT NULL,
  used_at DATETIME NUll,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_reset_user
             FOREIGN KEY (user_id)
             REFERENCES registration(id)
             ON DELETE CASCADE,
  
  CONSTRAINT uq_token_hash UNIQUE (token_hash),
  
  INDEX idx_user_id (user_id),
  INDEX idx_expires_at (expires_at)
  );
  
  
  




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

ALTER TABLE service ADD status TINYINT(1) DEFAULT 1;


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
ALTER TABLE product
 ADD COLUMN image VARCHAR(255),
ADD COLUMN status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER status;

ALTER TABLE product ADD description TEXT;
ALTER TABLE product ADD quantity VARCHAR(50);

INSERT INTO product 
(name, brand_name, price, image, status, created_at, description, quantity)
VALUES
('Herbal Shampoo', 'Mamaearth', 399, 'shampoo.webp', 'ACTIVE', NOW(),
 'Deep nourishing shampoo for dry hair.', '250ml'),

('Hair Spray', 'Mamaearth', 549, 'hair_spray.jpg', 'ACTIVE', NOW(),
 'Long lasting hair hold spray.', '200ml'),

('Hydrating Mask', 'Lakme', 699, 'Hydrating Mask.webp', 'ACTIVE', NOW(),
 'Moisturizing face mask for glowing skin.', '100gm'),

('Lipstick', 'Lakme', 1000, 'lipstick.jpg', 'ACTIVE', NOW(),
 'Matte finish long lasting lipstick.', '10gm');




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

SHOW COLUMNS FROM booking LIKE 'status';


ALTER TABLE booking
ADD COLUMN total_amount DECIMAL(10,2) NOT NULL AFTER booking_time;

ALTER TABLE booking
ADD COLUMN client_name VARCHAR(100) AFTER client_id,
ADD COLUMN client_email VARCHAR(100) AFTER client_name,
ADD COLUMN client_phone VARCHAR(20) AFTER client_email,
ADD COLUMN service_type VARCHAR(50) AFTER booking_time;

SELECT * FROM booking;

-- 13. Booking Service (Many-to-Many)
CREATE TABLE booking_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
) ENGINE=InnoDB;

/*Seat Table*/

drop table seat;

CREATE TABLE seat (
             id int AUTO_INCREMENT PRIMARY KEY,
             seat_name varchar(50) NOT NULL,
             seat_type varchar(20) NOT NULL,
              status ENUM('active','inactive') DEFAULT 'active'
              );

ALTER TABLE seat 
ADD service_type_id INT;

SET SQL_SAFE_UPDATES = 0;

UPDATE seat SET service_type_id = 1 WHERE seat_type = 'NORMAL';
UPDATE seat SET service_type_id = 2 WHERE seat_type = 'GROOM';
UPDATE seat SET service_type_id = 3 WHERE seat_type = 'BRIDAL';

ALTER TABLE seat 
MODIFY service_type_id INT NOT NULL;
              
ALTER TABLE seat
ADD CONSTRAINT fk_seat_service_type
FOREIGN KEY (service_type_id)
REFERENCES service_type(id)
ON DELETE CASCADE;

ALTER TABLE seat
DROP COLUMN seat_type;

SET SQL_SAFE_UPDATES = 1;

INSERT INTO seat (seat_name, service_type_id, status)
VALUES 
('Chair 1', 1, 'active'),
('Chair 2', 1, 'active'),
('Chair 3', 1, 'active'),
('Chair 4', 1, 'active'),
('Chair 5', 1, 'active');              

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

ALTER TABLE payment
ADD UNIQUE (booking_id);


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
    
ALTER TABLE appointment
ADD UNIQUE (booking_id);

ALTER TABLE appointment
MODIFY status ENUM('PENDING','CONFIRMED','COMPLETED','CANCELLED') NOT NULL;

ALTER TABLE appointment DROP COLUMN status;
ALTER TABLE appointment
ADD COLUMN status ENUM('PENDING','CONFIRMED','COMPLETED','CANCELLED')
NOT NULL DEFAULT 'PENDING';

ALTER TABLE appointment
MODIFY payment_id INT NULL;


ALTER TABLE appointment
ADD seat_id INT,
ADD CONSTRAINT fk_seat
FOREIGN KEY (seat_id) REFERENCES seat(id)
ON DELETE SET NULL;

ALTER TABLE appointment
ADD CONSTRAINT unique_seat_slot
UNIQUE (seat_id, appointment_date, appointment_time);










SHOW COLUMNS FROM appointment;

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

alter table review
add column status ENUM('PENDING', 'APPROVED', 'REJECTED') 
default 'PENDING' AFTER comment ;

ALTER TABLE review 
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at DATETIME 
DEFAULT CURRENT_TIMESTAMP 
ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE review
CHANGE update_at updated_at DATETIME
DEFAULT CURRENT_TIMESTAMP
ON UPDATE CURRENT_TIMESTAMP;


DESCRIBE review;


ALTER TABLE review
ADD COLUMN booking_id INT NULL AFTER service_id;

ALTER TABLE review
ADD CONSTRAINT fk_review_booking
FOREIGN KEY (booking_id) REFERENCES booking(id)
ON DELETE SET NULL;

ALTER TABLE review
CHANGE comment review_text TEXT;

ALTER TABLE review MODIFY service_id INT NULL;
ALTER TABLE review MODIFY booking_id INT NULL;





