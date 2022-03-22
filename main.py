from flask import Flask, request, abort
# flask（Webアプリ用のライブラリ）
# request httpリクエストのデータ取得用関数
# abprt http用のExceptionのような関数

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
# 環境変数操作を行うモジュール

import scrape

#Webアプリ作成 
app = Flask(__name__)
 
#環境変数取得
#LINE Developersで設定されている値をを取得、設定
#アクセストークン
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
#Channel Secret
YOUR_CHANNEL_SECRET       = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler      = WebhookHandler(YOUR_CHANNEL_SECRET) 


#Webhookからのリクエスト（スマホ → LineAPI）をチェック
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']
 
    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
 
    # handle webhook body
    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'
 

###############################################
#LINEで入力した検索文字列と、スクレイピング処理
############################################### 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text=event.message.text #検索文字列
    lists=scrape.getNews(text) #スクレイピング
    print(any(lists))
    if any(lists):
        r = []
        limit = 15
        for i in range(limit):
            link  = lists[i]
            title = link["title"]
            url   = link["pickup_id"]
            r.append("{}({})". format(url, title))
    
        result = ', '.join(map(str, r))
        line_bot_api.reply_message(event.reply_token,
            [
                TextSendMessage(text=f"検索ワード「{text}」での検索結果[{limit}]件です！"),
                TextSendMessage(text=result)
            ]
        )

    else:
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage("検索結果がありません。終了します。"))
        return

    
 
#Webアプリ実行
if __name__ == "__main__":
    #ポート番号の設定
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)