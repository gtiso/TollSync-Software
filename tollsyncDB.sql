CREATE DATABASE IF NOT EXISTS tollsync;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'user';
GRANT ALL PRIVILEGES ON tollsync.* TO 'user'@'localhost';
FLUSH PRIVILEGES;
