-- Diabetes Prediction AI System — MySQL schema
-- Run this once against an empty database, e.g.:
--   mysql -u root -p < schema.sql
-- (FastAPI's Base.metadata.create_all also creates these automatically on
-- first startup if they don't exist — this file is provided for clarity,
-- manual setup, and production migrations.)

CREATE DATABASE IF NOT EXISTS diabetes_ai_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE diabetes_ai_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  pregnancies INT NOT NULL,
  glucose FLOAT NOT NULL,
  bloodpressure FLOAT NOT NULL,
  skinthickness FLOAT NOT NULL,
  insulin FLOAT NOT NULL,
  bmi FLOAT NOT NULL,
  dpf FLOAT NOT NULL,
  age INT NOT NULL,
  prediction INT NOT NULL,
  probability FLOAT NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_predictions_user (user_id),
  INDEX idx_predictions_created (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reminders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  message TEXT,
  remind_at DATETIME NOT NULL,
  is_sent BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_reminders_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  action VARCHAR(150) NOT NULL,
  details TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_activity_user (user_id),
  INDEX idx_activity_created (created_at)
) ENGINE=InnoDB;
