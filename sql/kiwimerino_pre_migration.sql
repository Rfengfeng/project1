# ************************************************************
# Sequel Ace SQL dump
# Version 20062
#
# https://sequel-ace.com/
# https://github.com/Sequel-Ace/Sequel-Ace
#
# Host: localhost (MySQL 8.0.36)
# Database: foobar
# Generation Time: 2024-03-15 02:44:00 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE='NO_AUTO_VALUE_ON_ZERO', SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table alembic_version
# ------------------------------------------------------------

DROP TABLE IF EXISTS `alembic_version`;

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;

INSERT INTO `alembic_version` (`version_num`)
VALUES
	('a417abf9e220');

/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table booking
# ------------------------------------------------------------

DROP TABLE IF EXISTS `booking`;

CREATE TABLE `booking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `booking_datetime` datetime DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `type` varchar(32) DEFAULT NULL,
  `workshop_id` int DEFAULT NULL,
  `lesson_id` int DEFAULT NULL,
  `cost` decimal(8,2) NOT NULL,
  `amount_paid` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `workshop_id` (`workshop_id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `booking_ibfk_3` FOREIGN KEY (`workshop_id`) REFERENCES `workshop` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `booking_ibfk_4` FOREIGN KEY (`lesson_id`) REFERENCES `lesson` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table image
# ------------------------------------------------------------

DROP TABLE IF EXISTS `image`;

CREATE TABLE `image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `size` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table lesson
# ------------------------------------------------------------

DROP TABLE IF EXISTS `lesson`;

CREATE TABLE `lesson` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `tutor_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tutor_id` (`tutor_id`),
  CONSTRAINT `lesson_ibfk_1` FOREIGN KEY (`tutor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table lesson_schedule
# ------------------------------------------------------------

DROP TABLE IF EXISTS `lesson_schedule`;

CREATE TABLE `lesson_schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lesson_id` int DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `cost` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `lesson_schedule_ibfk_1` FOREIGN KEY (`lesson_id`) REFERENCES `lesson` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table location
# ------------------------------------------------------------

DROP TABLE IF EXISTS `location`;

CREATE TABLE `location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `address1` varchar(64) DEFAULT NULL,
  `address2` varchar(64) DEFAULT NULL,
  `suburb` varchar(32) DEFAULT NULL,
  `city` varchar(32) DEFAULT NULL,
  `region` varchar(32) DEFAULT NULL,
  `state` varchar(32) DEFAULT NULL,
  `postcode` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table news
# ------------------------------------------------------------

DROP TABLE IF EXISTS `news`;

CREATE TABLE `news` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) DEFAULT NULL,
  `content` text,
  `publish_at` datetime DEFAULT NULL,
  `author` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table subscription
# ------------------------------------------------------------

DROP TABLE IF EXISTS `subscription`;

CREATE TABLE `subscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `price` decimal(8,2) NOT NULL,
  `duration` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table test
# ------------------------------------------------------------

DROP TABLE IF EXISTS `test`;

CREATE TABLE `test` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `first_name` varchar(32) DEFAULT NULL,
  `last_name` varchar(32) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `sex` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table user
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(32) NOT NULL,
  `last_name` varchar(32) NOT NULL,
  `title` varchar(32) DEFAULT NULL,
  `position` varchar(32) DEFAULT NULL,
  `phone_number` varchar(32) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `profile_image_id` int DEFAULT NULL,
  `password` varchar(64) NOT NULL,
  `salt` varchar(32) NOT NULL,
  `role` enum('manager','tutor','member') NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `profile_image_id` (`profile_image_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`profile_image_id`) REFERENCES `image` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table user_subscription
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user_subscription`;

CREATE TABLE `user_subscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `subscription_id` int NOT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `cost` decimal(8,2) DEFAULT NULL,
  `amount_paid` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `subscription_id` (`subscription_id`),
  CONSTRAINT `user_subscription_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `user_subscription_ibfk_2` FOREIGN KEY (`subscription_id`) REFERENCES `subscription` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table workshop
# ------------------------------------------------------------

DROP TABLE IF EXISTS `workshop`;

CREATE TABLE `workshop` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(32) DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `price` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `workshop_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table workshop_schedule
# ------------------------------------------------------------

DROP TABLE IF EXISTS `workshop_schedule`;

CREATE TABLE `workshop_schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `workshop_id` int DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `finish_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `workshop_id` (`workshop_id`),
  CONSTRAINT `workshop_schedule_ibfk_1` FOREIGN KEY (`workshop_id`) REFERENCES `workshop` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `reminder`;

CREATE TABLE `reminder` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `remind_at` datetime NOT NULL,
  `receiver_id` int,
  `sender_id` int,
  `read_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `receiver_id` (`receiver_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `reminder_ibfk_1` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`),
  CONSTRAINT `reminder_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
