from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.base import View

from lib import mixins
from . import forms


class StaffLoginView(View):
    template = 'staff/login.html'

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


class StaffSignupView(View):
    template = 'staff/signup.html'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        form = forms.SignupForm(request.POST, context={'request': request})
        if not form.is_valid():
            context = dict(form=form)
            return render(request, self.template, context)
        user = form.save()
        return render(request, 'staff/signup_done.html')


class StaffTopView(mixins.StaffPageMixin, View):
    template = 'staff/top.html'

    def get(self, request):
        return render(request, self.template)