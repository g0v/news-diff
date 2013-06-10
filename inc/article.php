<?php

class Article extends ORM{
    protected static $_table_name = 'articles';
    protected static $_primary_keys = array('id');
    protected static $_columns = array('id', 'url', 'published_on', 'src_id', 'title');


    
}
