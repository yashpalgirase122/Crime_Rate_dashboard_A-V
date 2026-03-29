CREATE DATABASE IF NOT EXISTS crime_dashboard_db;
USE crime_dashboard_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS crime_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    crime_type VARCHAR(100),
    predicted_count FLOAT,
    prediction_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_message TEXT,
    city VARCHAR(100),
    severity ENUM('LOW', 'MEDIUM', 'HIGH'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: The admin password hash is for 'admin123' used by werkzeug
INSERT IGNORE INTO users (username, email, password_hash, role) VALUES ('admin', 'admin@example.com', 'scrypt:32768:8:1$1uW31FzWehR3m8wX$12a9e334a17387cc22e342722108ecb059cfbe9cb6e17446342898b9a1da8cbf3ebddc3733e884175390a364bb2eb7e2bbd06b3e9a7e32bad7684df61ff1e605', 'admin');
