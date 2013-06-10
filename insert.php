<?php

require('inc/common.php');

$fp = fopen("articles.csv", "r");

$column_names = array(
    'id',
    'title',
    'url',
    'src_title',
    'published_on',
    'fulltext',
    'inserted'
);

$pdo = ORM::pdo();

$pdo->query("TRUNCATE TABLE `_articles`");
$stmt = $pdo->prepare('REPLACE INTO `_articles` values (?,?,?,?,?,?,?)');

while($raw = fgetcsv($fp)) {
    $stmt->execute($raw);
}

fclose($fp);
