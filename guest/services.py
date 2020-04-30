import json

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login

from lib import line
from users.models import User, HostessProfile, GuestProfile
from . import bot


class LineLoginService:
    def __init__(self, request):
        self.request = request

    # LINEログインページへのURLを作成
    def login_url(self):
        redirect_to = self.request.GET.get('redirect_to')
        context = {}
        if redirect_to:
            context = dict(redirect_to=redirect_to)
        url = line.login_url(self.request, is_guest=True, context=context)
        return url
    
    # LINEログイン時に取得されるコードからユーザー情報を取得
    def get_profile(self):
        request_code = self.request.GET.get("code")
        state = self.request.GET.get("state")
        state = json.loads(state)
        is_guest = (state['type'] == 'guest')
        redirect_to = state.get('redirect_to')
        try:
            id_token, profile = line.get_id_token(self.request, request_code, is_guest=is_guest)
        except ValueError:
            # ログイン失敗
            return None, None, None
        return id_token, profile, redirect_to
    
    # LINEプロフィールからユーザーを作成してログイン実行
    def do_login(self, id_token, profile):
        # ユーザーの取得/作成
        user_id = profile.get('sub')
        username = user_id + '_guest'
        user, created = User.objects.get_or_create(username=username, line_user_id=user_id, user_type=User.UserTypes.GUEST)
        user.id_token = id_token
        user.save()
        # ログイン実行
        authenticate(username=username, backend='lib.auth.LineAuthBackend')
        login(self.request, user, backend='lib.auth.LineAuthBackend')
        # プロフィールが作成済みかどうか確認
        service = GuestService()
        signup_done = service.filled_profile(user)
        return user, signup_done

    def send_welcome(self):
        line.send_welcome(self.request.user.line_user_id, is_guest=True)


class GuestService:
    def filled_profile(self, user):
        try:
            profile = user.guest_profile
        except GuestProfile.DoesNotExist:
            return False
        if not line.registered_line_at(user.id_token, is_guest=True):
            return False
        return True

class LineBotService:
    def reply(self, request):
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        bot.handler.handle(body, signature)