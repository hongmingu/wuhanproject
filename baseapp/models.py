from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class DateFlag(models.Model):
    when = models.CharField(default="date_flag", blank=None, null=True, max_length=255)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.when


class CountryItem(models.Model):
    date_flag = models.ForeignKey(DateFlag, on_delete=models.DO_NOTHING, null=True, blank=True)

    country = models.CharField(default="country", blank=None, null=True, max_length=255)
    confirmed = models.CharField(default="confirmed", blank=None, null=True, max_length=255)
    death = models.CharField(default="death", blank=None, null=True, max_length=255)
    recovered = models.CharField(default="recovered", blank=None, null=True, max_length=255)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s // %s" % (self.date_flag.when, self.name, self.infected)

    class Meta:
        unique_together = ('date_flag', 'country',)


class CountryTranslation(models.Model):
    chinese = models.CharField(default="chinese", blank=None, null=True, max_length=255)

    english = models.CharField(default="english", blank=None, null=True, max_length=255)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s" % (self.chinese, self.english)


id_length = 15


class YoutubeVideo(models.Model):
    video_id = models.CharField(max_length=id_length, unique=True,default=None, blank=True, null=True)
    url = models.CharField(max_length=50 + id_length, default=None, blank=True, null=True)
    title = models.CharField(max_length=120, default=None, blank=True, null=True)
    channel_title = models.CharField(max_length=100, default=None, blank=True, null=True)
    description = models.TextField(max_length=5000, default=None, blank=True, null=True)
    published_date = models.CharField(max_length=100, default=None, blank=True, null=True)
    view_count = models.CharField(max_length=id_length, default=None, blank=True, null=True)
    thumbnail = models.CharField(null=True, blank=True, default=None, max_length=255)  # 썸네일
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class CnnItem(models.Model):
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    published_date = models.CharField(max_length=100, default=None, blank=True, null=True)
    content = models.TextField(max_length=5000, default=None, blank=True, null=True)
    url = models.CharField(max_length=255, unique=True, default=None, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
