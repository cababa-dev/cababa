from django.contrib.auth.backends import ModelBackend
from users.models import User


class LineAuthBackend(ModelBackend):
    """Log in to Django without providing a password.
    """
    def authenticate(self, username=None):
        try:
            user = User.objects.get(username=username)
            if not user.id_token:
                return None
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if not user.id_token:
                return None
            return user
        except User.DoesNotExist:
            return None