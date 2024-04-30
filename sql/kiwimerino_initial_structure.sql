# ************************************************************
# Sequel Ace SQL dump
# Version 20062
#
# https://sequel-ace.com/
# https://github.com/Sequel-Ace/Sequel-Ace
#
# Host: localhost (MySQL 8.0.36)
# Database: kiwimerino
# Generation Time: 2024-03-11 21:53:27 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE='NO_AUTO_VALUE_ON_ZERO', SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table booking
# ------------------------------------------------------------

DROP TABLE IF EXISTS `booking`;

CREATE TABLE `booking` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned DEFAULT NULL,
  `booking_datetime` datetime DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `type` varchar(32) DEFAULT NULL,
  `lession_id` int unsigned DEFAULT NULL,
  `workshop_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_workshop_id` (`workshop_id`),
  KEY `fk_booking_user_id` (`user_id`),
  CONSTRAINT `fk_booking_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_workshop_id` FOREIGN KEY (`workshop_id`) REFERENCES `workshop` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table image
# ------------------------------------------------------------

DROP TABLE IF EXISTS `image`;

CREATE TABLE `image` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
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
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `tutor_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_lesson_tutor_id` (`tutor_id`),
  CONSTRAINT `fk_lesson_tutor_id` FOREIGN KEY (`tutor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table lesson_schedule
# ------------------------------------------------------------

DROP TABLE IF EXISTS `lesson_schedule`;

CREATE TABLE `lesson_schedule` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `lesson_id` int unsigned DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `cost` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_lesson_schedule_lesson_id` (`lesson_id`),
  CONSTRAINT `fk_lesson_schedule_lesson_id` FOREIGN KEY (`lesson_id`) REFERENCES `lesson` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table location
# ------------------------------------------------------------

DROP TABLE IF EXISTS `location`;

CREATE TABLE `location` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
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
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `content` text,
  `publish_at` datetime DEFAULT NULL,
  `author` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table subscription
# ------------------------------------------------------------

DROP TABLE IF EXISTS `subscription`;

CREATE TABLE `subscription` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `price` decimal(8,2) NOT NULL DEFAULT '0.00',
  `duration` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table user
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `first_name` varchar(32) DEFAULT NULL,
  `last_name` varchar(32) DEFAULT NULL,
  `title` varchar(32) DEFAULT NULL,
  `position` varchar(32) DEFAULT NULL,
  `phone_number` varchar(32) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `profile_image_id` int unsigned DEFAULT NULL,
  `password` varchar(64) DEFAULT NULL,
  `salt` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table user_subscription
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user_subscription`;

CREATE TABLE `user_subscription` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `subscription_id` int unsigned NOT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `cost` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_user_id` (`user_id`),
  KEY `fk_subscription_id` (`subscription_id`),
  CONSTRAINT `fk_subscription_id` FOREIGN KEY (`subscription_id`) REFERENCES `subscription` (`id`),
  CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table workshop
# ------------------------------------------------------------

DROP TABLE IF EXISTS `workshop`;

CREATE TABLE `workshop` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(32) DEFAULT NULL,
  `location_id` int unsigned DEFAULT NULL,
  `price` decimal(8,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `fk_workshop` (`location_id`),
  CONSTRAINT `fk_workshop` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table workshop_schedule
# ------------------------------------------------------------

DROP TABLE IF EXISTS `workshop_schedule`;

CREATE TABLE `workshop_schedule` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `workshop_id` int unsigned DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `finish_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_workshop_schedule_workshop_id` (`workshop_id`),
  CONSTRAINT `fk_workshop_schedule_workshop_id` FOREIGN KEY (`workshop_id`) REFERENCES `workshop` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
