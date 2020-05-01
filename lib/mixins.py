import urllib.parse

from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from users.models import User
from guest.services import GuestService


class HostessPageMixin(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return self.request.user.user_type == User.UserTypes.HOSTESS
    
    def handle_no_permission(self):
        return redirect('hostess:login')


class GuestSignupMixin(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = 'redirect_to'
    
    def test_func(self):
        is_guest = self.request.user.user_type == User.UserTypes.GUEST
        if not is_guest:
            return False
    
    def handle_no_permission(self):
        return redirect(reverse('guest:login') + '?redirect_to=' + urllib.parse.quote(self.request.path, safe=''))


class GuestPageMixin(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = 'redirect_to'
    
    def test_func(self):
        is_guest = self.request.user.user_type == User.UserTypes.GUEST
        if not is_guest:
            return False
        # プロフィール作成済みかどうか
        service = GuestService()
        return service.filled_profile(self.request.user)
    
    def handle_no_permission(self):
        redirect_to = self.request.GET.get('redirect_to')
        if not redirect_to:
            redirect_to = urllib.parse.quote(self.request.path, safe='')
        return redirect(reverse('guest:signup') + '?redirect_to=' + redirect_to)


class StaffPageMixin(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return self.request.user.user_type == User.UserTypes.STAFF
    
    def handle_no_permission(self):
        return redirect('staff:login')