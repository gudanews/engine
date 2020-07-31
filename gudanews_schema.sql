-- MySQL dump 10.17  Distrib 10.3.22-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: gudanews
-- ------------------------------------------------------
-- Server version	10.3.22-MariaDB-0+deb10u1

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
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comment` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `parent_id` int(32) NOT NULL DEFAULT 0,
  `user_id` int(24) NOT NULL DEFAULT 0,
  `datetime` datetime DEFAULT current_timestamp(),
  `body` varchar(512) DEFAULT NULL,
  `likes` int(24) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `headline`
--

DROP TABLE IF EXISTS `headline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `headline` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `is_processed` tinyint(1) NOT NULL DEFAULT 0,
  `is_displayable` tinyint(1) NOT NULL DEFAULT 0,
  `duplicate_id` int(32) NOT NULL DEFAULT 0,
  `source_id` int(16) NOT NULL DEFAULT 0,
  `image_id` int(32) NOT NULL DEFAULT 0,
  `news_id` int(32) NOT NULL DEFAULT 0,
  `heading` varchar(256) DEFAULT NULL,
  `url` varchar(512) DEFAULT 'NULL',
  `datetime` datetime DEFAULT current_timestamp(),
  `snippet` varchar(320) DEFAULT NULL,
  `quality` int(16) NOT NULL DEFAULT 0,
  `view` int(24) NOT NULL DEFAULT 0,
  `likes` int(24) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `source_id` (`source_id`),
  KEY `is_processed` (`is_processed`),
  KEY `is_displayable` (`is_displayable`),
  FULLTEXT KEY `snippet` (`snippet`),
  FULLTEXT KEY `heading` (`heading`)
) ENGINE=MyISAM AUTO_INCREMENT=2684 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website home page';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `image`
--

DROP TABLE IF EXISTS `image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `image` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `path` varchar(128) DEFAULT NULL,
  `thumbnail` varchar(128) DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2041 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used to store image locally';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `type_id` int(8) NOT NULL DEFAULT 0,
  `url` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `is_indexed` tinyint(1) NOT NULL DEFAULT 0,
  `headline_id` int(32) NOT NULL DEFAULT 0,
  `image_id` int(32) NOT NULL DEFAULT 0,
  `source_id` int(16) NOT NULL DEFAULT 0,
  `datetime` datetime DEFAULT current_timestamp(),
  `heading` varchar(256) DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  `body` text DEFAULT NULL,
  `likes` int(24) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `headline_id` (`headline_id`),
  KEY `is_indexed` (`is_indexed`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website news content page';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_comment`
--

DROP TABLE IF EXISTS `news_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_comment` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `news_id` int(32) NOT NULL DEFAULT 0,
  `comment_id` int(32) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `news_id` (`news_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_image`
--

DROP TABLE IF EXISTS `news_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_image` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `news_id` int(32) NOT NULL DEFAULT 0,
  `image_id` int(32) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `news_id` (`news_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=FIXED COMMENT='Used for news data and image relation';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_media`
--

DROP TABLE IF EXISTS `news_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_media` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `news_id` int(32) NOT NULL DEFAULT 0,
  `media_id` int(32) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `data_id` (`news_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `source`
--

DROP TABLE IF EXISTS `source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `source` (
  `id` int(16) NOT NULL,
  `is_crawling` tinyint(1) NOT NULL,
  `crawling_url` varchar(512) DEFAULT 'NULL',
  `name` varchar(32) DEFAULT NULL,
  `display_name` varchar(32) DEFAULT NULL,
  `image_id` int(32) NOT NULL DEFAULT 0,
  `host` varchar(64) DEFAULT NULL,
  `bias` int(8) NOT NULL,
  `quality` int(16) NOT NULL DEFAULT 0,
  `popularity` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used to store news source';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-07-30 22:51:21
