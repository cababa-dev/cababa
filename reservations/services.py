from linebot.models import TextSendMessage, PostbackAction, TemplateSendMessage, ButtonsTemplate

from django.conf import settings

from lib import line, zoom
from . import models


class ReservationService:
    def send_notification(self, reservation):
        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        hostess_name = reservation.time.hostess.display_name
        date = "開始{}\n終了{}\n".format(reservation.time.start_at.strftime('%m-%d %H:00'), reservation.time.end_at.strftime('%m-%d %H:00'))
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
        print(resp)
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
        client = zoom.get_client()
        request_params = dict(
            start_time=reservation.time.start_at,
            timezone=settings.TIME_ZONE,
            duration=(reservation.time.end_at - reservation.time.start_at).seconds, # [sec]
            user_id="u651601f@gmail.com",
            settings=dict(join_before_host=True, participant_video=True)
        )
        response = client.meeting.create(**request_params)
        data = response.json()
        meeting_id = data['id']
        join_url = data['join_url']
        start_url = data['start_url']
        meeting = models.ZoomMeeting.objects.create(
            meeting_id=meeting_id,
            join_url=join_url,
            start_url=start_url,
            reservation=reservation,
        )
        return meeting

    def send_meeting(self, meeting):
        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        text = "ZOOM参加のURLはこちら\n\n{}".format(meeting.join_url)
        line_bot_api.push_message(meeting.reservation.guest.line_user_id, TextSendMessage(text=text))

        # お嬢に通知
        line_bot_api = line.get_line_bot_api(is_guest=False)
        text = "ZOOM参加のURLはこちら\n\n{}".format(meeting.join_url)
        line_bot_api.push_message(meeting.reservation.time.hostess.line_user_id, TextSendMessage(text=text))