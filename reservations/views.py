import datetime

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.core.paginator import Paginator
from django.db.models import Q

from lib import mixins, line
from users import models as user_models
from hostess import models as hostess_models
from . import models, forms, services


class HostessListView(View):
    template = 'reservation/hostess/index.html'

    def get_queryset(self, page=1, page_size=24, **query):
        querysets = user_models.HostessProfile.objects.search(**query)
        page_obj = Paginator(querysets, page_size)
        return page_obj.page(page)
	
    # ホステス検索
    def get(self, request):
        form = forms.HostessSearchForm(request.GET)
        if not form.is_valid():
            querysets = self.get_queryset()
        else:
            querysets = self.get_queryset(**form.cleaned_data)
        context = dict(page_obj=querysets)
        return render(request, self.template, context=context)

class HostessSearchView(View):
    template = 'reservation/hostess/search.html'

    # ホステス検索
    def get(self, request):
        context = dict()
        return render(request, self.template, context=context)


class HostessDetailTestView(View):
    template = 'reservation/hostess/detail.html'

    def get(self, request):
        context = dict()
        return render(request, self.template, context=context)


class HostessDetailView(View):
    template = 'reservation/hostess/detail.html'

    def get_queryset(self, hostess_id):
        try:
            querysets = user_models.User.objects.get_hostess(hostess_id=hostess_id)
        except user_models.User.DoesNotExist:
            raise Http404
        return querysets
	
    # ホステス詳細
    def get(self, request, hostess_id):
        hostess = self.get_queryset(hostess_id)
        start_at = datetime.datetime.today()
        end_at = start_at + datetime.timedelta(days=7)
        available_times = hostess_models.AvailableTime.objects.filter(hostess=hostess, start_at__gt=start_at, end_at__lt=end_at)
        # 予約済みの場合は表示しない。ただし、拒否された予約の場合は表示する
        available_times = [a for a in available_times if not models.Reservation.objects.filter(time=a).filter(Q(is_approval=True) | Q(is_approval=None)).exists()]
        available_date = [start_at + datetime.timedelta(days=i) for i in range(7)]
        context = {'hostess': hostess, 'available_times': available_times, 'available_date': available_date}
        return render(request, self.template, context=context)

    # ホステス予約時間選択
    def post(self, request, hostess_id):
        hostess = self.get_queryset(hostess_id)
        form = forms.HostessDetailForm(request.POST)
        if not form.is_valid():
            return redirect('reservations:hostess_detail', hostess_id=hostess_id)
        # 予約画面へ遷移する -> ログインしてなければ自動的にプロフィール登録ページへリダイレクトする
        available_id = form.cleaned_data.get('available_time').available_id
        return redirect('reservations:create_reserve', available_id=available_id)


class CreateReserveView(mixins.GuestPageMixin, View):
    template = 'reservation/new.html'

    def get_queryset(self, available_id):
        try:
            querysets = hostess_models.AvailableTime.objects.get(available_id=available_id)
        except hostess_models.AvailableTime.DoesNotExist:
            raise Http404
        return querysets
	
    # 予約確認ページ
    def get(self, request, available_id):
        available_time = self.get_queryset(available_id)
        context = {'available_time': available_time}
        return render(request, self.template, context=context)

    # 予約実行
    def post(self, request, available_id):
        available_time = self.get_queryset(available_id)
        reservation = models.Reservation.objects.create(guest=self.request.user, time=available_time)
        service = services.ReservationService()
        service.send_notification(reservation)
        return redirect('reservations:done_reserve', reservation.reservation_id)


class DoneReserveView(mixins.GuestPageMixin, View):
    template = 'reservation/done.html'

    def get(self, request, reservation_id):
        context = dict()
        return render(request, self.template, context)

class ReserveAuthorizeView(View):
    template = 'reservation/authorize.html'

    def get_queryset(self, reservation_id=None, transaction_id=None):
        return models.LinePayTransaction.objects.get(reservation__reservation_id=reservation_id, transaction_id=int(transaction_id))

    def get(self, request, reservation_id):
        transaction_id = request.GET.get('transactionId')
        transaction = self.get_queryset(reservation_id=reservation_id, transaction_id=transaction_id)
        resp = line.pay_confirm(transaction)
        transaction.confirmed = True
        transaction.canceled = False
        transaction.save()

        # ミーティングを作成
        reservation = transaction.reservation
        service = services.ReservationService()
        meeting = service.create_meeting(reservation)
        service.send_meeting(meeting)
        context = dict(transaction=transaction)
        return render(request, self.template, context=context)


class ReserveCancelView(View):
    template = 'reservation/cancel.html'

    def get_queryset(self, reservation_id, transaction_id):
        return models.LinePayTransaction.objects.get(reservation_id=reservation_id, transaction_id=transaction_id)

    def get(self, request, reservation_id):
        transaction_id = request.GET.get('transactionId')
        transaction = self.get_queryset(reservation_id=reservation_id, transaction_id=transaction_id)
        transaction.confirmed = False
        transaction.canceled = True
        transaction.save()
        context = dict(transaction=transaction)
        return render(request, self.template, context=context)