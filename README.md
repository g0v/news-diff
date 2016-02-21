News-Diff
==================
新聞 Crawler，並且當新聞內容變動時發出通知。

REQUIREMENTS
------------------
* python-dateutil
* BeautifulSoup4
* cssselect

* python-lxml
* python-mysqldb

## Parse資料檔
###下載檔案
```
virtualenv --python=python2 venv2; . venv2/bin/activate; pip install --upgrade pip
pip install parallel_sync
python parser/myCurl.py 
```

### 轉成文字檔
```
virtualenv --python=python3 venv; . venv2/bin/activate; pip install --upgrade pip
python parser/readFile.py
```


LICENSE
------------------
MIT
