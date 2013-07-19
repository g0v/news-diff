-- phpMyAdmin SQL Dump
-- version 4.0.4.1
-- http://www.phpmyadmin.net
--
-- 主機: localhost
-- 產生日期: 2013 年 07 月 19 日 09:20
-- 伺服器版本: 5.5.31-30.3-log
-- PHP 版本: 5.4.15-1ubuntu3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 資料庫: `news`
--
CREATE DATABASE IF NOT EXISTS `news` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
USE `news`;

-- --------------------------------------------------------

--
-- 表的結構 `articles`
--

CREATE TABLE IF NOT EXISTS `articles` (
  `pub_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `created_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `last_seen_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `feed_id` mediumint(8) unsigned DEFAULT NULL,
  `ctlr_id` mediumint(8) unsigned NOT NULL,
  `url` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `title` varchar(512) COLLATE utf8_bin NOT NULL,
  `meta` longtext COLLATE utf8_bin NOT NULL,
  `html_hash` binary(16) NOT NULL,
  `text_hash` binary(16) NOT NULL,
  PRIMARY KEY (`url`,`text_hash`,`created_on`),
  UNIQUE KEY `text_hash` (`text_hash`,`url`),
  KEY `html_hash` (`html_hash`),
  KEY `feed_id` (`feed_id`),
  KEY `ctlr_id` (`ctlr_id`),
  KEY `created_on` (`created_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `article_htmls`
--

CREATE TABLE IF NOT EXISTS `article_htmls` (
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `article_texts`
--

CREATE TABLE IF NOT EXISTS `article_texts` (
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `ctlrs`
--

CREATE TABLE IF NOT EXISTS `ctlrs` (
  `ctlr_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `classname` varchar(128) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ctlr_id`),
  UNIQUE KEY `classname` (`classname`),
  UNIQUE KEY `ctlr_id` (`ctlr_id`,`created_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `ctlr_feed`
--

CREATE TABLE IF NOT EXISTS `ctlr_feed` (
  `feed_id` mediumint(8) unsigned NOT NULL,
  `ctlr_id` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`feed_id`,`ctlr_id`),
  KEY `parser_id` (`ctlr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `feeds`
--

CREATE TABLE IF NOT EXISTS `feeds` (
  `feed_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `host_id` mediumint(8) unsigned DEFAULT NULL,
  `url` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `title` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`feed_id`),
  UNIQUE KEY `url` (`url`),
  KEY `host_id` (`host_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `fetches`
--

CREATE TABLE IF NOT EXISTS `fetches` (
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `url` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `category` enum('unknown','error','response','revisit','rss_2_0') COLLATE utf8_bin NOT NULL DEFAULT 'unknown',
  `response` longtext COLLATE utf8_bin NOT NULL,
  UNIQUE KEY `category` (`category`,`url`,`created_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `hosts`
--

CREATE TABLE IF NOT EXISTS `hosts` (
  `host_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8_bin NOT NULL,
  `url` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  PRIMARY KEY (`host_id`),
  UNIQUE KEY `url` (`url`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `responses`
--

CREATE TABLE IF NOT EXISTS `responses` (
  `last_seen_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `feed_id` mediumint(8) unsigned DEFAULT NULL,
  `url` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  `body_md5` binary(16) NOT NULL,
  `meta` text COLLATE utf8_bin NOT NULL,
  UNIQUE KEY `body_md5` (`body_md5`,`url`),
  KEY `ctlr_id` (`feed_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='抓取到的文章原文；若內容變動則寫入新列，否則僅修改原列之值';

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
