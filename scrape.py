import urllib.request
from bs4 import BeautifulSoup as bs4
import json
import requests

# アクセス先URLを設定
url = 'https://news.yahoo.co.jp/search?ei=utf-8'

# 記事取得関数
def getNews(word):

    #URL生成
    if word != "" :
        mod_url = "{}&p='{}'".format(url, word)
    else:
        mod_url = url

    #パース
    res = requests.get(mod_url)
    
    #スクレイピング
    soup = bs4(res.text,'lxml')
    base = soup.find(class_="newsFeed")
    if base is None:
        return False

    a_elems = base.find_all("a", class_="newsFeed_item_link")
    
    #タイトルとURLをリストに代入、返却
    result = []
    for elem in a_elems:
        item = {}
        href = elem.attrs['href']
        pickup_id = href.replace('https://news.yahoo.co.jp/pickup/', '')
        title = elem.find(class_="newsFeed_item_title").text

        item["pickup_id"] = pickup_id
        item["title"] = title
        result.append(item)
        result.append("\n")
    
    return result
