from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_200_OK,
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
)
from rest_framework.test import (
    APIRequestFactory, APITestCase, force_authenticate)

from posts.models import Post, Vote
from posts.views import PostViewSet, UserCreate


class TestPostViewSet(APITestCase):

    def setUp(self):

        self.factory = APIRequestFactory()
        self.user_first_poster = User.objects.create(
            username='first_poster',
            first_name='first',
            last_name='poster',
            email='first_poster@posts.com'
        )
        self.user_second_poster = User.objects.create(
            username='second_poster',
            first_name='second',
            last_name='poster',
            email='second_poster@posts.com'
        )
        self.user_for_vote = User.objects.create(
            username='for_vote',
            first_name='user',
            last_name='for_vote',
            email='for_vote@posts.com'
        )
        self.content_data = {
            'title': 'Test Post',
            'content': 'This is post of testing'
        }

    def create_post_service(self):

        view = PostViewSet.as_view({'post': 'create'})
        url = 'api/v1/posts'
        request = self.factory.post(url, self.content_data)
        force_authenticate(request, user=self.user_first_poster)

        return view(request)

    def vote_post_service(self, post_id, vote, vote_by):

        view = PostViewSet.as_view({'post': vote})
        url = 'api/v1/posts'
        request = self.factory.post(url)
        force_authenticate(request, user=vote_by)

        return view(request, pk=post_id)

    def test_create_post_with_valid_data(self):

        response = self.create_post_service()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data.get('title'),
                         self.content_data.get('title'))
        self.assertEqual(response.data.get('content'),
                         self.content_data.get('content'))
        self.assertEqual(response.data.get('created_by'),
                         self.user_first_poster.id)

    def test_fail_create_post_with_invalid_data(self):

        view = PostViewSet.as_view({'post': 'create'})
        url = 'api/v1/posts'
        list_content_data = [
            {},
            {'title': 'Test Post'},
            {'content': 'This is post of testing'},
            {'title': '', 'content': ''}
        ]

        for data in list_content_data:
            request = self.factory.post(url, data)
            force_authenticate(request, user=self.user_first_poster)
            response = view(request)

            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_post(self):

        response_create = self.create_post_service()
        post = Post.objects.filter(title='Test Post').first()

        self.assertEqual(post.title, self.content_data.get('title'))
        self.assertEqual(post.content, self.content_data.get('content'))

        view = PostViewSet.as_view({'post': 'destroy'})
        url = 'api/v1/posts'
        request = self.factory.post(url)
        force_authenticate(request, user=self.user_first_poster)

        response_destroy = view(request, pk=response_create.data.get('id'))

        self.assertEqual(response_destroy.status_code, HTTP_204_NO_CONTENT)

        post = Post.objects.filter(title='Test Post').first()

        self.assertIsNone(post)

    def test_deny_another_user_to_delete_post(self):

        response_create = self.create_post_service()

        view = PostViewSet.as_view({'post': 'destroy'})
        url = 'api/v1/posts'
        request = self.factory.post(url)
        force_authenticate(request, user=self.user_second_poster)

        response_destroy = view(request, pk=response_create.data.get('id'))
        error_code = 'permission_denied'
        error_detail = response_destroy.data.get('detail')

        self.assertEqual(response_destroy.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(error_detail.code, error_code)

    def test_vote_post(self):

        response_create = self.create_post_service()
        post_id = response_create.data.get('id')

        expected_data = [
            {'vote': 'like', 'likes': 1, 'dislikes': 0},
            {'vote': 'dislike', 'likes': 0, 'dislikes': 1},
            {'vote': 'like', 'likes': 1, 'dislikes': 0},
        ]

        for data in expected_data:
            response = self.vote_post_service(
                post_id,
                vote=data.get('vote'),
                vote_by=self.user_for_vote
            )

            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.data.get('likes'),
                             data.get('likes'))
            self.assertEqual(response.data.get('dislikes'),
                             data.get('dislikes'))

    def test_deny_vote_post_user_create(self):

        response_create = self.create_post_service()
        post_id = response_create.data.get('id')

        expected_data = [
            {'vote': 'like', 'error_code': 'permission_denied'},
            {'vote': 'dislike', 'error_code': 'permission_denied'},
        ]

        for data in expected_data:
            response = self.vote_post_service(
                post_id,
                vote=data.get('vote'),
                vote_by=self.user_first_poster
            )

            error_detail = response.data.get('detail')
            self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
            self.assertEqual(error_detail.code, data.get('error_code'))

    def test_deny_vote_post_twice(self):
        response_create = self.create_post_service()
        post_id = response_create.data.get('id')

        expected_data = [
            {'vote': 'like', 'status': HTTP_200_OK},
            {'vote': 'like', 'status': HTTP_403_FORBIDDEN},
            {'vote': 'dislike', 'status': HTTP_200_OK},
            {'vote': 'dislike', 'status': HTTP_403_FORBIDDEN},
        ]

        for data in expected_data:
            response = self.vote_post_service(
                post_id,
                vote=data.get('vote'),
                vote_by=self.user_for_vote
            )

            self.assertEqual(response.status_code, data.get('status'))

    def test_get_posts_unauthorized_user(self):

        view = PostViewSet.as_view({'get': 'list'})
        url = 'api/v1/posts'
        request = self.factory.get(url)
        response = view(request)
        error_detail = response.data.get('detail')
        error_code = 'not_authenticated'

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(error_detail.code, error_code)


class TestUserCreate(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.content_data = {
            'username': 'user_for_test',
            'email': 'user_for_test@testapp.com',
            'password': 'Ecfjk34p!'
        }

    def create_user_service(self, content_data):

        view = UserCreate.as_view()
        url = 'signup/'
        request = self.factory.post(url, content_data)

        return view(request)

    def test_create_user(self):

        expected_data = {
            'username': 'user_for_test',
            'email': 'user_for_test@testapp.com',
            'password': None
        }

        response = self.create_user_service(self.content_data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

        for key, value in expected_data.items():
            self.assertEqual(response.data.get(key), value)

        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(User.objects.get().username, 'user_for_test')

    def test_fail_create_user_with_invalid_data(self):

        content_data = [
            ('user_for_test', 'user_for_test@testapp.com', ''),
            ('user_for_test', '', 'Ecfjk34p'),
            ('', 'user_for_test@testapp.com', 'Ecfjk34p'),
            ('', '', '')
        ]

        view = UserCreate.as_view()
        url = 'signup/'

        for data in content_data:
            request = self.factory.post(
                url,
                {'username': data[0], 'email': data[1], 'password': data[2]}
            )
            response = view(request)
            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_user_with_preexisting_username(self):

        response = self.create_user_service(self.content_data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

        self.content_data['email'] = 'same_user_for_test@testapp.com'

        response_same_user = self.create_user_service(self.content_data)
        error_detail = response_same_user.data.get('username')[0]
        error_code = 'unique'

        self.assertEqual(response_same_user.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(error_detail.code, error_code)

    def test_create_user_with_preexisting_email(self):

        response = self.create_user_service(self.content_data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

        self.content_data['username'] = 'same_user_for_test'

        response_same_user = self.create_user_service(self.content_data)
        error_detail = response_same_user.data.get('email')[0]
        error_code = 'unique'

        self.assertEqual(response_same_user.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(error_detail.code, error_code)
