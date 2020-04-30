import datetime

import linebot
from linebot import WebhookHandler, LineBotApi
from linebot.models import (
    MessageEvent, PostbackEvent,
    PostbackAction,
    TextMessage, TextSendMessage, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, CarouselColumn, QuickReply, QuickReplyButton,
)

from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware, localtime

from lib.bot import (
    parse_query,
    Menu, ActionHandler, MenuHandler,
    SimpleMenu, SimpleSelection, SimpleSelectionItem,
)


handler = WebhookHandler(settings.GUEST_LINE_CHANNEL_SECRET)
line_bot_api = LineBotApi(settings.GUEST_LINE_ACCESS_TOKEN)


"""
リッチメニュー: 予約一覧
"""
class ReservationMenu(Menu):
    title = '予約一覧'
    name = 'reservations'

    """予約メニューを表示
    """
    def main_action(self, event):
        actions = {
            self.action_list_date: '設定済みの出勤時間',
            self.action_new_date: '出勤時間を設定'
        }
        message = SimpleMenu(self, actions=actions)
        return line_bot_api.reply_message(event.reply_token, message)


"""
リッチメニュー: 領収書
"""
class InvoiceMenu(Menu):
    title = '領収書'
    name = 'invoices'

    def main_action(self, event):
        pass


menu_handler = MenuHandler()
menu_handler.add(ReservationMenu())
menu_handler.add(InvoiceMenu())


# テキストメッセージに対する反応
# テキストは基本的にリッチメニューのために使用
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # リッチメニュー制御
    text = event.message.text
    menu = menu_handler.search_menu(text)
    if menu:
        return menu.main_action(event)

# ポストバックアクションに対する反応
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    postback_msg = event.postback.data
    query = parse_query(postback_msg)

    # ポストバック内のクエリーから呼び出す関数を制御
    menu_name = query.pop('menu')
    action_name = query.pop('action')

    menu = menu_handler.get_menu(menu_name)
    if not menu:
        return
    action = menu.search_action(action_name)
    if not action:
        return
    action(event, query)