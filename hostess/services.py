import json

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login

from lib import line
from users.models import User, HostessProfile, Group
from . import bot


class LineLoginService:
    def __init__(self, request):
        self.request = request

    # LINEログインページへのURLを作成
    def login_url(self, context={}):
        url = line.login_url(self.request, is_guest=False, context=context)
        return url
    
    # LINEログイン時に取得されるコードからユーザー情報を取得
    def get_profile(self):
        request_code = self.request.GET.get("code")
        state = self.request.GET.get("state")
        state = json.loads(state)
        is_guest = (state['type'] == 'guest')
        try:
            id_token, profile = line.get_id_token(self.request, request_code, is_guest=is_guest)
        except ValueError:
            # ログイン失敗
            return None, None
        return id_token, profile
    
    # LINEプロフィールからユーザーを作成してログイン実行
    def do_login(self, id_token, profile):
        line_user_id = profile.get('sub')
        username = line_user_id + '_hostess'

        state = self.request.GET.get("state")
        state = json.loads(state)
        user_id = state.get('invitation_hostess')

        if user_id:
            # もし作成済みのユーザーに招待を受けた場合は
            # ユーザーを取得する
            user = User.objects.get(user_id=user_id)
            user.line_user_id = line_user_id
            user.username = username
        else:
            # ユーザーの取得/作成
            user, created = User.objects.get_or_create(username=username, line_user_id=line_user_id, user_type=User.UserTypes.HOSTESS)

        user.id_token = id_token
        user.save()
        # ログイン実行
        authenticate(username=username, backend='lib.auth.LineAuthBackend')
        login(self.request, user, backend='lib.auth.LineAuthBackend')
        # プロフィールが作成済みかどうか確認
        service = HostessService()
        signup_done = service.filled_profile(user)
        return user, signup_done

    def send_welcome(self):
        line.send_welcome(self.request.user.line_user_id, is_guest=False)

    def get_invitation_group(self):
        state = self.request.GET.get("state")
        state = json.loads(state)
        group_id = state.get('invitation')
        if not group_id:
            return None
        group = Group.objects.get(group_id=group_id)
        return group


class HostessService:
    def filled_profile(self, user):
        try:
            profile = user.hostess_profile
        except HostessProfile.DoesNotExist:
            return False
        if not line.registered_line_at(user.id_token, is_guest=False):
            return False
        return True

class LineBotService:
    def reply(self, request):
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        bot.handler.handle(body, signature)