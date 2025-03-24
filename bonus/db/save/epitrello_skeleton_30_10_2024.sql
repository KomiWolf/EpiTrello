-- MariaDB dump 10.19  Distrib 10.11.2-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: epitrello
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `epitrello`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `epitrello` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;

USE `epitrello`;

--
-- Table structure for table `board`
--

DROP TABLE IF EXISTS `board`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `board` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `background_color` varchar(100) NOT NULL,
  `list_nb` bigint(20) unsigned NOT NULL,
  `workspace_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_workspace_FK` (`workspace_id`),
  CONSTRAINT `board_workspace_FK` FOREIGN KEY (`workspace_id`) REFERENCES `workspace` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `board`
--

LOCK TABLES `board` WRITE;
/*!40000 ALTER TABLE `board` DISABLE KEYS */;
/*!40000 ALTER TABLE `board` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `board_activity`
--

DROP TABLE IF EXISTS `board_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `board_activity` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `message` varchar(1000) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `board_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_activity_board_FK` (`board_id`),
  CONSTRAINT `board_activity_board_FK` FOREIGN KEY (`board_id`) REFERENCES `board` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `board_activity`
--

LOCK TABLES `board_activity` WRITE;
/*!40000 ALTER TABLE `board_activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `board_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `board_list`
--

DROP TABLE IF EXISTS `board_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `board_list` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `board_id` bigint(20) unsigned NOT NULL,
  `position` bigint(20) unsigned NOT NULL,
  `card_nb` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_list_board_FK` (`board_id`),
  CONSTRAINT `board_list_board_FK` FOREIGN KEY (`board_id`) REFERENCES `board` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `board_list`
--

LOCK TABLES `board_list` WRITE;
/*!40000 ALTER TABLE `board_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `board_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card_assignees`
--

DROP TABLE IF EXISTS `card_assignees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_assignees` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `card_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `card_assignees_users_FK` (`user_id`),
  KEY `card_assignees_list_card_FK` (`card_id`),
  CONSTRAINT `card_assignees_list_card_FK` FOREIGN KEY (`card_id`) REFERENCES `list_card` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `card_assignees_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_assignees`
--

LOCK TABLES `card_assignees` WRITE;
/*!40000 ALTER TABLE `card_assignees` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_assignees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `list_card`
--

DROP TABLE IF EXISTS `list_card`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `list_card` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` varchar(2000) DEFAULT NULL,
  `date_end` datetime DEFAULT NULL,
  `list_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `list_card_board_list_FK` (`list_id`),
  CONSTRAINT `list_card_board_list_FK` FOREIGN KEY (`list_id`) REFERENCES `board_list` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `list_card`
--

LOCK TABLES `list_card` WRITE;
/*!40000 ALTER TABLE `list_card` DISABLE KEYS */;
/*!40000 ALTER TABLE `list_card` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` bigint(20) unsigned NOT NULL,
  `message` varchar(1000) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_users_FK` (`user_id`),
  CONSTRAINT `notifications_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_connection`
--

DROP TABLE IF EXISTS `user_connection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_connection` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `token` varchar(200) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_connection_unique` (`token`),
  KEY `user_connection_users_FK` (`user_id`),
  CONSTRAINT `user_connection_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_connection`
--

LOCK TABLES `user_connection` WRITE;
/*!40000 ALTER TABLE `user_connection` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_connection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `email` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `password` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `favicon` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL,
  `bio` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_unique` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='The table that store every users data';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workspace`
--

DROP TABLE IF EXISTS `workspace`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `workspace` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `creator_id` bigint(20) unsigned NOT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `favicon` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workspace_users_FK` (`creator_id`),
  CONSTRAINT `workspace_users_FK` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workspace`
--

LOCK TABLES `workspace` WRITE;
/*!40000 ALTER TABLE `workspace` DISABLE KEYS */;
/*!40000 ALTER TABLE `workspace` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workspace_invitation`
--

DROP TABLE IF EXISTS `workspace_invitation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `workspace_invitation` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `workspace_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workspace_invitation_users_FK` (`user_id`),
  CONSTRAINT `workspace_invitation_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `workspace_invitation_workspace_FK` FOREIGN KEY (`id`) REFERENCES `workspace` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workspace_invitation`
--

LOCK TABLES `workspace_invitation` WRITE;
/*!40000 ALTER TABLE `workspace_invitation` DISABLE KEYS */;
/*!40000 ALTER TABLE `workspace_invitation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workspace_members`
--

DROP TABLE IF EXISTS `workspace_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `workspace_members` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `workspace_id` bigint(20) unsigned NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `board_creation_restriction` tinyint(1) NOT NULL,
  `board_deletion_restriction` tinyint(1) NOT NULL,
  `invitation_restriction` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workspace_members_users_FK` (`user_id`),
  KEY `workspace_members_workspace_FK` (`workspace_id`),
  CONSTRAINT `workspace_members_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `workspace_members_workspace_FK` FOREIGN KEY (`workspace_id`) REFERENCES `workspace` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workspace_members`
--

LOCK TABLES `workspace_members` WRITE;
/*!40000 ALTER TABLE `workspace_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `workspace_members` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-30  0:11:03
