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
-- Dumping data for table `comment`
--

LOCK TABLES `comment` WRITE;
/*!40000 ALTER TABLE `comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `comment` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website home page';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `headline`
--

LOCK TABLES `headline` WRITE;
/*!40000 ALTER TABLE `headline` DISABLE KEYS */;
/*!40000 ALTER TABLE `headline` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used to store image locally';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `image`
--

LOCK TABLES `image` WRITE;
/*!40000 ALTER TABLE `image` DISABLE KEYS */;
/*!40000 ALTER TABLE `image` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
/*!40000 ALTER TABLE `media` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Used for website news content page';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `news_comment`
--

LOCK TABLES `news_comment` WRITE;
/*!40000 ALTER TABLE `news_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `news_comment` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `news_image`
--

LOCK TABLES `news_image` WRITE;
/*!40000 ALTER TABLE `news_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `news_image` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `news_media`
--

LOCK TABLES `news_media` WRITE;
/*!40000 ALTER TABLE `news_media` DISABLE KEYS */;
/*!40000 ALTER TABLE `news_media` ENABLE KEYS */;
UNLOCK TABLES;

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

--
-- Dumping data for table `source`
--

LOCK TABLES `source` WRITE;
/*!40000 ALTER TABLE `source` DISABLE KEYS */;
INSERT INTO `source` VALUES (1,1,'https://www.reuters.com/theWire','Reuters','Reuters',0,NULL,0,0,70.44),(2,1,'https://apnews.com/apf-topnews','AP','Associated Press',0,NULL,0,0,37.20),(3,0,'https://www.upi.com/Top_News/','UPI','United Press International',0,NULL,0,0,3.40),(4,0,'https://www.afp.com/en','AFP','Agence France-Presse',0,NULL,0,0,3.69),(101,1,'https://us.cnn.com/','CNN','CNN',0,NULL,-7,0,757.87),(102,0,'https://www.bbc.com/news','BBC NEWS','BBC News',0,NULL,-3,0,432.12),(103,0,'https://www.nytimes.com/','NYT','The New York Times',0,NULL,-3,0,397.10),(104,1,'https://www.foxnews.com/','FOX NEWS','Fox News',0,NULL,7,0,369.77),(105,0,'https://www.dailymail.co.uk/','DailyMail.com','Daily Mail',0,NULL,7,0,318.29),(106,0,'https://www.theguardian.com/us','The Guardian','The Guardian',0,NULL,-3,0,312.82),(107,0,'https://www.washingtonpost.com/','The Washington Post','The Washington Post',0,NULL,-3,0,218.47),(108,0,'https://www.usatoday.com/news/','USA TODAY','USA TODAY',0,NULL,-3,0,122.45),(109,0,'https://nypost.com/news/','NYPost','New York Post',0,NULL,3,0,115.89),(110,0,'https://www.nbcnews.com/','NBC News','NBC News',0,NULL,-3,0,105.09),(111,0,'https://www.npr.org/sections/news/','NPR','National Public Radio',0,NULL,-3,0,99.34),(112,0,'https://www.huffpost.com/news/','HUFFPOST','The Huffington Post',0,NULL,-7,0,84.41),(113,0,'https://www.breitbart.com/','Breitbart','Breitbart News Network',0,NULL,9,0,80.81),(114,0,'https://www.politico.com/','POLITICO','POLITICO',0,NULL,0,0,70.37),(115,0,'https://www.wsj.com/','WSJ','The Wall Street Journal',0,NULL,3,0,68.38),(116,0,'https://www.latimes.com/','LA Times','Los Angeles Times',0,NULL,-3,0,54.07),(117,0,'https://www.cbsnews.com/','CBS News','CBS News',0,NULL,-3,0,53.26),(118,0,'https://abcnews.go.com/','abcNEWS','ABCNews',0,NULL,-3,0,51.39);
/*!40000 ALTER TABLE `source` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-07-30 22:51:29
