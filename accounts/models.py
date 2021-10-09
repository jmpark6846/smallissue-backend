from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not username:
            raise ValueError("User must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager()

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, null=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile', )
    job = models.CharField(max_length=140, null=True, blank=True)


def save_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()


post_save.connect(save_profile, sender=User)
