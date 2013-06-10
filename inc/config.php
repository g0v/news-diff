<?php

class Config {
    private static $_cache = array();

    private static function load_from_cache($host, $entry) {
        $list = explode('.', $entry);
        for(
            $i=0, $ptr =& self::$_cache[$host];
            isset($list[$i]) && $list[$i]; 
            $ptr =& $ptr[$list[$i++]]) {
//            print_r(array($ptr, $i, $list[$i]));
        }

        return $ptr;
    }

    private static function load_to_cache($host) {
        self::$_cache[$host] = json_decode(file_get_contents(PATH_CONF . $host . '.json'), true);
    }

    static function get($host, $entry) {
        if (!isset(self::$_cache[$host])) {
            static::load_to_cache($host);
        }

        return self::load_from_cache($host, $entry);
    }
}
