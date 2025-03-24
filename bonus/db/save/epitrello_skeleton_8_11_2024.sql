-- MariaDB dump 10.19  Distrib 10.11.2-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: epitrello
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB-ubu2404
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!40101 SET NAMES utf8mb4 */
;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */
;
/*!40103 SET TIME_ZONE='+00:00' */
;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */
;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */
;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */
;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */
;
--
-- Current Database: `epitrello`
--

CREATE DATABASE
/*!32312 IF NOT EXISTS*/
`epitrello`
/*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */
;
USE `epitrello`;
--
-- Table structure for table `boards`
--

DROP TABLE IF EXISTS `boards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `boards` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `background_color` varchar(100) NOT NULL,
  `list_nb` bigint(20) unsigned NOT NULL,
  `workspace_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_workspace_FK` (`workspace_id`),
  CONSTRAINT `board_workspace_FK` FOREIGN KEY (`workspace_id`) REFERENCES `workspaces` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `boards`
--

LOCK TABLES `boards` WRITE;
/*!40000 ALTER TABLE `boards` DISABLE KEYS */
;
/*!40000 ALTER TABLE `boards` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `boards_activities`
--

DROP TABLE IF EXISTS `boards_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `boards_activities` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `message` varchar(1000) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `board_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_activity_board_FK` (`board_id`),
  CONSTRAINT `board_activity_board_FK` FOREIGN KEY (`board_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `boards_activities`
--

LOCK TABLES `boards_activities` WRITE;
/*!40000 ALTER TABLE `boards_activities` DISABLE KEYS */
;
/*!40000 ALTER TABLE `boards_activities` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `boards_lists`
--

DROP TABLE IF EXISTS `boards_lists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `boards_lists` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `board_id` bigint(20) unsigned NOT NULL,
  `position` bigint(20) unsigned NOT NULL,
  `card_nb` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `board_list_board_FK` (`board_id`),
  CONSTRAINT `board_list_board_FK` FOREIGN KEY (`board_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `boards_lists`
--

LOCK TABLES `boards_lists` WRITE;
/*!40000 ALTER TABLE `boards_lists` DISABLE KEYS */
;
/*!40000 ALTER TABLE `boards_lists` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `cards_assignees`
--

DROP TABLE IF EXISTS `cards_assignees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `cards_assignees` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `card_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `card_assignees_users_FK` (`user_id`),
  KEY `card_assignees_list_card_FK` (`card_id`),
  CONSTRAINT `card_assignees_list_card_FK` FOREIGN KEY (`card_id`) REFERENCES `lists_cards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `card_assignees_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `cards_assignees`
--

LOCK TABLES `cards_assignees` WRITE;
/*!40000 ALTER TABLE `cards_assignees` DISABLE KEYS */
;
/*!40000 ALTER TABLE `cards_assignees` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `lists_cards`
--

DROP TABLE IF EXISTS `lists_cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `lists_cards` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` varchar(2000) DEFAULT NULL,
  `date_end` datetime DEFAULT NULL,
  `list_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `list_card_board_list_FK` (`list_id`),
  CONSTRAINT `list_card_board_list_FK` FOREIGN KEY (`list_id`) REFERENCES `boards_lists` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `lists_cards`
--

LOCK TABLES `lists_cards` WRITE;
/*!40000 ALTER TABLE `lists_cards` DISABLE KEYS */
;
/*!40000 ALTER TABLE `lists_cards` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `notifications` (
  `id` bigint(20) unsigned NOT NULL,
  `message` varchar(1000) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_users_FK` (`user_id`),
  CONSTRAINT `notifications_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */
;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `email` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `password` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL,
  `favicon` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL,
  `bio` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_unique` (`email`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'The table that store every users data';
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */
;
/*!40000 ALTER TABLE `users` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `users_connections`
--

DROP TABLE IF EXISTS `users_connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `users_connections` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `token` varchar(200) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_connection_unique` (`token`),
  KEY `user_connection_users_FK` (`user_id`),
  CONSTRAINT `user_connection_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `users_connections`
--

LOCK TABLES `users_connections` WRITE;
/*!40000 ALTER TABLE `users_connections` DISABLE KEYS */
;
/*!40000 ALTER TABLE `users_connections` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `workspaces`
--

DROP TABLE IF EXISTS `workspaces`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `workspaces` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `creator_id` bigint(20) unsigned NOT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `favicon` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workspace_users_FK` (`creator_id`),
  CONSTRAINT `workspace_users_FK` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `workspaces`
--

LOCK TABLES `workspaces` WRITE;
/*!40000 ALTER TABLE `workspaces` DISABLE KEYS */
;
/*!40000 ALTER TABLE `workspaces` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `workspaces_invitations`
--

DROP TABLE IF EXISTS `workspaces_invitations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `workspaces_invitations` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `workspace_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workspace_invitation_users_FK` (`user_id`),
  CONSTRAINT `workspace_invitation_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `workspace_invitation_workspace_FK` FOREIGN KEY (`workspace_id`) REFERENCES `workspaces` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `workspaces_invitations`
--

LOCK TABLES `workspaces_invitations` WRITE;
/*!40000 ALTER TABLE `workspaces_invitations` DISABLE KEYS */
;
/*!40000 ALTER TABLE `workspaces_invitations` ENABLE KEYS */
;
UNLOCK TABLES;
--
-- Table structure for table `workspaces_members`
--

DROP TABLE IF EXISTS `workspaces_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */
;
/*!40101 SET character_set_client = utf8 */
;
CREATE TABLE `workspaces_members` (
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
  CONSTRAINT `workspace_members_workspace_FK` FOREIGN KEY (`workspace_id`) REFERENCES `workspaces` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */
;
--
-- Dumping data for table `workspaces_members`
--

LOCK TABLES `workspaces_members` WRITE;
/*!40000 ALTER TABLE `workspaces_members` DISABLE KEYS */
;
/*!40000 ALTER TABLE `workspaces_members` ENABLE KEYS */
;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */
;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */
;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */
;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */
;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */
;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */
;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */
;
-- Dump completed on 2024-11-08 12:43:35
