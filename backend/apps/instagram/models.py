from django.db import models


# Create your models here.
class contact(models.Model):
    link_to_account = models.CharField(max_lenght=100, blank=False)
    username = models.CharField(max_length=100, blank=False)
    followed_at = models.DateTimeField(null=False, blank=False)
