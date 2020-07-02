import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import BaseModel


class AvailableTime(BaseModel, models.Model):
    available_id = models.UUIDField(_('available_id'), default=uuid.uuid4, db_index=True)
    hostess = models.ForeignKey('users.User', db_index=True, on_delete=models.CASCADE)
    start_at = models.DateTimeField(_('start_at'), db_index=True)
    end_at = models.DateTimeField(_('end_at'), db_index=True)

    class Meta:
        unique_together = (
            ('hostess', 'start_at'),
            ('hostess', 'end_at'),
        )