import json
import xlrd
from linebot.models import TextSendMessage, PostbackAction, TemplateSendMessage, ButtonsTemplate
from zoomus import ZoomClient

from django.db.models import Q
from django.utils.timezone import localtime
from django.conf import settings

from lib import line, zoom
from . import models


class ReservationService:
    def send_notification(self, reservation):
        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        hostess_name = reservation.time.hostess.display_name
        date = "開始{}\n終了{}\n".format(localtime(reservation.time.start_at).strftime('%m-%d %H:%M'), localtime(reservation.time.end_at).strftime('%m-%d %H:%M'))
        text = "予約が完了しました！\n\n【予約情報】\nお嬢おなまえ: {}\n{}".format(hostess_name, date)
        line_bot_api.push_message(reservation.guest.line_user_id, TextSendMessage(text=text))

        # お嬢に通知
        line_bot_api = line.get_line_bot_api(is_guest=False)
        actions = [
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
        text = '{}\nおなまえ: {}'.format(date, reservation.guest.display_name)
        buttons = ButtonsTemplate(text=text, title='新規予約が入りました', actions=actions)
        message = TemplateSendMessage(alt_text='alt text', template=buttons)
        line_bot_api.push_message(reservation.time.hostess.line_user_id, message)

    def create_transaction(self, reservation):
        resp = line.pay_request(reservation)
        transaction = models.LinePayTransaction.objects.create(
            return_code=resp['return_code'],
            return_message=resp['return_message'],
            transaction_id=resp['transaction_id'],
            access_token=resp['access_token'],
            url=resp['url']['web'],
            reservation=reservation
        )
        return transaction
    
    def create_meeting(self, reservation):
        # 1. 同じ時刻に使用されていないZOOMアカウントを探す
        start_at = reservation.time.start_at
        end_at = reservation.time.end_at
        # クエリに該当するものは、同じ時刻に被ることの無いルーム
        query = Q(start_at__gte=end_at) # 本ルームの終了時刻の後に開始されるルーム
        query = query | Q(end_at__lte=start_at) # 本ルームの開始時刻より前に終了するルーム
        # 逆に同じ時刻に被るルームを検索
        concurrent_meetings = models.ZoomMeeting.objects.filter(~query)
        # ルームに該当するミーティングIDを取得
        unusable_accounts = [meeting.account.api_key for meeting in concurrent_meetings if meeting.account]
        # 使用可能なアカウントを探す
        query = Q(api_key__in=unusable_accounts)
        usable_account = models.ZoomAccount.objects.filter(~query).first()
        
        # もし使用可能なアカウントが無い場合はエラーを返す
        if not usable_account:
            raise ValueError('使用可能なZOOMアカウントが見つかりませんでした')

        # 使用可能なアカウントを使ってZOOMのクライアントを作成
        client = ZoomClient(usable_account.api_key, usable_account.api_secret)

        # 2. ZOOMのルームを作成する
        room_settings = dict(
            host_video=False,
            join_before_host=True,
            participant_video=True,
            approval_type=0,
            waiting_room=False,
        )
        request_params = dict(
            # type=1, # 1: instant meeting, 2: scheduled meeting
            start_time=reservation.time.start_at,
            timezone=settings.TIME_ZONE,
            duration=(reservation.time.end_at - reservation.time.start_at).seconds, # [sec]
            user_id=usable_account.admin_email,
            settings=room_settings
        )
        response = client.meeting.create(**request_params)
        data = response.json()
        print(data)
        meeting_id = data['id']
        join_url = data['join_url']
        start_url = data['start_url']
        zoom_meeting_id = data['id']
        password = data['password']
        context = json.dumps(data)
        meeting = models.ZoomMeeting.objects.create(
            meeting_id=meeting_id,
            join_url=join_url,
            start_url=start_url,
            password=password,
            zoom_meeting_id=zoom_meeting_id,
            reservation=reservation,
            context=context,
            account=usable_account,
            start_at=reservation.time.start_at,
            end_at=reservation.time.end_at,
        )
        return meeting

    def send_meeting(self, meeting):
        join_text = "ZOOM参加のURLはこちら\n\n{}".format(meeting.join_url)
        password_text = meeting.password
        password_help_text = "↑パスワードはこちら"

        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        line_bot_api.push_message(meeting.reservation.guest.line_user_id, TextSendMessage(text=join_text))
        line_bot_api.push_message(meeting.reservation.guest.line_user_id, TextSendMessage(text=password_text))
        line_bot_api.push_message(meeting.reservation.guest.line_user_id, TextSendMessage(text=password_help_text))

        # お嬢に通知
        line_bot_api = line.get_line_bot_api(is_guest=False)
        line_bot_api.push_message(meeting.reservation.time.hostess.line_user_id, TextSendMessage(text=join_text))
        line_bot_api.push_message(meeting.reservation.time.hostess.line_user_id, TextSendMessage(text=password_text))
        line_bot_api.push_message(meeting.reservation.time.hostess.line_user_id, TextSendMessage(text=password_help_text))


class ZoomService:
    def import_accounts(self, filepath):
        wb = xlrd.open_workbook(filepath)
        sheet = wb.sheet_by_name('ZOOMアカウント')
        tag_groups = dict()
        # ignore header
        for row in range(1, sheet.nrows):
            cols = sheet.row_values(row)
            
            api_key = cols[13]
            zoom_account, created = models.ZoomAccount.objects.get_or_create(api_key=api_key)
            
            zoom_account.admin_email = cols[12]
            zoom_account.api_secret = cols[14]
            zoom_account.api_imchat_history_token = cols[15]

            zoom_account.save()
            