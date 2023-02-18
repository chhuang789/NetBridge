# This is the main.py for flex with line bot api
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

import logging.config
from NetBridgeRMAApi.rmaapi import RMAApi

app = Flask(__name__)

line_bot_api = LineBotApi('LineBotApi')
handler = WebhookHandler('WebhookHandler')

# create logger
if not os.path.exists("log"):
    os.makedirs("log")
# Load logging.conf
logging.config.fileConfig('logging.conf')
console_handler = logging.StreamHandler()
logger = logging.getLogger('NetBridgeRMA')

def isValidSN(strSN):
    if len(strSN) != 13:
        return 3  # 長度需為13碼
    for ch in strSN:
        if not (ord(ch) in range(97, 122) or ord(ch) in range(65, 90) or ch.isdigit()):
            if ch.isspace():
                return 1  # 序號有空白
            else:
                return 2  # 序號不為英數字
    return 0

@app.route("/callback", methods=['POST'])
def callback():
        logger.debug("/callback")
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: %s", body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    strSN = event.message.text
    status = isValidSN(strSN)
    logger.info("SN=%s status=%d", strSN.replace('\n',' '), status)
    strReply = None
    strRootUrl = request.url_root
    logger.debug("root url=%s", strRootUrl)
    if strSN.lower().find("profile") >= 0:
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Your ID: ' + profile.user_id),
                    TextSendMessage(text='Status message: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif strSN.lower().find("emoji") >= 0:
        emojis = [
            {
                "index": 0,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "001"
            },
            {
                "index": 13,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "002"
            }
        ]
        text_message = TextSendMessage(text='$ LINE emoji $', emojis=emojis)
        line_bot_api.reply_message(
            event.reply_token, [
                text_message
            ]
        )
    elif strSN.lower().find('qc') >= 0:
        quota_consumption = line_bot_api.get_message_quota_consumption()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
            ]
        )
    elif strSN.lower().find('push') >= 0:
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text='PUSH!'),
            ]
        )
    elif strSN.lower().find('btn') >= 0:
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif strSN.lower().find('cc1') >= 0:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif strSN.lower().find('cc2') >= 0:
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://netbridge.ciot.work/static/images/netbridge_2021.png',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(image_url='https://netbridge.ciot.work/static/images/netbridge_2021.png',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif strSN.lower().find('quota') >= 0:
        quota = line_bot_api.get_message_quota()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='type: ' + quota.type),
                TextSendMessage(text='value: ' + str(quota.value))
            ]
        )
    elif strSN.find("照片") >= 0:
        strUrl = strRootUrl + '/static/images/netbridge_2021.png'
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url = strUrl, preview_image_url = strUrl))
    elif strSN.find("影片") >= 0:
        strUrl = strRootUrl + '/static/videos/netbridge_orbi.mp4'
        strUrlPreview = strRootUrl + '/static/images/netbridge_orbi.png'
        line_bot_api.reply_message(event.reply_token, VideoSendMessage(original_content_url = strUrl, preview_image_url = strUrlPreview))
    elif strSN.find("貼圖") >= 0:
        line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id = '446', sticker_id = '1988'))
    elif strSN.find("音檔") >= 0:
        strUrl = strRootUrl + '/static/audios/netbridge_eric.mp3'
        line_bot_api.reply_message(event.reply_token, AudioSendMessage(original_content_url = strUrl, duration=60000))
    elif strSN.find("住址") >= 0 or strSN.find("地址") >= 0:
        line_bot_api.reply_message(event.reply_token, LocationSendMessage(title='瀚錸科技', address='台北市信義區信義路五段5號', latitude = 25.030148, longitude = 121.562496))
    elif strSN.find("秘密") >= 0:
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='歡迎來到瀚錸科技', actions=[
                URIAction(label='瀚錸科技網站', uri='https://www.netgearstore.com.tw/'),
                URIAction(label='全球最好的交換器', uri='https://www.netbridgetech.com.tw/netgear-business/'),
                URIAction(label='Orbi帶來新的網路體驗', uri='https://www.netbridgetech.com.tw/orbi/'),
                URIAction(label='台灣網路旗艦店', uri='https://www.netgearstore.com.tw/')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif strSN.find("投票") >= 0:
        confirm_template = ConfirmTemplate(text='你覺得瀚錸是個好公司嗎?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif strSN.find("請回覆維修產品的序號") < 0:
        if status > 0:
            strReply = "請回覆維修產品的序號\n序號為英文字母及數字組合\n長度為13碼\n中間不能有空格"
        else:
            try:
                myRMAApi = RMAApi(logger)
                status, json_workers = myRMAApi.getRMAStats(
                    strSN.upper())
                logger.debug("HTTP Response code =%s", status)
                #logger.debug("HTTP response json=%s", str(json_workers))
                if status == 200:
                    strReply = "SN=" + json_workers[0]['Serial'] + "\nStatus=" + \
                        json_workers[0]['Status'] + "\nRO=" + \
                        json_workers[0]['Repair_Order']
                elif status == 404:
                    strReply = json_workers['Status']
                else:
                    strReply = "系統忙碌中，請稍後再試"
            except Exception as e:
                logger.error(str(e))
                strReply = "系統忙碌中，請稍後再試 " + str(e)
        logger.info("Reply '%s'", strReply.replace('\n',' '))
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(text=strReply)
        )
    else:
        logger.debug("可能是使用圖文選單")
    #message = TextSendMessage(text=event.message.text)
    #line_bot_api.reply_message(event.reply_token, message)

@app.route("/hello/")
def helloCH():
    logger.debug("request /hello/")
    return "Hello C.H. Huang!"

@app.route("/")
def hello():
    logger.debug("request /")
    return "Hello Flask!"

@app.errorhandler(404)
def page_not_found(error):
    return 'This route does not exist {}'.format(request.url), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
