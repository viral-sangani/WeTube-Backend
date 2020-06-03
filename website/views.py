from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .serializers import UserSerializer, UserSerializerWithToken
from website.models import Channel, Video
from slugify import slugify
import datetime

url = 'http://localhost:8000'


def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def createVideoList(videoList):
    res_list = []
    for item in videoList:
        res_list.append({
            'videoId': item.pk,
            'videoName': item.videoName,
            'videoSlug': item.videoSlug,
            'videoLink': item.videoLink,
            'videoThumbnail': item.videoThumbnail,
            'videoTotalViews': item.videoTotalViews,
            'videoTotalLikes': item.videoTotalLikes,
            'videoTotalDislikes': item.videoTotalDislikes,
            'videoChannelName': item.videoChannel.channelName,
            'videoChannelSlug': item.videoChannel.channelSlug,
            'videoDescription': item.videoDescription,
            'videoChannelImage': url + item.videoChannel.channelImage.url,
            'videoUploadTime': pretty_date(item.videoUploadTime.replace(tzinfo=None))

        })
    return res_list


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class userChannel(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            resObj = {
                "hasChannel": request.user.hasChannel,
            }
            if request.user.hasChannel:
                channelObj = Channel.objects.get(channelCreatedBy=request.user)
                resObj.update({
                    "channelName": channelObj.channelName,
                    "channelImage": url + channelObj.channelImage.url,
                    "channelCreateTime": channelObj.channelCreateTime,
                    "channelUpdateTime": channelObj.channelUpdateTime,
                    "channelAbout": channelObj.channelAbout,
                    "channelTotalSub": channelObj.channelTotalSub
                })
                videoObj = Video.objects.filter(videoChannel=channelObj)
                videoList = createVideoList(videoObj)
                resObj.update({"videoList": videoList})
            return Response(resObj)
        else:
            return Response({'Error': 'Please Login in access this.'})


class createChannel(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        if request.user.is_authenticated:
            if request.user.hasChannel is False:
                channelObj = Channel()
                channelObj.channelName = request.data.get('channelName')
                channelObj.channelSlug = slugify(request.data.get('channelName'))
                channelObj.channelImage = request.FILES.get('channelImage')
                channelObj.channelAbout = request.data.get('channelAbout')
                channelObj.channelCreatedBy = request.user
                channelObj.save()
                request.user.hasChannel = True
                request.user.channelObj = channelObj
                request.user.save()
                return Response({'succes': True})
            else:
                return Response({'Error': 'This Accound has a Channel.'})
        else:
            return Response({'Error': 'Please Login in access this.'})


class uploadVideo(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            url = request.data['videoLink']
            videoObj = Video()
            videoObj.videoName = request.data.get('videoName', "N/A")
            videoObj.videoSlug = slugify(request.data.get('videoName', "N/A"))
            videoObj.videoLink = url
            videoObj.videoThumbnail = "https://i.ytimg.com/vi/" + url[url.index("=")+1:] + "/maxresdefault.jpg"
            videoObj.videoDescription = request.data.get('videoDescription', "N/A")
            videoObj.videoChannel = Channel.objects.get(channelCreatedBy=request.user)
            videoObj.save()
            return Response({'success': True})
        else:
            return Response({'Error': 'Please Login in access this.'})


class getVideos(APIView):
    def get(self, request):
        videoObj = Video.objects.all().order_by('-videoUploadTime')
        res_list = []
        res_list = createVideoList(videoObj)

        return Response(res_list)


class getVideoById(APIView):
    def get(self, request, slug):
        item = Video.objects.get(videoSlug=slug)
        if request.user.is_authenticated:
            hasLiked = True if request.user.pk in item.videoLikedBy else False
            hasDisliked = True if request.user.pk in item.videoDislikedBy else False
            if slug not in request.user.watchedVideo:
                request.user.watchedVideo.append(slug)
                request.user.save()
            hasSubscribed = False
            if item.videoChannel.pk in request.user.subscribedChannel:
                hasSubscribed = True
        item.videoTotalViews += 1
        item.save()

        videoList = Video.objects.all().exclude(videoSlug=slug)
        res_dict = {
            'videoId': item.pk,
            'videoName': item.videoName,
            'videoSlug': item.videoSlug,
            'videoLink': item.videoLink,
            'videoThumbnail': item.videoThumbnail,
            'videoTotalViews': item.videoTotalViews,
            'videoTotalLikes': item.videoTotalLikes,
            'videoTotalDislikes': item.videoTotalDislikes,
            'videoDescription': item.videoDescription,
            'videoComment': item.videoComment,
            'videoChannelName': item.videoChannel.channelName,
            'videoChannelSlug': item.videoChannel.channelSlug,
            'viodeChannelSubs': item.videoChannel.channelTotalSub,
            'videoChannelImage': url + item.videoChannel.channelImage.url,
            'videoUploadTime': pretty_date(item.videoUploadTime.replace(tzinfo=None)),
            'videoList': createVideoList(videoList),
        }
        if request.user.is_authenticated:
            res_dict.update({
                'hasLiked': hasLiked,
                'hasDisliked': hasDisliked,
                'hasSubscribed': hasSubscribed,
                'userName': request.user.firstName + " " + request.user.lastName
            })
        return Response(res_dict)


class getRecommendedVideos(APIView):
    def get(self, request):
        res_list = []
        id = request.query_params.get('id')
        if id is not None:
            channelObj = Channel.objects.get(video=id)
            videoObj__1 = Video.objects.filter(
                videoChannel=channelObj).exclude(id=id)
            videoObj__2 = Video.objects.all().order_by("-videoUploadTime").exclude(id=id)
            videoObj = videoObj__1 | videoObj__2
        else:
            videoObj = Video.objects.all().order_by("-videoUploadTime").exclude(id=id)
        res_list = createVideoList(videoObj)

        return Response(res_list[:10])


class likeVideo(APIView):
    def get(self, request, slug):
        item = Video.objects.get(videoSlug=slug)
        if request.user.pk not in item.videoLikedBy:
            item.videoLikedBy.append(request.user.pk)
            item.videoTotalLikes += 1
            print("like +")
            if request.user.pk in item.videoDislikedBy:
                item.videoDislikedBy.remove(request.user.pk)
                item.videoTotalDislikes -= 1
                print("dislike -")
        else:
            item.videoLikedBy.remove(request.user.pk)
            item.videoTotalLikes -= 1
            print("like -")

        ## Dislike
        if slug in request.user.likedVideo:
            request.user.likedVideo.remove(slug)
        else:
            request.user.likedVideo.append(slug)
        item.save()
        request.user.save()
        request.user.likedVideo.append(slug)
        return Response({"success": True})


class dislikeVideo(APIView):
    def get(self, request, slug):
        item = Video.objects.get(videoSlug=slug)
        if request.user.pk not in item.videoDislikedBy:
            item.videoDislikedBy.append(request.user.pk)
            item.videoTotalDislikes += 1
            print("dislike +")
            if request.user.pk in item.videoLikedBy:
                item.videoLikedBy.remove(request.user.pk)
                item.videoTotalLikes -= 1
                print("like -")
        else:
            item.videoDislikedBy.remove(request.user.pk)
            item.videoTotalDislikes -= 1
            print("dislike -")
        item.save()
        request.user.save()
        request.user.likedVideo.append(slug)
        return Response({"success": True})


class commentVideo(APIView):
    def post(self, request, slug):
        item = Video.objects.get(videoSlug=slug)
        item.videoComment.append({
            "commentId": str(datetime.datetime.now().time()),
            "user": request.user.pk,
            "userName": request.user.firstName + " " + request.user.lastName,
            "comment": request.data.get("comment", ""),
            "time": str(datetime.datetime.now().strftime("%d/%m/%y"))

        })
        item.save()
        return Response({"success": True})


class subscribeChanel(APIView):
    def get(self, request, slug):
        channelObj = Channel.objects.get(channelSlug=slug)
        if channelObj.pk not in request.user.subscribedChannel:
            request.user.subscribedChannel.append(channelObj.pk)
            channelObj.channelTotalSub += 1
        request.user.save()
        channelObj.save()
        return Response({'success': True})


class allChannel(APIView):
    def get(self, request):
        channelObj = Channel.objects.all()
        res_list = []
        for item in channelObj:
            res_list.append({
                "channelName": item.channelName,
                "channelSlug": item.channelSlug,
                "channelImage": url + item.channelImage.url
            })
        return Response(res_list)


class historyVideo(APIView):
    def get(self, request):
        res_list = []
        for slug in request.user.watchedVideo[::-1]:
            item = Video.objects.get(videoSlug=slug)
            res_list.append({
                'videoId': item.pk,
                'videoName': item.videoName,
                'videoSlug': item.videoSlug,
                'videoLink': item.videoLink,
                'videoThumbnail': item.videoThumbnail,
                'videoTotalViews': item.videoTotalViews,
                'videoTotalLikes': item.videoTotalLikes,
                'videoTotalDislikes': item.videoTotalDislikes,
                'videoChannelName': item.videoChannel.channelName,
                'videoChannelSlug': item.videoChannel.channelSlug,
                'videoDescription': item.videoDescription,
                'videoChannelImage': url + item.videoChannel.channelImage.url,
                'videoUploadTime': pretty_date(item.videoUploadTime.replace(tzinfo=None))
            })
        return Response(res_list)


class likedVideos(APIView):
    def get(self, request):
        res_list = []
        for slug in request.user.likedVideo[::-1]:
            item = Video.objects.get(videoSlug=slug)
            res_list.append({
                'videoId': item.pk,
                'videoName': item.videoName,
                'videoSlug': item.videoSlug,
                'videoLink': item.videoLink,
                'videoThumbnail': item.videoThumbnail,
                'videoTotalViews': item.videoTotalViews,
                'videoTotalLikes': item.videoTotalLikes,
                'videoTotalDislikes': item.videoTotalDislikes,
                'videoChannelName': item.videoChannel.channelName,
                'videoChannelSlug': item.videoChannel.channelSlug,
                'videoDescription': item.videoDescription,
                'videoChannelImage': url + item.videoChannel.channelImage.url,
                'videoUploadTime': pretty_date(item.videoUploadTime.replace(tzinfo=None))
            })
        return Response(res_list)


class trendingVideos(APIView):
    def get(self, request):
        videoObj = Video.objects.all().order_by('-videoTotalViews')
        res_list = createVideoList(videoObj)
        return Response(res_list)


class getChannel(APIView):
    def get(self, request, slug):
        channelObj = Channel.objects.get(channelSlug=slug)
        res_dict = {
            "channelName": channelObj.channelName,
            "channelImage": url + channelObj.channelImage.url,
            "channelCreateTime": channelObj.channelCreateTime,
            "channelUpdateTime": channelObj.channelUpdateTime,
            "channelAbout": channelObj.channelAbout,
            "channelTotalSub": channelObj.channelTotalSub
        }
        if request.user.is_authenticated:
            hasSubscribed = False
            if channelObj.pk in request.user.subscribedChannel:
                hasSubscribed = True
            res_dict.update({
                'hasSubscribed': hasSubscribed
            })
        videoObj = Video.objects.filter(videoChannel=channelObj)
        videoList = createVideoList(videoObj)
        res_dict.update({"videoList": videoList})
        return Response(res_dict)
