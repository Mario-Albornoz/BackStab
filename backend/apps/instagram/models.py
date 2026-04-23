from apps.users.models import User
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


# Create your models here.
class Contact(models.Model):
    link_to_account = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=100, blank=False)
    followed_at = models.DateTimeField(null=False, blank=False)


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(Contact, on_delete=models.CASCADE)


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(Contact, on_delete=models.CASCADE)
