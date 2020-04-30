import json
import urllib.parse

import jwt
import requests
import linebot
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage,
)
from linepay import LinePayApi

from django.urls import reverse
from django.conf import settings


# LINEログインページへのURLを作成
def login_url(request, is_guest=True, context={}):
    if is_guest:
        client_id = settings.GUEST_LINE_CLIENT_ID
        client_secret = settings.GUEST_LINE_CLIENT_SECRET
        redirect_uri = 'https://{}{}'.format(settings.HOST_NAME, reverse('guest:login_callback'))
        context['type'] = 'guest'
    else:
        client_id = settings.HOSTESS_LINE_CLIENT_ID
        client_secret = settings.HOSTESS_LINE_CLIENT_SECRET
        redirect_uri = 'https://{}{}'.format(settings.HOST_NAME, reverse('hostess:login_callback'))
        context['type'] = 'hostess'
    base_url = 'https://access.line.me/oauth2/v2.1/authorize'
    params = dict(
        response_type = 'code',
        client_id = client_id,
        redirect_uri = redirect_uri,
        state = json.dumps(context),
        scope = 'openid profile',
        bot_prompt = 'aggressive',
    )
    url = base_url + '?' + urllib.parse.urlencode(params)
    return url

# LINEログイン時に取得されるコードからユーザー情報を取得
def get_id_token(request, request_code, is_guest=True):
    uri_access_token = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if is_guest:
        client_id = settings.GUEST_LINE_CLIENT_ID
        client_secret = settings.GUEST_LINE_CLIENT_SECRET
        redirect_uri = 'https://{}{}'.format(settings.HOST_NAME, reverse('guest:login_callback'))
    else:
        client_id = settings.HOSTESS_LINE_CLIENT_ID
        client_secret = settings.HOSTESS_LINE_CLIENT_SECRET
        redirect_uri = 'https://{}{}'.format(settings.HOST_NAME, reverse('hostess:login_callback'))
    data = {
        "grant_type": "authorization_code",
        "code": request_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    # JWTトークン取得
    resp = requests.post(uri_access_token, headers=headers, data=data)
    line_id_token = resp.json().get('id_token')
    # トークンの取得に失敗した場合
    if not line_id_token:
        raise ValueError
    # JWTのペイロードからユーザー情報を取得
    payload = parse_id_token(line_id_token, is_guest=is_guest)
    return line_id_token, payload


def parse_id_token(id_token, is_guest=True):
    if is_guest:
        client_id = settings.GUEST_LINE_CLIENT_ID
        client_secret = settings.GUEST_LINE_CLIENT_SECRET
    else:
        client_id = settings.HOSTESS_LINE_CLIENT_ID
        client_secret = settings.HOSTESS_LINE_CLIENT_SECRET
    payload = jwt.decode(id_token, client_secret, audience=client_id, issuer='https://access.line.me', algorithms=['HS256'], verify=False)
    return payload

def get_line_bot_api(is_guest=True):
    if is_guest:
        acccess_token = settings.GUEST_LINE_ACCESS_TOKEN
    else:
        acccess_token = settings.HOSTESS_LINE_ACCESS_TOKEN
    line_bot_api = LineBotApi(acccess_token)
    return line_bot_api


def registered_line_at(id_token, is_guest=True):
    profile = parse_id_token(id_token, is_guest=is_guest)
    line_user_id = profile.get('sub')
    # LINE@に登録済みかどうかチェック
    line_bot_api = get_line_bot_api(is_guest=is_guest)
    try:
        profile = line_bot_api.get_profile(line_user_id)
    except linebot.exceptions.LineBotApiError:
        return False
    return True

def send_welcome(line_user_id, is_guest=True):
    line_bot_api = get_line_bot_api(is_guest=is_guest)
    if is_guest:
        line_bot_api.push_message(line_user_id, TextSendMessage(text=f"CABABAへようこそ！😁\n\n"f"女の子からの通知をお待ちください！"))
    else:
        line_bot_api.push_message(line_user_id, TextSendMessage(text=f"CABABAへようこそ！😁\n\n"f"下のメニューから、出勤可能な時間を選択してください！"))


def get_line_pay_api():
    LINE_PAY_CHANNEL_ID = settings.LINE_PAY_CHANNEL_ID
    LINE_PAY_CHANNEL_SECRET = settings.LINE_PAY_CHANNEL_SECRET
    api = LinePayApi(LINE_PAY_CHANNEL_ID, LINE_PAY_CHANNEL_SECRET, is_sandbox=False)
    return api


def pay_request(reservation):
    api = get_line_pay_api()
    LINE_PAY_REQEST_BASE_URL = "https://{}".format(settings.HOST_NAME)
    hostess = reservation.time.hostess
    amount = 1
    currency = 'JPY'
    request_options = {
		"amount": amount,
		"currency": currency,
		"orderId": str(reservation.reservation_id),
		"packages": [
			{
				"id": str(reservation.reservation_id),
				"amount": amount,
				"name": "お嬢予約",
				"products": [
					{
						"id": str(reservation.reservation_id),
						"name": hostess.display_name,
						"imageUrl": hostess.hostess_profile.image,
						"quantity": 1,
						"price": amount
					}
				]
			}
		],
		"options": {
			"payment": {
				"capture": True
			}
		},
		"redirectUrls": {
			"confirmUrl": LINE_PAY_REQEST_BASE_URL + reverse('reservations:pay_authorize', kwargs=dict(reservation_id=str(reservation.reservation_id))),
			"cancelUrl": LINE_PAY_REQEST_BASE_URL + reverse('reservations:pay_cancel', kwargs=dict(reservation_id=str(reservation.reservation_id)))
		}
	}
    response = api.request(request_options)
    return_code = response.get('returnCode')
    return_message = response.get('returnMessage')
    info = response.get('info', {})
    transaction_id = info.get('transactionId')
    access_token = info.get('paymentAccessToken')
    url = info.get('paymentUrl')
    return dict(
        return_code=return_code,
        return_message=return_message,
        transaction_id=transaction_id,
        access_token=access_token,
        url=url,
        amount=amount,
        currency=currency,
    )


def pay_confirm(transaction):
    api = get_line_pay_api()
    response = api.confirm(
		transaction.transaction_id,
        transaction.amount, 
		transaction.currency,
	)
    return response