# Generated by Django 3.0.7 on 2020-06-03 18:08

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channelSlug', models.CharField(max_length=100, verbose_name='Channel Slug')),
                ('channelName', models.CharField(max_length=100, verbose_name='Channel Name')),
                ('channelImage', models.ImageField(null=True, upload_to='image/channel', verbose_name='Channel Image')),
                ('channelCreateTime', models.DateTimeField(auto_now_add=True, verbose_name='Channel Create Time')),
                ('channelUpdateTime', models.DateTimeField(auto_now=True, verbose_name='Channel Update Time')),
                ('channelAbout', models.TextField(verbose_name='Channel About')),
                ('channelTotalSub', models.IntegerField(default=0, verbose_name='Channel Total Subs')),
            ],
            options={
                'verbose_name': 'channel',
                'verbose_name_plural': 'channels',
                'db_table': 'channel',
            },
        ),
        migrations.RenameField(
            model_name='user',
            old_name='date_joined',
            new_name='dateJoined',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='first_name',
            new_name='firstName',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='is_active',
            new_name='isActive',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='last_name',
            new_name='lastName',
        ),
        migrations.AddField(
            model_name='user',
            name='hasChannel',
            field=models.BooleanField(default=False, verbose_name='hasChannel'),
        ),
        migrations.AddField(
            model_name='user',
            name='likedVideo',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribedChannel',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default),
        ),
        migrations.AddField(
            model_name='user',
            name='watchedVideo',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True, verbose_name='staff status'),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videoName', models.CharField(max_length=200, verbose_name='Video Name')),
                ('videoSlug', models.CharField(max_length=200, verbose_name='Video Slug')),
                ('videoLink', models.URLField(max_length=2000, null=True, verbose_name='Video Link')),
                ('videoThumbnail', models.URLField(max_length=2000, null=True, verbose_name='Video Thumbnail')),
                ('videoDescription', models.TextField(null=True, verbose_name='Video Description')),
                ('videoUploadTime', models.DateTimeField(auto_now_add=True, verbose_name='Video Upload Time')),
                ('videoTotalViews', models.IntegerField(default=0, verbose_name='Video Total Views')),
                ('videoTotalLikes', models.IntegerField(default=0, verbose_name='Video Total Likes')),
                ('videoTotalDislikes', models.IntegerField(default=0, verbose_name='Video Total Dislikes')),
                ('videoLikedBy', django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default)),
                ('videoDislikedBy', django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default)),
                ('videoComment', django.contrib.postgres.fields.jsonb.JSONField(default=website.models.default)),
                ('videoChannel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Channel', verbose_name='Channel Name')),
            ],
            options={
                'verbose_name': 'video',
                'verbose_name_plural': 'videos',
                'db_table': 'video',
            },
        ),
        migrations.AddField(
            model_name='channel',
            name='channelCreatedBy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
    ]
