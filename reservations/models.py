import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import BaseModel


class Reservation(BaseModel, models.Model):
    reservation_id = models.UUIDField(_('reservation_id'), default=uuid.uuid4, db_index=True)
    guest = models.ForeignKey('users.User', db_index=True, on_delete=models.CASCADE)
    time = models.ForeignKey('hostess.AvailableTime', db_index=True, on_delete=models.CASCADE)
    is_approval = models.BooleanField(_('is_approval'), db_index=True, null=True, default=None)

    @property
    def paied(self):
        transaction = LinePayTransaction.objects.filter(reservation=self).order_by('-created_at').first()
        return transaction.confirmed if transaction else False


class LinePayTransaction(BaseModel, models.Model):
    transaction_id = models.CharField(_('transaction_id'), max_length=100, db_index=True)
    access_token = models.CharField(_('access_token'), max_length=50)
    url = models.URLField(_('url'), max_length=1024)
    reservation = models.ForeignKey('reservations.Reservation', db_index=True, on_delete=models.CASCADE)
    confirmed = models.BooleanField(_('confirmed'), null=True, default=None)
    canceled = models.BooleanField(_('canceled'), null=True, default=None)
    return_code = models.CharField(_('return_code'), max_length=10)
    return_message = models.CharField(_('return_message'), max_length=100)
    amount = models.IntegerField(_('amount'), default=1)
    currency = models.CharField(_('currency'), max_length=10, default='JPY')


class ZoomAccount(BaseModel, models.Model):
    api_key = models.CharField(_('api_key'), max_length=50, unique=True)
    api_secret = models.CharField(_('api_secret'), max_length=100)
    api_imchat_history_token = models.CharField(_('api_imchat_history_token'), max_length=500)
    admin_email = models.CharField(_('admin_email'), max_length=200)


class ZoomMeeting(BaseModel, models.Model):
    meeting_id = models.CharField(_('meeting_id'), max_length=100, db_index=True)
    join_url = models.URLField(_('join_url'), max_length=1024)
    start_url = models.URLField(_('start_url'), max_length=1024)
    password = models.CharField(_('password'), max_length=20, null=True, default=None)
    zoom_meeting_id = models.CharField(_('zoom_meeting_id'), max_length=20, null=True, default=None)
    reservation = models.ForeignKey('reservations.Reservation', db_index=True, on_delete=models.CASCADE)
    context = models.TextField(_('context'), default='')
    account = models.ForeignKey('reservations.ZoomAccount', null=True, default=None, on_delete=models.CASCADE)
    start_at = models.DateTimeField(_('start_at'), db_index=True, null=True, default=None)
    end_at = models.DateTimeField(_('end_at'), db_index=True, null=True, default=None)