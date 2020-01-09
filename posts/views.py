from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework import generics, viewsets
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST
)

from posts.models import Post
from posts.serializers import UserCreateSerializer, PostSerializer
from posts.services import PostLogic


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny, )
    serializer_class = UserCreateSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data,
                            status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user == post.created_by:
            raise PermissionDenied('You can not delete this post.')
        return super().destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=True)
    def like(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.created_by:
            raise PermissionDenied('You cannot vote own post')

        liked_post = PostLogic.vote_post(post, request.user, vote='like')
        serializer = PostSerializer(liked_post)

        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def dislike(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.created_by:
            raise PermissionDenied('You cannot vote own post')

        disliked_post = PostLogic.vote_post(post, request.user, vote='dislike')
        serializer = PostSerializer(disliked_post)

        return Response(serializer.data, status=HTTP_200_OK)
