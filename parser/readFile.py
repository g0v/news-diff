from datetime import date
import json
from os import makedirs
from os.path import join, dirname, abspath
from posix import listdir
import re
from parser.source對應表 import source對應表


class 轉編輯模式:

    @classmethod
    def _is_json(cls, myjson):
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True

    @classmethod
    def _parse(cls, 來源檔):
        with open(來源檔) as 檔案:
            lines = 檔案.readlines()
            meta = ''
            title = ''
            content = ''

            for i in range(0, len(lines)):
                currentLine = lines[i].rstrip()
#             print(currentLine)
                if cls._is_json(currentLine) and currentLine.startswith('{'):
                    #
                    # output previous
                    #
                    if len(meta) > 0:
                        yield json.loads(meta), json.loads(title), json.loads(content)
                    #
                    # new block
                    #
                    meta = currentLine
                    title = ''
                    content = ''
                elif len(meta) > 0 and len(title) == 0:
                    title = currentLine
                else:
                    content += currentLine

    @classmethod
    def 掃全部檔案(cls, 開始日期, 結束日期, 來源資料夾, 目標資料夾):
        新聞編號對應表 = {}
        for 檔名 in listdir(來源資料夾):
            if 檔名.endswith('.txt'):
                完整檔名 = join(來源資料夾, 檔名)
                for 一篇新聞 in cls._parse(完整檔名):
                    meta, _標題, _內容 = 一篇新聞
                    新聞編號 = meta['id']
                    if 新聞編號 not in 新聞編號對應表:
                        新聞編號對應表[新聞編號] = []
                    新聞編號對應表[新聞編號].append(一篇新聞)
        開始日期字串 = '{}-{:02}-{:02}'.format(*開始日期)
        結束日期字串 = '{}-{:02}-{:02}'.format(*結束日期)
        cls._輸出檔案(開始日期字串, 結束日期字串, 新聞編號對應表, 目標資料夾)

    @classmethod
    def _揣網址變化(cls, 新聞陣列):
        網址變化 = []
        for 一篇新聞 in 新聞陣列:
            meta, _標題, _內容 = 一篇新聞
            網址變化.append(meta['url'])
        return 網址變化

    @classmethod
    def _算日期(cls, meta):
        return date.fromtimestamp(
            int(meta['created_at'])
        ).strftime("%Y-%m-%d")

    @classmethod
    def _產生輸出檔名(cls, meta, 標題, 幾版):
        return '{}／{}／{}／{}／{}／.txt'.format(
            cls._算日期(meta),
            source對應表[int(meta['source'])],
            meta['id'],
            re.sub(r'\W', '_', 標題),
            幾版,
        )

    @classmethod
    def _產生檔案內容(cls, 網址變化, 上尾內容):
        版 = "--->\n{0}\n\n\n{1}"
        return 版.format(
            '\n'.join(['　　' + 網址 for 網址 in 網址變化]),
            上尾內容
        )

    @classmethod
    def _輸出檔案(cls, 開始日期字串, 結束日期字串, 新聞編號對應表, 目標資料夾):
        makedirs(目標資料夾, exist_ok=True)
        for 編號, 新聞陣列 in sorted(新聞編號對應表.items()):
            網址變化 = cls._揣網址變化(新聞陣列)
            頭一篇meta, _標題, _內容 = 新聞陣列[0]
            這篇日期字串 = cls._算日期(頭一篇meta)
            if 開始日期字串 <= 這篇日期字串 and 這篇日期字串 <= 結束日期字串:
                _meta, 上尾標題, 上尾內容 = 新聞陣列[-1]
    #             meta, 標題, 內容 = 一篇新聞
                try:
                        # 1. 第三個值是文章id編號，因為考慮標題有可能會變動
                        # 2. 第四個值是標題，多雙引號，怕到時有奇怪的符號，電腦會出錯
                    檔名 = cls._產生輸出檔名(頭一篇meta, 上尾標題, len(新聞陣列))
                    with open(join(目標資料夾, 檔名), 'w') as _輸出檔案:
                        print(cls._產生檔案內容(網址變化, 上尾內容), file=_輸出檔案)
                except:
                    print(編號)
                    raise
if __name__ == '__main__':
    #
    # read file
    #
    sourceDir = join(dirname(abspath(__file__)), 'extract')
    targetDir = join(dirname(abspath(__file__)), '結果資料夾')
    轉編輯模式.掃全部檔案((2016, 2, 6), (2016, 2, 15), sourceDir, targetDir)
