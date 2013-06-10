<?php

require('inc/common.php');

if (0) {
    $a = Article::forge(array(
        'url' => 'http://nowhere.com/nothing'
    ));
    $a->save();
}

if (1) {
    print_r(Article::find());
}
