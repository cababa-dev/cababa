import urllib.parse

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import japanmap

from lib import line, mixins
from users import models as user_models
from . import services, forms


class GuestLoginView(View):
    def get(self, request):
        service = services.LineLoginService(request)
        login_url = service.login_url()
        error=request.GET.get('error')
        context = dict(login_url=login_url, error=error)
        return render(request, 'guest/login.html', context)


class GuestLoginCallbackView(View):
    def get(self, request):
        # LINEログイン成功時にコードを取得
        service = services.LineLoginService(request)
        id_token, profile, redirect_to = service.get_profile()
        # ログイン出来なかった場合
        if not id_token or not profile:
            params = urllib.parse.urlencode(dict(error='ログインに失敗しました'.encode('utf-8'), redirect_to=redirect_to))
            url = '{}?{}'.format(reverse('guest:login'), params)
            return redirect(url)
        # ユーザー作成処理
        user, signup_done = service.do_login(id_token, profile)
        if not signup_done:
            # 初回登録時のプロフィール設定ページへ移動
            return redirect(reverse('guest:signup') + '?redirect_to=' + redirect_to)
        # ログイン完了時には元のページに移動
        if redirect_to:
            return redirect(redirect_to)
        # デフォルトはサインアップ完了画面
        return redirect(reverse('guest:signup_done'))


class SignUpView(mixins.GuestSignupMixin, View):
    template = 'guest/signup.html'

    def get_prefectures(self):
        prefectures = []
        for name, code in zip(japanmap.pref_names, list(range(len(japanmap.pref_names)))):
            prefectures.append(dict(
                name=name,
                code=code
            ))
        prefectures[0]['name'] = '非公開'
        return prefectures

    def get(self, request):
        prefectures = self.get_prefectures()
        context = dict(prefectures=prefectures)
        return render(request, self.template, context)
    
    def post(self, request):
        form = forms.SignupForm(request.POST, request.FILES, context={'request': request})
        if not form.is_valid():
            prefectures = self.get_prefectures()
            context = dict(prefectures=prefectures, form=form)
            return render(request, self.template, context)
        profile = form.save()
        service = services.LineLoginService(request)
        service.send_welcome()
        # ログイン完了時には元のページに移動
        redirect_to = request.GET.get('redirect_to')
        if redirect_to:
            return redirect(redirect_to)
        return redirect(reverse('guest:signup_done'))


class SignUpDoneView(mixins.GuestSignupMixin, View):
    template = 'guest/signup_done.html'

    def get(self, request):
        service = services.LineLoginService(request)
        service.send_welcome()
        context = dict()
        return render(request, self.template, context)


class LineBotWebhookView(View):
    def post(self, request):
        service = services.LineBotService()
        service.reply(request)
        return HttpResponse('OK')
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)