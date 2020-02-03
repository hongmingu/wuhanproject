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


class CountryInfo(models.Model):
    date_flag = models.ForeignKey(DateFlag, on_delete=models.DO_NOTHING, null=True, blank=True)

    name = models.CharField(default="country_info", blank=None, null=True, max_length=255)

    infected = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s // %s" % (self.date_flag.when, self.name, self.infected)

    class Meta:
        unique_together = ('date_flag', 'name',)


class CountryTranslation(models.Model):
    chinese = models.CharField(default="chinese", blank=None, null=True, max_length=255)

    english = models.CharField(default="english", blank=None, null=True, max_length=255)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s" % (self.chinese, self.english)


id_length = 15


class YoutubeVideo(models.Model):
    video_id = models.CharField(max_length=id_length)
    url = models.CharField(max_length=50 + id_length)
    title = models.CharField(max_length=120)
    channel_title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, default=None, blank=True, null=True)
    published_date = models.DateTimeField()
    view_count = models.CharField(max_length=id_length)
    thumbnail = models.CharField(null=True, blank=True, default=None, max_length=255)  # 썸네일
