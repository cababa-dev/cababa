import datetime
import pytz

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
from django.db.models import Q

from lib.bot import (
    parse_query,
    Menu, ActionHandler, MenuHandler,
    SimpleMenu, SimpleSelection, SimpleSelectionItem,
)
from reservations.models import Reservation
from reservations.services import ReservationService
from . import models


handler = WebhookHandler(settings.HOSTESS_LINE_CHANNEL_SECRET)
line_bot_api = LineBotApi(settings.HOSTESS_LINE_ACCESS_TOKEN)
line_bot_api_guest = LineBotApi(settings.GUEST_LINE_ACCESS_TOKEN)


"""
リッチメニュー: 出勤可能時間
"""
class AvailableTimeMemu(Menu):
    title = '出勤可能時間'
    name = 'available_time'

    """出勤可能時間の設定メニューを表示
    """
    def main_action(self, event):
        actions = {
            self.action_list_date: '設定済みの出勤時間',
            self.action_new_date: '出勤時間を設定'
        }
        message = SimpleMenu(self, actions=actions)
        return line_bot_api.reply_message(event.reply_token, message)

    """設定済みの出勤時間検索
    """
    def action_list_date(self, event, query): 
        # 本日から1週間で検索
        # 出勤時間を取得
        hostess = self.get_hostess(event)
        now = datetime.datetime.now()
        availables = [a for a in models.AvailableTime.objects.filter(hostess=hostess, start_at__gte=now).order_by('start_at') if not Reservation.objects.filter(time=a).exists()]
        # 出勤時間が無ければエラーメッセージを返す
        if len(availables) == 0:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定されていません'))
        # 日付ごとに分ける
        available_dates = {}
        for available in availables:
            available_dates[available.start_at.day] = available
        answers = [
            SimpleSelectionItem(text=available.start_at.strftime('%Y-%m-%d'), key='day', value=available.start_at.strftime('%Y-%m-%d'))
            for available in available_dates.values()
        ]
        message = SimpleSelection(self, title='どの日付で検索しますか？', action='list_datetime', answers=answers)
        return line_bot_api.reply_message(event.reply_token, message)

    """出勤可能日を選択
    """
    def action_list_datetime(self, event, query):
        # 本日から1週間で検索
        # 出勤時間を取得
        hostess = self.get_hostess(event)
        start_date = make_aware(datetime.datetime.strptime(query['day'], '%Y-%m-%d'))
        end_date = start_date + datetime.timedelta(days=1)
        availables = [a for a in models.AvailableTime.objects.filter(hostess=hostess, start_at__gte=start_date, end_at__lte=end_date).order_by('start_at') if not Reservation.objects.filter(time=a).exists()]
        # カルーセルで表示
        columns = [
            CarouselColumn(
                title=localtime(available.start_at).strftime('%Y-%m-%d'), text='{}-{}'.format(localtime(available.start_at).strftime('%H:%M'), localtime(available.end_at).strftime('%H:%M')), actions=[
                PostbackAction(label='キャンセルする', display_text='キャンセルする', data='menu={}&action=cancel&id={}'.format(self.name, available.available_id))
            ])
            for available in availables
        ]
        message = TemplateSendMessage(alt_text='alt text', template=CarouselTemplate(columns=columns))
        return line_bot_api.reply_message(event.reply_token, message)

    """設定した出勤時間をキャンセルする
    """
    def action_cancel(self, event, query):
        available_id = query.get('id')
        # 出勤可能時間を削除
        models.AvailableTime.objects.get(available_id=available_id).delete()
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='キャンセルしました'))

    """出勤可能日を選択
    """
    def action_new_date(self, event, query):
        # 本日から1週間で検索
        answers = [
            SimpleSelectionItem(text=date_str, key='day', value=date_str)
            for date_str in self.get_weekly()
        ]
        message = SimpleSelection(self, title='どの日付で検索しますか？', action='new_datetime', answers=answers)
        return line_bot_api.reply_message(event.reply_token, message)
    
    """出勤可能日時を選択
    """
    def action_new_datetime(self, event, query):
        day = query.get('day')
        day = datetime.datetime.strptime(day, '%Y-%m-%d')
        # 候補時間一覧
        now = localtime(timezone.now()).replace(year=day.year, month=day.month, day=day.day)
        start_hour = now.replace(hour=settings.BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
        end_hour = now.replace(hour=settings.BUSINESS_END_HOUR, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        diff = end_hour - start_hour
        candidate_hours = [
            (start_hour+datetime.timedelta(hours=i), start_hour+datetime.timedelta(hours=i+1))
            for i in range(diff.seconds//3600)
        ]
        # 設定済みの出勤時間を取得
        hostess = self.get_hostess(event)
        availables = models.AvailableTime.objects.filter(hostess=hostess, start_at__gte=start_hour, end_at__lte=end_hour)
        # 設定済みの出勤時間を候補から削除
        for available in availables:
            candidate_hours = [d for d in candidate_hours if d[0] != available.start_at]
        answers = [
            SimpleSelectionItem(text='{}-{}'.format(d[0].strftime('%H:%M'), d[1].strftime('%H:%M')), key='start_hour', value=d[0].strftime('%Y-%m-%dT%H'))
            for d in candidate_hours
        ]
        message = SimpleSelection(self, title='出勤したい時間を選択してください', action='set_available', answers=answers)
        return line_bot_api.reply_message(event.reply_token, message)
    
    """出勤可能時間を設定
    """
    def action_set_available(self, event, query):
        hostess = self.get_hostess(event)
        start_hour = query.get('start_hour')
        start_hour = make_aware(datetime.datetime.strptime(start_hour, '%Y-%m-%dT%H'))
        end_hour_half = start_hour + datetime.timedelta(minutes=30)
        end_hour = end_hour_half + datetime.timedelta(minutes=30)
        # 出勤可能時間を作成
        available = models.AvailableTime.objects.create(start_at=start_hour, end_at=end_hour_half, hostess=hostess)
        available = models.AvailableTime.objects.create(start_at=end_hour_half, end_at=end_hour, hostess=hostess)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定が完了しました'))
    
    def get_weekly(self):
        now = localtime(timezone.now())
        return [(now + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]


"""
リッチメニュー: 未承認の予約一覧
"""
class UnconfirmReservationMenu(Menu):
    title = '予約一覧'
    name = 'unconfirm_reservations'

    def main_action(self, event):
        hostess = self.get_hostess(event)
        now = datetime.datetime.now()
        reservations = Reservation.objects.filter(time__hostess=hostess, time__start_at__gte=now, is_approval=None)
        # 依頼が無い場合
        if len(reservations) == 0:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='新規予約はありません'))
        # カルーセルで表示
        columns = []
        for reservation in reservations:
            date = "開始{}\n終了{}\n".format(localtime(reservation.time.start_at).strftime('%m-%d %H:%M'), localtime(reservation.time.end_at).strftime('%m-%d %H:%M'))
            column = CarouselColumn(
                title=reservation.guest.display_name,
                text=date,
                actions=[
                    PostbackAction(
                        label='承認',
                        display_text='承認',
                        data='menu=unconfirm_reservations&action=approval&reservation_id={}'.format(reservation.reservation_id)
                    ),
                    PostbackAction(
                        label='拒否',
                        display_text='拒否',
                        data='menu=unconfirm_reservations&action=deny&reservation_id={}'.format(reservation.reservation_id)
                    )
                ]
            )
            columns.append(column)
            
        message = TemplateSendMessage(alt_text='alt text', template=CarouselTemplate(columns=columns))
        return line_bot_api.reply_message(event.reply_token, message)
    
    """予約の通知に対する返答 - 承認
    """
    def action_approval(self, event, query):
        hostess = self.get_hostess(event)
        reservation_id = query.get('reservation_id')
        reservation = Reservation.objects.get(reservation_id=reservation_id)
        if reservation.is_approval is not None:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='すでに返答済みです'))
        reservation.is_approval = True
        reservation.save()
        # 決済を作成
        service = ReservationService()
        transaction = service.create_transaction(reservation)
        # ゲストに通知
        date = "開始{}\n終了{}\n".format(localtime(reservation.time.start_at).strftime('%m-%d %H:00'), localtime(reservation.time.end_at).strftime('%m-%d %H:00'))
        text = "お嬢が予約を承認しました！\n\n【予約情報】\nお嬢おなまえ: {}\n{}\n\n".format(hostess.display_name, date)
        text += "こちらから支払いお願いします\n{}".format(transaction.url)
        line_bot_api_guest.push_message(reservation.guest.line_user_id, TextSendMessage(text=text))
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ゲストに承認通知を送信しました'))
    
    """予約の通知に対する返答 - 拒否
    """
    def action_deny(self, event, query):
        hostess = self.get_hostess(event)
        reservation_id = query.get('reservation_id')
        reservation = Reservation.objects.get(reservation_id=reservation_id)
        if reservation.is_approval is not None:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='すでに返答済みです'))
        reservation.is_approval = False
        reservation.save()
        # ゲストに通知
        date = "開始{}\n終了{}\n".format(localtime(reservation.time.start_at).strftime('%m-%d %H:00'), localtime(reservation.time.end_at).strftime('%m-%d %H:00'))
        text = "お嬢が予約を拒否しました。残念\n\n【予約情報】\nお嬢おなまえ: {}\n{}".format(hostess.display_name, date)
        line_bot_api_guest.push_message(reservation.guest.line_user_id, TextSendMessage(text=text))
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ゲストに承認通知を送信しました'))


"""
リッチメニュー: 確定予約一覧
"""
class ReservationMenu(Menu):
    title = '確定予約一覧'
    name = 'reservations'

    def main_action(self, event):
        pass


"""
リッチメニュー: 出勤可能時間
"""
class SalesMenu(Menu):
    title = '売上一覧'
    name = 'sales'

    def main_action(self, event):
        pass



menu_handler = MenuHandler()
menu_handler.add(AvailableTimeMemu())
menu_handler.add(UnconfirmReservationMenu())
menu_handler.add(ReservationMenu())
menu_handler.add(SalesMenu())


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