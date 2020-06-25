from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

def default():
    return []

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    firstName = models.CharField(_('first name'), max_length=30, blank=True)
    lastName = models.CharField(_('last name'), max_length=30, blank=True)
    dateJoined = models.DateTimeField(_('date joined'), auto_now_add=True)
    isActive = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=True)
    hasChannel = models.BooleanField(_("hasChannel"), default=False)
    likedVideo = JSONField(default=default)
    watchedVideo = JSONField(default=default)
    subscribedChannel = JSONField(default=default)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Channel(models.Model):
    channelCreatedBy = models.ForeignKey("User", verbose_name=_("Created By"), on_delete=models.CASCADE)
    channelSlug = models.CharField(_("Channel Slug"), max_length=100)
    channelName = models.CharField(_("Channel Name"), max_length=100)
    channelImage = models.ImageField(_("Channel Image"), upload_to="image/channel", null=True)
    channelCreateTime = models.DateTimeField(_("Channel Create Time"), auto_now_add=True)
    channelUpdateTime = models.DateTimeField(_("Channel Update Time"), auto_now=True)
    channelAbout = models.TextField(_("Channel About"))
    channelTotalSub = models.IntegerField(_("Channel Total Subs"), default=0)

    def __str__(self):
        return self.channelName

    class Meta:
        db_table = "channel"
        verbose_name = _('channel')
        verbose_name_plural = _('channels')


class Video(models.Model):
    videoName = models.CharField(_("Video Name"), max_length=200)
    videoSlug = models.CharField(_("Video Slug"), max_length=200)
    videoLink = models.URLField(_("Video Link"), max_length=2000, null=True)
    videoThumbnail = models.URLField(_("Video Thumbnail"), max_length=2000, null=True)
    videoDescription = models.TextField(_("Video Description"), null=True)
    videoUploadTime = models.DateTimeField(_("Video Upload Time"), auto_now_add=True)
    videoTotalViews = models.IntegerField(_("Video Total Views"), default=0)
    videoTotalLikes = models.IntegerField(_("Video Total Likes"), default=0)
    videoTotalDislikes = models.IntegerField(_("Video Total Dislikes"), default=0)
    videoChannel = models.ForeignKey("Channel", verbose_name=_("Channel Name"), on_delete=models.CASCADE)
    videoLikedBy = JSONField(default=default)
    videoDislikedBy = JSONField(default=default)
    videoComment = JSONField(default=default)
    algolia_id = models.CharField(_("Algolia ID"), max_length=50)

    def __str__(self):
        return self.videoName

    class Meta:
        db_table = "video"
        verbose_name = _('video')
        verbose_name_plural = _('videos')
