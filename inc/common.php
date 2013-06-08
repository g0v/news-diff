<?php

define('PATH_ROOT', dirname(__dir__) . '/');
define('PATH_CONF', PATH_ROOT . 'conf/');
define('PATH_INC',  PATH_ROOT . 'inc/');
define('PATH_BIN',  PATH_ROOT . 'bin/');


require('config.php');

require('orm.php');
require('article.php');
require('content.php');

