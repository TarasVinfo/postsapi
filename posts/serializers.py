from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(required=False)
    dislikes = serializers.IntegerField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'created_by', 'pub_date',
                  'likes', 'dislikes')
        extra_kwargs = {'created_by': {'read_only': True}}


class UserCreateSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'token')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    @staticmethod
    def get_token(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
