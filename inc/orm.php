<?php

abstract class ORM {
    protected static $_table_name = '';
    protected static $_primary_keys = array();
    protected static $_columns = array();

    protected $_data = array();
    protected $_data_original = array();

    private function _update() {
        $pdo = static::pdo();
        
        $stmt = $pdo->prepare(
            // ok, mysql only for now
            sprintf('REPLACE INTO `%s` (%s) VALUES (%s)', 
                static::$_table_name, 
                join(',', array_map(function($col_name){return "`$col_name`";}, array_keys($this->_data))),
                str_repeat('?', count($this->_data))
            )
        );

        $stmt->execute(array_values($this->_data));
    }
  
    public function has_pk() {
        foreach(static::$_primary_keys as $pk) {
            if (!isset($_data[$pk]))
                return false;
        }
        return true;
    }

    public function save() {
        if ($this->has_pk())
            return $this->_update();
        // return $this->_new();
        return $this->_update();
    }

    protected function __construct($data, $is_init = false) {
        $this->_data = $data;

        if ($is_init) {
            $this->_data_original = $data;
        }
    }

    private static $_pdo_obj;
    public static function pdo() {
        if (!is_resource(self::$_pdo_obj)) {
            self::$_pdo_obj = new PDO(
                Config::get('db', 'default.driver').':'.
                'dbname=' . Config::get('db', 'default.db').
                ';host=' . Config::get('db', 'default.host'), 
                Config::get('db', 'default.user'),
                Config::get('db', 'default.pass')
            );
        }

        return self::$_pdo_obj;
    }

    public static function forge($arr = array()) {
        $arr = array_merge(static::defaults(), $arr);
        return new static($arr);
    }

    public static function hydrate($array) {
        return new static($array, true); 
    }

    public static function find($id = array()) {
        $pdo = self::pdo();
        $qkey = array();
        $qval = array();

        if ($id) {
            foreach($id as $col => $val) {
                $qkey[] = "`$col` = ?`";
                $qval[] = $val;
            }
        } else {
            $qkey = array(1);
        }
        
        $stmt = $pdo->prepare(sprintf('SELECT * FROM `%s` WHERE %s',
            static::$_table_name, join(' AND ', $qkey)
        ));
        $stmt->execute($qval);
        
        $output = array();
        foreach($stmt->fetchAll() as $row) {
            print_r($row);
        }
        return $output;   
    }

    /**
     * Deafault values for ORM
     */
    public static function defaults() {
        return array();
    }
}
