from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)
    
    def all_hostess(self):
        return self.filter(user_type=self.model.UserTypes.HOSTESS)

    def get_hostess(self, line_user_id=None, hostess_id=None):
        if line_user_id:
            return self.get(line_user_id=line_user_id, user_type=self.model.UserTypes.HOSTESS)
        return self.get(user_id=hostess_id, user_type=self.model.UserTypes.HOSTESS)
    
    def get_guest(self, line_user_id=None, guest_id=None):
        if line_user_id:
            return self.get(line_user_id=line_user_id, user_type=self.model.UserTypes.GUEST)
        return self.get(user_id=guest_id, user_type=self.model.UserTypes.GUEST)


class GroupManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)