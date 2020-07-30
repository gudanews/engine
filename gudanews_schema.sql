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
-- Table structure for table `data`
--

DROP TABLE IF EXISTS `data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data` (
  `id` int(32) NOT NULL,
  `is_indexed` tinyint(1) NOT NULL DEFAULT 0,
  `headline_id` int(32) NOT NULL,
  `image_id` int(32) NOT NULL DEFAULT 0,
  `source_id` int(16) NOT NULL,
  `heading` varchar(256) NOT NULL,
  `datetime` datetime DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  `content` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website news content page';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_image`
--

DROP TABLE IF EXISTS `data_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_image` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `news_id` int(32) NOT NULL DEFAULT 0,
  `image_id` int(32) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=FIXED COMMENT='Used for news data and image relation';
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
  `data_id` int(32) NOT NULL DEFAULT 0,
  `heading` varchar(256) DEFAULT NULL,
  `url` varchar(512) DEFAULT 'NULL',
  `datetime` datetime DEFAULT NULL,
  `snippet` varchar(320) DEFAULT NULL,
  `quality` int(8) NOT NULL DEFAULT 0,
  `view` int(24) NOT NULL DEFAULT 0,
  `click` int(24) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `source_id` (`source_id`),
  KEY `image_id` (`image_id`),
  KEY `id` (`id`) USING BTREE,
  KEY `duplicate_id` (`duplicate_id`),
  KEY `data_id` (`data_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2514 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website home page';
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
) ENGINE=MyISAM AUTO_INCREMENT=1920 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used to store image locally';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `source`
--

DROP TABLE IF EXISTS `source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `source` (
  `id` int(16) NOT NULL,
  `is_crawling` tinyint(1) NOT NULL DEFAULT 0,
  `name` varchar(32) NOT NULL,
  `display_name` varchar(32) NOT NULL,
  `bias` int(8) NOT NULL,
  `image` varchar(256) DEFAULT NULL,
  `website` varchar(512) DEFAULT NULL,
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

-- Dump completed on 2020-07-30 16:16:23
