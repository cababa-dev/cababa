from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.urls import reverse

from . import forms


class PreRegistrationView(View):
    template = 'pre_register/form.html'

    def get(self, request):
        form = forms.PreRegistrationForm()
        context = dict(form=form)
        return render(request, self.template, context)
    
    def post(self, request):
        form = forms.PreRegistrationForm(request.POST, request.FILES, context={'request': self.request})
        if not form.is_valid():
            print(form.errors)
            context = dict(form=form)
            return render(request, self.template, context)
        profile = form.save()
        return redirect(reverse('pre_register:done'))


def pre_registration_done_view(request):
    return render(request, 'pre_register/done.html')