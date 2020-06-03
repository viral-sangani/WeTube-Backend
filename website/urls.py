from django.urls import path
from website.views import getChannel, trendingVideos, likedVideos, historyVideo, allChannel, subscribeChanel, commentVideo, dislikeVideo, likeVideo, current_user, UserList, userChannel, createChannel, getVideos, getVideoById, uploadVideo, getRecommendedVideos

urlpatterns = [
    path('current_user/', current_user),

    path('users/', UserList.as_view()),
    path('user/channel/', userChannel.as_view()),
    path('user/channel/create/', createChannel.as_view()),
    path('user/video/upload/', uploadVideo.as_view()),

    path('video/', getVideos.as_view()),
    path('video/recommended/', getRecommendedVideos.as_view()),
    path('video/like/<slug:slug>/', likeVideo.as_view()),
    path('video/dislike/<slug:slug>/', dislikeVideo.as_view()),
    path('video/comment/<slug:slug>/', commentVideo.as_view()),
    path('video/history/', historyVideo.as_view()),
    path('video/liked/', likedVideos.as_view()),
    path('video/trending/', trendingVideos.as_view()),
    path('video/<slug:slug>/', getVideoById.as_view()),

    path('channel/subscribe/<slug:slug>/', subscribeChanel.as_view()),
    path('channels/', allChannel.as_view()),
    path('channels/<slug:slug>/', getChannel.as_view())
]
