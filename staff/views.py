from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.contrib.auth import logout

from lib import mixins
from users import models as user_models
from . import models, forms, services


class StaffLoginView(View):
    template = 'staff/account/login.html'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        form = forms.LoginForm(request.POST, context={'request': request})
        if not form.is_valid():
            context = dict(form=form)
            return render(request, self.template, context)
        form.save()
        redirect_to = request.GET.get('redirect_to')
        if redirect_to:
            return redirect(redirect_to)
        return redirect('staff:top')


class StaffLogoutView(mixins.StaffPageMixin, View):
    def get(self, request):
        logout(request)
        return redirect('staff:login')


class StaffSignupView(View):
    template = 'staff/account/signup.html'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        form = forms.SignupForm(request.POST, context={'request': request})
        if not form.is_valid():
            context = dict(form=form)
            return render(request, self.template, context)
        user = form.save()
        return render(request, 'staff/signup_done.html')


class SignupConfirmView(View):
    template = 'staff/account/signup_confirm.html'

    def get_queryset(self, otp_id):
        querysets = models.OTP.objects.filter(otp_id=otp_id).first()
        return querysets

    def get(self, request):
        otp_id = request.GET.get('token')
        otp = self.get_queryset(otp_id)
        context = {'otp': otp}
        return render(request, self.template, context)

    def post(self, request):
        form = forms.SignupConfirmForm(request.POST, context={'request': request})
        if not form.is_valid():
            otp_id = request.GET.get('token')
            otp = self.get_queryset(otp_id)
            context = dict(form=form, otp=otp)
            return render(request, self.template, context)
        user = form.save()
        return redirect('staff:top')


class StaffTopView(mixins.StaffPageMixin, View):
    template = 'staff/top.html'

    def get(self, request):
        return render(request, self.template)


class StaffListView(mixins.StaffPageMixin, View):
    template = 'staff/staff/list.html'

    def get_queryset(self, request):
        user = request.user
        querysets = user_models.User.objects.filter(group=user.group, user_type=user_models.User.UserTypes.STAFF).exclude(username=user.username)
        return querysets

    def get(self, request):
        page_obj = self.get_queryset(request)
        context = {'page_obj': page_obj}
        return render(request, self.template, context)


class StaffCreateView(mixins.StaffPageMixin, View):
    template = 'staff/staff/new.html'

    def get(self, request):
        context = {}
        return render(request, self.template, context)
    
    def post(self, request):
        form = forms.StaffForm(request.POST, context={'request': request})
        if not form.is_valid():
            context = dict(form=form)
            return render(request, self.template, context)
        otp = form.create()
        service = services.StaffService()
        service.send_registration_otp(otp)
        return redirect(reverse('staff:staff_list'))


class StaffDetailView(mixins.StaffPageMixin, View):
    template = 'staff/staff/detail.html'

    def get_queryset(self, staff_id):
        querysets = user_models.User.objects.get(user_id=staff_id, user_type=user_models.User.UserTypes.STAFF)
        return querysets

    def get(self, request, staff_id):
        querysets = self.get_queryset(staff_id)
        context = {'staff': querysets}
        return render(request, self.template, context)

class StaffEditView(mixins.StaffPageMixin, View):
    template = 'staff/staff/edit.html'

    def get_queryset(self, staff_id):
        querysets = user_models.User.objects.get(user_id=staff_id, user_type=user_models.User.UserTypes.STAFF)
        return querysets

    def get(self, request, staff_id):
        querysets = self.get_queryset(staff_id)
        context = {'staff': querysets}
        return render(request, self.template, context)

    def post(self, request, staff_id):
        querysets = self.get_queryset(staff_id)
        form = forms.StaffForm(request.POST, context={'request': request, 'staff': querysets})
        if not form.is_valid():
            print(form.errors)
            context = dict(form=form)
            return render(request, self.template, context)
        user = form.update()
        return redirect(reverse('staff:staff_detail', kwargs=dict(staff_id=querysets.user_id)))


class StaffDeleteView(mixins.StaffPageMixin, View):
    def get_queryset(self, staff_id):
        querysets = user_models.User.objects.get(user_id=staff_id, user_type=user_models.User.UserTypes.STAFF)
        return querysets

    def post(self, request, staff_id):
        staff = self.get_queryset(staff_id)
        staff.delete()
        return redirect('staff:staff_list')


class StaffEditMeView(mixins.StaffPageMixin, View):
    template = 'staff/staff/edit_me.html'

    def get(self, request):
        context = {}
        return render(request, self.template, context)

    def post(self, request):
        form = forms.StaffEditMeForm(request.POST, context={'request': request})
        if not form.is_valid():
            context = dict(form=form)
            return render(request, self.template, context)
        user = form.update()
        return redirect('staff:edit_me')