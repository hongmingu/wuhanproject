# Generated by Django 2.0.10 on 2020-02-05 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BBCItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('content', models.TextField(blank=True, default=None, max_length=5000, null=True)),
                ('url', models.CharField(blank=True, default=None, max_length=255, null=True, unique=True)),
                ('published_date', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('published_date_raw', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CountryCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=None, default='code', max_length=255, null=True, unique=True)),
                ('english', models.CharField(blank=None, default='english', max_length=255, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CountryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.IntegerField(blank=None, default=0, null=True)),
                ('death', models.IntegerField(blank=None, default=0, null=True)),
                ('recovered', models.IntegerField(blank=None, default=0, null=True)),
                ('death_rate', models.DecimalField(blank=None, decimal_places=2, default=0, max_digits=9, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('country_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='baseapp.CountryCode')),
            ],
        ),
        migrations.CreateModel(
            name='DateFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.CharField(blank=None, default='date_flag', max_length=255, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorldItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_count', models.IntegerField(blank=None, default=0, null=True)),
                ('confirmed', models.IntegerField(blank=None, default=0, null=True)),
                ('death', models.IntegerField(blank=None, default=0, null=True)),
                ('recovered', models.IntegerField(blank=None, default=0, null=True)),
                ('death_rate', models.DecimalField(blank=None, decimal_places=2, default=0, max_digits=9, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('date_flag', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='baseapp.DateFlag')),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_id', models.CharField(blank=True, default=None, max_length=15, null=True, unique=True)),
                ('url', models.CharField(blank=True, default=None, max_length=65, null=True)),
                ('title', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('channel_title', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('description', models.TextField(blank=True, default=None, max_length=5000, null=True)),
                ('published_date', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('published_date_raw', models.DateTimeField(blank=True, default=None, null=True)),
                ('view_count', models.CharField(blank=True, default=None, max_length=15, null=True)),
                ('thumbnail', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='countryitem',
            name='date_flag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='baseapp.DateFlag'),
        ),
        migrations.AlterUniqueTogether(
            name='countryitem',
            unique_together={('date_flag', 'country_code')},
        ),
    ]
