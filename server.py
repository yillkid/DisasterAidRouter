import requests
import json
from linebot.models import *
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from datetime import datetime
import math
from config import *

# Secret data
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api.push_message(USER_ID, TextSendMessage(text='歡迎使用，不會使用請打?符號'))

# Test data
TEST_DATA = [
    ["測試用", "虛擬避難所", 50.98186702918472, 50.68693773834926],
    ["玉峰里", "草屯國小避難所", 23.98186702918472, 120.68693773834926],
    ["炎峰里", "草屯國中避難所", 23.977475429532966, 120.68562248522376],
    ["和平里", "聯合里辦公室避難所", 23.979316821694304, 120.686872162827],
    ["敦和里", "敦和宮避難所", 23.980704713191532, 120.68116100475969],
    ["山腳里", "虎山國小避難所", 23.96353758850045, 120.68561323795751],
    ["富寮里", "富功國小避難所", 23.979699007238064, 120.70253418258714],
    ["御史里", "里集會所", 23.990331601260195, 120.68939940556267],
    ["新豐里", "社區活動中心", 24.000088263552275, 120.67564748677192],
    ["碧峰里", "里集會所", 23.97373258659279, 120.66376344498585],
    ["碧洲里", "里活動中心", 23.958866939556863, 120.66280629031954],
    ["復興里", "復興托兒所", 23.969888920811595, 120.66816912457305],
    ["上林里", "老人活動中心", 23.96906234216036, 120.67649476865779],
    ["新庄里", "新庄國小避難所", 23.9951555613731, 120.66900210333738],
    ["北投里", "朝陽宮避難所", 23.983772399028243, 120.66475916636642],
    ["石川里", "里集會所", 23.993943805452602, 120.64977577937871],
    ["加老里", "加興宮避難所", 23.998877866880658, 120.6558947861392],
    ["北勢里", "永安宮避難所", 23.983888348693487, 120.7447423995719],
    ["中原里", "中原國小避難所", 23.98526834158108, 120.72089941508128],
    ["南埔里", "里活動中心", 23.979024003390577, 120.72634514570568],
    ["土城里", "土城國小避難所", 23.98458021529031, 120.74377247011675],
    ["坪頂里", "坪頂國小避難中心", 23.967147445014955, 120.74016287861637],
    ["雙冬里", "紫雲宮避難所", 23.98280446363764, 120.79164420504064],
    ["平林里", "坪林國小避難所", 23.992224067141343, 120.76364579857126],
    ["中正里", "草屯國小避難所", 23.98162714908302, 120.68598627342858],
    ["中山里", "聯合里辦公室避難所", 23.97996303696292, 120.68655006547186],
    ["明正里", "草屯國小避難所", 23.981686272471933, 120.68769592661184],
    ["新厝里", "太清宮地下室避難所", 23.972332608322333, 120.68399187547817],
    ["敦和里", "敦和國小避難所", 23.98195783153191, 120.67855438461241],
    ["富寮里", "里集會所", 23.975287132201945, 120.70368338133578],
    ["北投里", "集仙宮避難所", 23.987718829705848, 120.6630911180865],
    ["加老里", "里集會所", 24.001655790484797, 120.65647935493209],
    ["北勢里", "龍泉宮避難所", 23.99279831236083, 120.74333063002337],
    ["中原里", "永和宮避難所", 23.98781341397663, 120.71852975583413],
    ["南埔里", "將軍廟避難所", 23.97889822174204, 120.71814748774902],
    ["坪頂里", "社區活動中心避難所", 23.968833809420683, 120.74589865403094],
    ["雙冬里", "雙冬國小避難所", 23.984645950347215, 120.79644786641342],
    ["桃米里", "里集會所", 23.944033533567122, 120.93007843034404]
]

url_weather_open_data = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=' + WEATHER_STATION_API_KEY

app = Flask(__name__)

def get_earthquake():
    data = requests.get(url_weather_open_data)
    data_json = data.json()

    return json.dumps(data_json, ensure_ascii=False)

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
def haversine_distance(lat1, lon1, lat2, lon2):
    # 將經緯度轉換為弧度喔
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius = 6371.0   # 地球半徑（單位：公里）
    distance = radius * c  # 計算距離
    return distance

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
       if event.message.text == '?':
          reply_text = "請按左下角加號，傳遞您的位置資訊給我，搜尋距離你最近的避難所。並依交通資訊趕快前往避難。\n\n"
          reply_text += "輸入 x，代表你已放棄求生，系統也會給您適當建議。\n\n"
          reply_text += "輸入 egg，會有小驚喜。\n\n"
          reply_text += "注意，我不是聊天機器人，輸入無關的訊息，我無法回應你喔！Sorry..."
          line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
       elif event.message.text == 'ek':
          reply_text = "警訊通知\n"
          reply_text += "[地震報告]"
          reply_text += datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          reply_text +="南投縣草屯鎮市區發生規模6.2有感地震，預估震度在5級以上，詳細資訊請參考氣象局網站，氣象局。\n"
          line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
       elif event.message.text == 'x':
          image_url = "https://r10.ntct.edu.tw/var/file/10/1010/img/4840/462050309.jpg"
          line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='確定不躲嗎?'),ImageSendMessage(original_content_url=image_url, preview_image_url=image_url),TextSendMessage(text='搏君一笑，請勿見怪..^^')])
       elif event.message.text == 'egg':
          image_url = "https://r10.ntct.edu.tw/var/file/10/1010/img/4840/373943184.jpg"
          line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='謝謝加入好友，希望我們的系統對你有幫助，願世界一切平安。'),ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)])
       elif event.message.text == 'id':
          reply_text = "你的ID\n"
          reply_text +=event.source.user_id
          line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
       elif event.message.text == 'qq':
          line_bot_api.reply_message(event.reply_token, TextSendMessage(text=get_earthquake()))
   ##    elif  "IFTTT" in event.message.text :
   ##       reply_text = "notify說地震來了\n"
   ##       line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    # 將GPS資訊以變數記錄起來
    latitude = event.message.latitude
    longitude = event.message.longitude

    min_value = 1000
    min_index = -1

    # 使用 for 迴圈找出最小值及其索引
    for i in range(38):
        Real_distance = haversine_distance(data[i][2], data[i][3],latitude, longitude)
        if Real_distance < min_value:
             min_value = Real_distance
             min_index = i

    image_url = "https://r10.ntct.edu.tw/var/file/10/1010/img/4840/"+str(min_index)+".jpg"  # 替換為實際的URL
    # 回傳給使用者
    reply_message = f"南投縣草屯鎮轄內\n {TEST_DATA[min_index][0]} 的 {TEST_DATA[min_index][1]} \n距離你的位置 {round(min_value*1000, 3)} 公尺，\n是距離你最近的避難場所，\n請盡速前往。\n\n避難所政府公開資料如下：\n點開圖可以放大。"
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply_message),ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)])

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
