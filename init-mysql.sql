-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `db_wiad` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if it doesn't exist (MySQL 8.0 syntax)
CREATE USER IF NOT EXISTS 'flaskapp'@'%' IDENTIFIED BY 'asdadwacsa';

-- Grant privileges
GRANT ALL PRIVILEGES ON `db_wiad`.* TO 'flaskapp'@'%';

-- Flush privileges to ensure they take effect
FLUSH PRIVILEGES;

-- Show that everything is ready
SELECT 'Database and user setup complete!' as status;