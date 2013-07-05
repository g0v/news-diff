# Dev Note #

## Global ##

系統內的資料與物件 (lib/*/*.py) 都視為 immutable；內容若變動應更換檔名，以便除錯。
唯一例外是 contents /articles 的 last_seen_on 欄位，表示最後一次抓出同樣資料
的時間。

## DB ##

### InnoDB Autoirement ###

MySQL 在 5.5 版改變了 InnoDB 對主鍵鎖定的邏輯；使得若有部份列因 rollback、
INSERT IGNORE、INSERT ... ON DUPLICATE KEY 而最終未寫入，則主鍵內的某些數值
會被跳過。

由於這個專案會頻繁發出 request 並嘗試寫入，被跳過的鍵值可能會造成困擾；因此我
將主機的 innodb_autoinc_lock_mode 設為 0；未來版本將在資料寫入前加入重覆值的
過濾 (lib.db.save_*)。

