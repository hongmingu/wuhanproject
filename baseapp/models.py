from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from ckeditor.fields import RichTextField


# Create your models here.

class DateFlag(models.Model):
    when = models.CharField(default="date_flag", blank=None, null=True, max_length=255)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.when


class CountryCode(models.Model):
    code = models.CharField(default="code", blank=None, null=True, max_length=255, unique=True)
    english = models.CharField(default="english", blank=None, null=True, max_length=255)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s" % (self.code, self.english)


class CountryItem(models.Model):
    date_flag = models.ForeignKey(DateFlag, on_delete=models.DO_NOTHING, null=True, blank=True)
    country_code = models.ForeignKey(CountryCode, on_delete=models.DO_NOTHING, null=True, blank=True)

    confirmed = models.IntegerField(default=0, blank=None, null=True)
    death = models.IntegerField(default=0, blank=None, null=True)
    recovered = models.IntegerField(default=0, blank=None, null=True)
    death_rate = models.DecimalField(default=0, blank=None, null=True, max_digits=9, decimal_places=2)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s // %s" % (self.date_flag.when, self.country)

    class Meta:
        unique_together = ('date_flag', 'country_code',)


class WorldItem(models.Model):
    date_flag = models.OneToOneField(DateFlag, on_delete=models.DO_NOTHING, null=True, blank=True)
    country_count = models.IntegerField(default=0, blank=None, null=True)

    confirmed = models.IntegerField(default=0, blank=None, null=True)
    death = models.IntegerField(default=0, blank=None, null=True)
    recovered = models.IntegerField(default=0, blank=None, null=True)
    death_rate = models.DecimalField(default=0, blank=None, null=True, max_digits=9, decimal_places=2)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.date_flag.when


id_length = 15


class YoutubeItem(models.Model):
    video_id = models.CharField(max_length=id_length, unique=True, default=None, blank=True, null=True)
    url = models.CharField(max_length=50 + id_length, default=None, blank=True, null=True)
    title = models.CharField(max_length=120, default=None, blank=True, null=True)
    channel_title = models.CharField(max_length=100, default=None, blank=True, null=True)
    description = models.TextField(max_length=5000, default=None, blank=True, null=True)
    published_date = models.CharField(max_length=100, default=None, blank=True, null=True)
    published_date_raw = models.DateTimeField(default=None, blank=True, null=True)
    view_count = models.CharField(max_length=id_length, default=None, blank=True, null=True)
    thumbnail = models.CharField(null=True, blank=True, default=None, max_length=255)  # 썸네일
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class BBCItem(models.Model):
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    content = models.TextField(max_length=5000, default=None, blank=True, null=True)
    url = models.CharField(max_length=255, unique=True, default=None, blank=True, null=True)
    published_date = models.CharField(max_length=100, default=None, blank=True, null=True)
    published_date_raw = models.DateTimeField(default=None, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    text = RichTextField(default=None, blank=None, null=True, max_length=2000)
    nickname = models.CharField(default=None, blank=None, null=True, max_length=255)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.when

