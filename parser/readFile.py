import json
from os import makedirs
from os.path import join, dirname, abspath
from parser.source對應表 import source對應表
from datetime import date


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def parse(來源檔, 結果資料夾):
    makedirs(結果資料夾, exist_ok=True)
    lines = open(來源檔).readlines()
    meta = ''
    title = ''
    content = ''

    for i in range(0, len(lines)):
        currentLine = lines[i].rstrip()
        print(currentLine)
        if is_json(currentLine) and currentLine.startswith('{'):
            #
            # output previous
            #
            if len(meta) > 0:
                meta = json.loads(meta)
                #
                # get news from
                #
                try:
                    # 1. 第三個值是文章id編號，因為考慮標題有可能會變動
                    # 2. 第四個值是標題，多雙引號，怕到時有奇怪的符號，電腦會出錯
                    檔名 = '{}／{}／{}／{}／{}／.txt'.format(
                        date.fromtimestamp(
                            int(meta['created_at'])).strftime("%Y-%m-%d"),
                        source對應表[int(meta['source'])],
                        meta['id'],
                        title,
                        meta['last_changed_at'],
                    )
                    with open(join(結果資料夾, 檔名), 'w') as 輸出檔案:
                        print(json.loads(content), file=輸出檔案)
                    break
                except:
                    print(meta)
                    raise
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

#
# read file
#
sourceDir = join(dirname(abspath(__file__)), 'extract')
結果資料夾 = join(dirname(abspath(__file__)), '結果資料夾')
parse(join(sourceDir, '20160201.txt'), 結果資料夾)
