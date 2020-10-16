import json
import xlrd
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, PostbackAction, TemplateSendMessage, ButtonsTemplate
from zoomus import ZoomClient

from django.db.models import Q
from django.utils.timezone import localtime
from django.conf import settings

from lib import line, zoom
from lib.date import get_display_dt
from . import models


class ReservationService:
    def send_notification(self, reservation):
        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        hostess_name = reservation.time.hostess.display_name
        date = "開始{}\n終了{}\n".format(localtime(get_display_dt(reservation.time.start_at)).strftime('%m-%d %H:%M'), localtime(get_display_dt(reservation.time.end_at)).strftime('%m-%d %H:%M'))
        text = "予約が完了しました！\n\n【予約情報】\nキャストおなまえ: {}\n{}".format(hostess_name, date)
        line_bot_api.push_message(reservation.guest.line_user_id, TextSendMessage(text=text))

        # キャストに通知
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

    def get_pay_amount(self, reservation):
        # テスト用に1円決済
        # amount = 1
        # 本番はランクに合わせて金額設定
        rank_price = settings.RANK_PRICES[reservation.time.hostess.hostess_profile.rank]
        amount = settings.BASE_PRICE + rank_price
        amount = int(amount / 100)
        return amount

    def create_transaction(self, reservation):
        resp = line.pay_request(reservation)
        transaction = models.LinePayTransaction.objects.create(
            return_code=resp['return_code'],
            return_message=resp['return_message'],
            transaction_id=resp['transaction_id'],
            access_token=resp['access_token'],
            url=resp['url']['web'],
            amount=self.get_pay_amount(reservation),
            reservation=reservation
        )
        return transaction
    
    def resend_pay_notification(self, transaction):
        line_bot_api_guest = LineBotApi(settings.GUEST_LINE_ACCESS_TOKEN)
        date = "開始{}\n終了{}\n".format(localtime(get_display_dt(transaction.reservation.time.start_at)).strftime('%m-%d %H:%M'), localtime(get_display_dt(transaction.reservation.time.end_at)).strftime('%m-%d %H:%M'))
        text = "【予約情報】\nキャストおなまえ: {}\n{}\n\n".format(transaction.reservation.time.hostess.display_name, date)
        text += "こちらから支払いお願いします。一度キャンセルすると支払いが出来なくなりますのでお気をつけください！\n{}\n\n請求元は「株式会社ニューエース」と表示されます".format(transaction.url)
        line_bot_api_guest.push_message(transaction.reservation.guest.line_user_id, TextSendMessage(text=text))
    
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

    def splitper(self, s, n=4):
        s = str(s)
        assert n > 0
        d, m = divmod(len(s), n)
        l = []
        if m:
            l.append(s[:m])
        for i in range(d):
            a = i * n + m
            l.append(s[a:a+n])
        return " ".join(l)

    def send_howto(self, line_bot_api, user_id):
        text = "LINEの画面からZOOMに入室できない場合は以下の2つの方法を試してみて下さい。"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        text = "＜１つ目の方法＞\n"
        text += "画面中央部の【ミーティングを起動】をクリックしてください。"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        image_url = "https://assets.st-note.com/production/uploads/images/33218618/picture_pc_fa1ab7ef7f643325cee03c3f10bda021.png"
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        text = "＜２つ目の方法＞\n"
        text += "【リンクをコピー】をクリックして、「Googlechrome」や「Safari」等のブラウザを開きアドレスバーに貼り付けてください。"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        image_url = "https://assets.st-note.com/production/uploads/images/36154103/picture_pc_a383481369ec6075541ead5d4c673b58.png"
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        text = "【ビデオ付きで参加】をクリックしてください。"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        image_url = "https://assets.st-note.com/production/uploads/images/33218255/picture_pc_fc99dbb0c88da9130cbdc4d8b6313256.jpg"
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        text = "音声が聞こえない時や、映像が映らないときは、【ミュートを解除】【ビデオの開始】の療法が解除されているかご確認ください。\n"
        text += "以下の左図のように赤い斜め線が入っている場合は解除されていません。右図のように【ミュート】【ビデオの停止】という表記になっている状態が正しい状態です。"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        image_url = "https://assets.st-note.com/production/uploads/images/33218444/picture_pc_004f012e97a102995359ef7c2fce5f64.png"
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        text = "【バーチャル背景機能について】※モバイル・タブレットからの場合\n"
        text += "自宅から参加する時や背景を隠したい時等は以下からバーチャル背景の機能を参考にしてみてください。\n"
        text += "\n"
        text += "①左図：右下の詳細（3つの点）をクリックしてください\n"
        text += "②中央図：バーチャル背景をクリックしてください\n"
        text += "③右図：写真を選択してください（+ボタンで自分だけの写真を背景にすることも可能です）"
        line_bot_api.push_message(user_id, TextSendMessage(text=text))

        image_url = "https://assets.st-note.com/production/uploads/images/33701824/picture_pc_98cb818f1ab2bfcbe3160e230c684f49.png"
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))


    def send_meeting(self, meeting):
        text = "ゲストの支払いが完了し、予約が確定しました！\n"
        text += "なまえ: {}\n".format(meeting.reservation.guest.display_name)
        text += "日付: {}\n".format(get_display_dt(meeting.reservation.time.start_at).strftime('%Y-%m-%d'))
        text += "時間: {}-{}\n".format(localtime(meeting.reservation.time.start_at).strftime('%H:%M'), localtime(meeting.reservation.time.end_at).strftime('%H:%M'))
        text += "\n"
        text += "時間になりましたら、ZOOMを立ち上げて\n"
        text += "こちらの情報からアクセスしてください\n"
        text += "\n"
        text += "{}\n".format(meeting.join_url)
        text += "\n"
        text += "ミーティングID: {}\n".format(self.splitper(meeting.zoom_meeting_id))
        text += "パスワード: {}\n".format(meeting.password)
        # text += "\n"
        # text += "音声/映像にトラブルがある場合は以下をご覧ください。\n"
        # text += "https://note.com/cababa/n/n150b47c0db09\n"
        # text += "\n"
        text += "※始める前にこちらをご覧ください※\n"
        text += "\n"
        text += "服装、迷惑行為等基本的なことをまとめています。\n"
        text += "https://note.com/cababa/n/n00540a1c02c7"

        # キャストに通知
        line_bot_api = line.get_line_bot_api(is_guest=False)
        line_bot_api.push_message(meeting.reservation.time.hostess.line_user_id, TextSendMessage(text=text))
        # noteの代わりにトラブル対応方法を送信
        self.send_howto(line_bot_api, meeting.reservation.time.hostess.line_user_id)

        text = "支払いが完了し、予約が確定しました！\n"
        text += "キャスト名: {}\n".format(meeting.reservation.time.hostess.display_name)
        text += "日付: {}\n".format(get_display_dt(meeting.reservation.time.start_at).strftime('%Y-%m-%d'))
        text += "時間: {}-{}\n".format(localtime(meeting.reservation.time.start_at).strftime('%H:%M'), localtime(meeting.reservation.time.end_at).strftime('%H:%M'))
        text += "\n"
        text += "ZOOM参加のURLは以下です。\n"
        text += "時間になりましたら、以下のの情報からアクセスしてください\n"
        text += "\n"
        text += "{}\n".format(meeting.join_url) 
        text += "\n"
        text += "ミーティングID: {}\n".format(self.splitper(meeting.zoom_meeting_id))
        text += "パスワード: {}\n".format(meeting.password)
        # text += "\n"
        # text += "音声/映像にトラブルがある場合は以下をご覧ください。\n"
        # text += "https://note.com/cababa/n/n150b47c0db09\n"
        # text += "\n"
        text += "※始める前にこちらをご覧ください※\n"
        text += "\n"
        text += "服装、迷惑行為等基本的なことをまとめています。\n"
        text += "https://note.com/cababa/n/n00540a1c02c7"

        # ゲストに通知
        line_bot_api = line.get_line_bot_api(is_guest=True)
        line_bot_api.push_message(meeting.reservation.guest.line_user_id, TextSendMessage(text=text))
        # noteの代わりにトラブル対応方法を送信
        self.send_howto(line_bot_api, meeting.reservation.time.hostess.line_user_id)


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
            