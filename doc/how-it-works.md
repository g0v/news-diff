資料
====================

News-Diff 記錄的資料如下，分別對應至同名資料表：

* article: 未解析 (parse) 之新聞 html 全文，以及相關 meta data
* content: 解析後之新聞內文，以及相關 meta data
* fetch: 透過 lib.Fetcher 抓取之所有資料
* host: 新聞來源網站
* indexor: 新聞來源列表，例如 RSS URL
* parser: 記錄解析器 (parser) 之物件名稱並編號
* keyword: 關鍵字

其中 fetch, article, content 為分析主軸，存有本專案主要資料；
indexor, parser 儲存分析主軸的物件名稱，便於除錯。由於 indexor 中的 url 未必位於
host 之網域下，因此其中欄位 host_id 可能需要人工修改。

host, keyword 為手動維護之表，主要供 web 前端操作使用。

分析邏輯
=====================
