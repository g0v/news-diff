-- phpMyAdmin SQL Dump
-- version 4.0.4.1
-- http://www.phpmyadmin.net
--
-- 主機: localhost
-- 產生日期: 2013 年 07 月 25 日 17:45
-- 伺服器版本: 5.6.12-rc60.4
-- PHP 版本: 5.4.9-4ubuntu2.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 資料庫: `news_production`
--
CREATE DATABASE IF NOT EXISTS `news_production` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
USE `news_production`;

-- --------------------------------------------------------

--
-- 表的結構 `articles`
--

CREATE TABLE IF NOT EXISTS `articles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(512) COLLATE utf8_bin NOT NULL,
  `pub_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `created_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `last_seen_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `feed_id` mediumint(8) unsigned NOT NULL,
  `ctlr_id` mediumint(8) unsigned NOT NULL,
  `url_hash` binary(16) NOT NULL COMMENT '原始狀態 url',
  `url_read_hash` binary(16) NOT NULL COMMENT '若被轉址，記錄最終之 url',
  `url_canonical_hash` binary(16) NOT NULL COMMENT '若回應中包含該 meta 則留存',
  `meta_hash` binary(16) NOT NULL,
  `html_hash` binary(16) NOT NULL,
  `text_hash` binary(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_canonical_hash_2` (`url_canonical_hash`,`text_hash`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1856 ;

-- --------------------------------------------------------

--
-- 表的結構 `article__htmls`
--

CREATE TABLE IF NOT EXISTS `article__htmls` (
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `article__meta`
--

CREATE TABLE IF NOT EXISTS `article__meta` (
  `hash` binary(16) NOT NULL,
  `body` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `article__texts`
--

CREATE TABLE IF NOT EXISTS `article__texts` (
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- 表的結構 `article__urls`
--

CREATE TABLE IF NOT EXISTS `article__urls` (
  `hash` binary(16) NOT NULL,
  `body` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
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
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=9 ;

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
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `title` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`feed_id`),
  UNIQUE KEY `url` (`url`),
  KEY `host_id` (`host_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=50 ;

-- --------------------------------------------------------

--
-- 表的結構 `fetches`
--

CREATE TABLE IF NOT EXISTS `fetches` (
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
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
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  PRIMARY KEY (`host_id`),
  UNIQUE KEY `url` (`url`),
  KEY `name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=8 ;

-- --------------------------------------------------------

--
-- 表的結構 `responses`
--

CREATE TABLE IF NOT EXISTS `responses` (
  `last_seen_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `feed_id` mediumint(8) unsigned DEFAULT NULL,
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  `body_hash` binary(16) NOT NULL,
  `meta` text COLLATE utf8_bin NOT NULL,
  UNIQUE KEY `url` (`url`,`body_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='抓取到的文章原文；若內容變動則寫入新列，否則僅修改原列之值';

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
