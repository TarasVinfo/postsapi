from rest_framework.exceptions import PermissionDenied

from posts.models import Vote


class PostLogic:

    @staticmethod
    def vote_post(obj_post, user, vote):

        is_voted = Vote.objects.filter(post=obj_post, voted_by=user).exists()

        if not is_voted:
            Vote.objects.create(post=obj_post, voted_by=user, choice=vote)

            return obj_post

        is_voting_by_same_vote = Vote.objects.filter(
            post=obj_post, voted_by=user, choice=vote).exists()

        if is_voting_by_same_vote:
            raise PermissionDenied(f'You cannot {vote} post twice')

        Vote.objects.filter(post=obj_post, voted_by=user).update(choice=vote)

        return obj_post
