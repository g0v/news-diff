-- phpMyAdmin SQL Dump
-- version 4.0.4.1
-- http://www.phpmyadmin.net
--
-- 主機: localhost
-- 產生日期: 2013 年 08 月 15 日 18:16
-- 伺服器版本: 5.5.32-31.0-log
-- PHP 版本: 5.4.9-4ubuntu2.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 資料庫: `news_develop`
--
CREATE DATABASE IF NOT EXISTS `news_develop` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
USE `news_develop`;

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
  `html_hash` binary(16) NOT NULL COMMENT '若解析失敗則標為 unhex(0), as a magic number',
  `text_hash` binary(16) NOT NULL,
  `src_hash` binary(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_canonical_hash` (`url_canonical_hash`,`text_hash`),
  KEY `feed_id` (`feed_id`),
  KEY `ctlr_id` (`ctlr_id`),
  KEY `url_hash` (`url_hash`),
  KEY `url_read_hash` (`url_read_hash`),
  KEY `meta_hash` (`meta_hash`),
  KEY `html_hash` (`html_hash`),
  KEY `text_hash` (`text_hash`),
  KEY `src_hash` (`src_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `article__htmls`
--

CREATE TABLE IF NOT EXISTS `article__htmls` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=COMPRESSED AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `article__meta`
--

CREATE TABLE IF NOT EXISTS `article__meta` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `hash` binary(16) NOT NULL,
  `body` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `article__srcs`
--

CREATE TABLE IF NOT EXISTS `article__srcs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=COMPRESSED AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `article__texts`
--

CREATE TABLE IF NOT EXISTS `article__texts` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `hash` binary(16) NOT NULL,
  `body` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=COMPRESSED AUTO_INCREMENT=1 ;

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
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
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
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `category` enum('unknown','error','response','revisit','rss_2_0') COLLATE utf8_bin NOT NULL DEFAULT 'unknown',
  `src` mediumtext COLLATE utf8_bin NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的結構 `responses`
--

CREATE TABLE IF NOT EXISTS `responses` (
  `last_seen_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `feed_id` mediumint(8) unsigned DEFAULT NULL,
  `url` varchar(512) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `src` mediumtext COLLATE utf8_bin NOT NULL,
  `src_hash` binary(16) NOT NULL,
  `meta` text COLLATE utf8_bin NOT NULL,
  UNIQUE KEY `url` (`url`,`src_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='抓取到的文章原文；若內容變動則寫入新列，否則僅修改原列之值';

-- --------------------------------------------------------

--
-- 替換 view以便查看 `view_articles`
--
CREATE TABLE IF NOT EXISTS `view_articles` (
`id` bigint(20) unsigned
,`title` varchar(512)
,`pub_ts` timestamp
,`created_on` timestamp
,`last_seen_on` timestamp
,`feed_id` mediumint(8) unsigned
,`ctlr_id` mediumint(8) unsigned
,`url_hash` binary(16)
,`url` varchar(512)
,`url_read_hash` binary(16)
,`url_read` varchar(512)
,`url_canonical_hash` binary(16)
,`url_canonical` varchar(512)
,`meta_hash` binary(16)
,`meta` text
,`html_hash` binary(16)
,`html` mediumtext
,`text_hash` binary(16)
,`text` mediumtext
,`src_hash` binary(16)
,`src` mediumtext
);
-- --------------------------------------------------------

--
-- view結構 `view_articles`
--
DROP TABLE IF EXISTS `view_articles`;

CREATE ALGORITHM=MERGE DEFINER=`_news`@`localhost` SQL SECURITY DEFINER VIEW `view_articles` AS select `a`.`id` AS `id`,`a`.`title` AS `title`,`a`.`pub_ts` AS `pub_ts`,`a`.`created_on` AS `created_on`,`a`.`last_seen_on` AS `last_seen_on`,`a`.`feed_id` AS `feed_id`,`a`.`ctlr_id` AS `ctlr_id`,`a`.`url_hash` AS `url_hash`,`au`.`body` AS `url`,`a`.`url_read_hash` AS `url_read_hash`,`aur`.`body` AS `url_read`,`a`.`url_canonical_hash` AS `url_canonical_hash`,`auc`.`body` AS `url_canonical`,`a`.`meta_hash` AS `meta_hash`,`am`.`body` AS `meta`,`a`.`html_hash` AS `html_hash`,`ah`.`body` AS `html`,`a`.`text_hash` AS `text_hash`,`at`.`body` AS `text`,`a`.`src_hash` AS `src_hash`,`as`.`body` AS `src` from (((((((`articles` `a` left join `article__texts` `at` on((`a`.`text_hash` = `at`.`hash`))) left join `article__htmls` `ah` on((`a`.`html_hash` = `ah`.`hash`))) left join `article__meta` `am` on((`a`.`meta_hash` = `am`.`hash`))) left join `article__srcs` `as` on((`a`.`src_hash` = `as`.`hash`))) left join `article__urls` `au` on((`a`.`url_hash` = `au`.`hash`))) left join `article__urls` `aur` on((`a`.`url_read_hash` = `aur`.`hash`))) left join `article__urls` `auc` on((`a`.`url_canonical_hash` = `auc`.`hash`)));

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
