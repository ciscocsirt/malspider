/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alert`
--

DROP TABLE IF EXISTS `alert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alert` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reason` varchar(250) NOT NULL,
  `uri` varchar(1000) DEFAULT NULL,
  `raw` text,
  `event_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `page_id` varchar(50) DEFAULT NULL,
  `org_id` int(11) DEFAULT NULL,
  `page` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2043075 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `element`
--

DROP TABLE IF EXISTS `element`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `element` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(255) DEFAULT NULL,
  `uri` varchar(1000) DEFAULT NULL,
  `referer` varchar(1000) DEFAULT NULL,
  `tag_name` varchar(50) DEFAULT NULL,
  `onsite` varchar(50) DEFAULT NULL,
  `org_id` varchar(50) DEFAULT NULL,
  `page_id` varchar(50) DEFAULT NULL,
  `raw` text,
  `attr_width` varchar(50) DEFAULT NULL,
  `attr_height` varchar(50) DEFAULT NULL,
  `attr_text` varchar(50) DEFAULT NULL,
  `attr_type` varchar(50) DEFAULT NULL,
  `attr_language` varchar(50) DEFAULT NULL,
  `attr_script_type` varchar(50) DEFAULT NULL,
  `css_attr_visibility` varchar(50) DEFAULT NULL,
  `css_attr_bottom` int(11) DEFAULT NULL,
  `css_attr_top` int(11) DEFAULT NULL,
  `css_attr_left` int(11) DEFAULT NULL,
  `css_attr_right` int(11) DEFAULT NULL,
  `css_class` varchar(50) DEFAULT NULL,
  `event_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=396286 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organization`
--

DROP TABLE IF EXISTS `organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `org_name` varchar(255) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1704 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `page`
--

DROP TABLE IF EXISTS `page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(1000) DEFAULT NULL,
  `referer` varchar(1000) DEFAULT NULL,
  `status_code` varchar(50) DEFAULT NULL,
  `org_id` varchar(50) DEFAULT NULL,
  `useragent` varchar(1000) DEFAULT NULL,
  `event_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ssdeep_pagesource` varchar(255) DEFAULT NULL,
  `ssdeep_screenshot` varchar(255) DEFAULT NULL,
  `screenshot` varchar(255) DEFAULT NULL,
  `num_offsite_links` int(11) DEFAULT NULL,
  `num_onsite_links` int(11) DEFAULT NULL,
  `page_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39406 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


--
-- Table structure for table `whitelist`
--
DROP TABLE IF EXISTS `whitelist`;
CREATE TABLE `whitelist` (
  `pattern` varchar(255) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pattern_UNIQUE` (`pattern`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


--
-- Table structure for table `email_alerts`
--
DROP TABLE IF EXISTS `email_alert`;
CREATE TABLE `email_alert` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipients` text,
  `subject` varchar(250) NOT NULL,
  `frequency` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
