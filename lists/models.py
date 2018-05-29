from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Bucketlist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bucketlists'
    )

    def __repr__(self):
        return "BucketList: {}".format(self.name)


class Item(models.Model):
    title = models.CharField(max_length=100, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    done = models.BooleanField(default=False)
    bucketlist = models.ForeignKey(
        Bucketlist,
        on_delete=models.CASCADE,
        related_name='items'
    )

    def __str__(self):
        return "Item: {}".format(self.title)
