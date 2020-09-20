import datetime

import linebot
from linebot import WebhookHandler, LineBotApi
from linebot.models import (
    MessageEvent, PostbackEvent,
    PostbackAction, URIAction, 
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
from lib.date import get_display_dt
from reservations.models import Reservation, LinePayTransaction


handler = WebhookHandler(settings.GUEST_LINE_CHANNEL_SECRET)
line_bot_api = LineBotApi(settings.GUEST_LINE_ACCESS_TOKEN)


"""
リッチメニュー: キャスト予約一覧
"""
class ReservationMenu(Menu):
    title = 'キャスト予約一覧'
    name = 'guest_reservations'

    """予約情報一覧を表示する
    """
    def main_action(self, event):
        guest = self.get_guest(event)
        now = datetime.datetime.now()
        reservations = Reservation.objects.filter(guest=guest, time__start_at__gte=now, is_approval=True)[:5]
        # 予約が無い場合
        if len(reservations) == 0:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='予約はありません'))
        # カルーセルで表示
        columns = []
        for reservation in reservations:
            date = "開始{}\n終了{}\n".format(localtime(get_display_dt(reservation.time.start_at)).strftime('%m-%d %H:%M'), localtime(get_display_dt(reservation.time.end_at)).strftime('%m-%d %H:%M'))
            column = CarouselColumn(
                title=reservation.time.hostess.display_name,
                text=date,
                actions=[
                    URIAction(
                        label='キャスト詳細',
                        uri='https://{}/reservations/hostess/{}'.format(settings.HOST_NAME, reservation.time.hostess.user_id)
                    ),
                ]
            )
            columns.append(column)
            
        message = TemplateSendMessage(alt_text='alt text', template=CarouselTemplate(columns=columns))
        return line_bot_api.reply_message(event.reply_token, message)


"""
リッチメニュー: 領収書
"""
class InvoiceMenu(Menu):
    title = '支払履歴'
    name = 'invoices'

    def main_action(self, event):
        # 支払い履歴を取得
        guest = self.get_guest(event)
        transactions = LinePayTransaction.objects.filter(reservation__guest=guest)[:5]

        if len(transactions) == 0:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='支払履歴はありません'))

        columns = []
        for transaction in transactions:
            title = '{date} {start}-{end} {hostess}'.format(
                date=localtime(get_display_dt(transaction.reservation.time.start_at)).strftime('%m/%d'),
                start=localtime(transaction.reservation.time.start_at).strftime('%H:%M'),
                end=localtime(transaction.reservation.time.end_at).strftime('%H:%M'),
                hostess=transaction.reservation.time.hostess.display_name,
            )
            hourly = settings.BASE_PRICE
            specif = settings.RANK_PRICES[transaction.reservation.time.hostess.hostess_profile.rank]
            total = transaction.amount
            text = f'合計金額:￥{total:,}\n■内訳\nベース料金：￥{hourly:,}, 指名料：￥{specif:,}'
            column = CarouselColumn(
                title=title,
                text=text,
                actions=[
                    URIAction(
                        label='再予約',
                        uri='https://{}/reservations/hostess/{}'.format(settings.HOST_NAME, transaction.reservation.time.hostess.user_id)
                    ),
                ]
            )
            columns.append(column)
            
        message = TemplateSendMessage(alt_text='alt text', template=CarouselTemplate(columns=columns))
        return line_bot_api.reply_message(event.reply_token, message)


        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ご利用履歴一覧を返す'))


guest_menu_handler = MenuHandler()
guest_menu_handler.add(ReservationMenu())
guest_menu_handler.add(InvoiceMenu())


# テキストメッセージに対する反応
# テキストは基本的にリッチメニューのために使用
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # リッチメニュー制御
    text = event.message.text
    menu = guest_menu_handler.search_menu(text)
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