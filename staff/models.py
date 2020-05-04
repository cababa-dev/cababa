import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import BaseModel
from users.models import User


class OTP(BaseModel, models.Model):
    otp_id = models.UUIDField(_('otp_id'), default=uuid.uuid4, unique=True, db_index=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_index=True)