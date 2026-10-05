-- init.sql 
-- Runs automatically when the MySQL container starts for the first time.
-- Creates the users table and seeds two test accounts.
-- The database trainingdb is auto-created by MySQL via the env var MYSQL_DATABASE.

USE trainingdb;

-- Table definition
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed users (passwords are securely hashed for Werkzeug)
-- Login credentials for testing:
-- username: admin    | password: password123
-- username: trainee  | password: training

INSERT INTO users (username, password_hash) 
VALUES
('admin', 'scrypt:32768:8:1$v2X2Blz54gZN0WAW$0382afbd77e2ba7fdbc0375d9fa852580c8d189c60bbf48ca1dd523b0b22243d78d2097359d8da21809b7d938dfc3ca2b58682f3a479a7031767c3dccf902bfa'),
('trainee', 'pbkdf2:sha256:600000$93P3ZHNRtX8aAkEI$13b8ab5e56ecd5c722f243934123d14edbda547fa7aeb3025560a6276379d6eb');
