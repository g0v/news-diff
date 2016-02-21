import urllib
import re
from parallel_sync import wget
from os.path import abspath, dirname, join
#
# parse html
#
link = "http://ronnywang-newsdiff.s3-website-ap-northeast-1.amazonaws.com/2016/"
fp = urllib.urlopen(link)
myHTML = fp.read()

matches = re.findall('<a href="201602([^\"]+)">', myHTML, re.DOTALL)
#print(matches)

# 
# download
#
prefix = 'http://ronnywang-newsdiff.s3-website-ap-northeast-1.amazonaws.com/2016/201602'
downList = [ prefix + x  for x in matches]
#print(downList)
targetPath = join(dirname(abspath(__file__)),'extract')
wget.download(targetPath, downList, extract=True)
