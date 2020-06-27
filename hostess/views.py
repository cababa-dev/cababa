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


class HostessDetailView(View):
    template = 'reservation/hostess/detail.html'

    def get_queryset(self, hostess_id):
        try:
            querysets = user_models.User.objects.get_hostess(hostess_id=hostess_id)
        except user_models.User.DoesNotExist:
            raise Http404
        return querysets
	
    def get(self, request, hostess_id):
        hostess = self.get_queryset(hostess_id)
        context = {'hostess': hostess}
        return render(request, self.template, context=context)


class HostessLoginView(View):
    def get(self, request):
        service = services.LineLoginService(request)
        login_url = service.login_url()
        error=request.GET.get('error')
        context = dict(login_url=login_url, error=error)
        return render(request, 'hostess/login.html', context)


class HostessLoginCallbackView(View):
    def get(self, request):
        # LINEログイン成功時にコードを取得
        service = services.LineLoginService(request)
        id_token, profile = service.get_profile()
        # ログイン出来なかった場合
        if not id_token or not profile:
            params = urllib.parse.urlencode(dict(error='ログインに失敗しました'.encode('utf-8')))
            url = '{}?{}'.format(reverse('hostess:login'), params)
            return redirect(url)
        # ユーザー作成処理
        user, signup_done = service.do_login(id_token, profile)
        # 招待の場合
        group = service.get_invitation_group()
        if group:
            user.group = group
            user.save()
        # 初回登録が完了していない場合
        if not signup_done:
            # 初回登録時のプロフィール設定ページへ移動
            return redirect(reverse('hostess:signup'))
        # ログイン完了ページへ移動
        return redirect(reverse('hostess:signup_done'))


class SignUpView(mixins.HostessPageMixin, View):
    template = 'hostess/signup.html'

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
        return redirect(reverse('hostess:signup_done'))


class SignUpDoneView(mixins.HostessPageMixin, View):
    template = 'hostess/signup_done.html'

    def get(self, request):
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


class HostessInviteView(View):
    template = 'hostess/invite.html'

    def get_queryset(self, user_id):
        querysets = user_models.User.objects.get(user_id=user_id)
        return querysets

    def get(self, request, user_id):
        hostess = self.get_queryset(user_id)
        service = services.LineLoginService(request)
        login_url = service.login_url(context=dict(invitation_hostess=str(hostess.user_id)))
        context = dict(hostess=hostess, login_url=login_url)
        return render(request, self.template, context)
    

class HostessGroupInviteView(View):
    template = 'hostess/group_invite.html'

    def get_queryset(self, group_id):
        querysets = user_models.Group.objects.get(group_id=group_id)
        return querysets

    def get(self, request, group_id):
        group = self.get_queryset(group_id)
        service = services.LineLoginService(request)
        login_url = service.login_url(context=dict(invitation=str(group.group_id)))
        context = dict(group=group, login_url=login_url)
        return render(request, self.template, context)