from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title=models.CharField(max_length=64)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)

    def likes(self):
        return self.votes.filter(choice='like').count()

    def dislikes(self):
        return self.votes.filter(choice='dislike').count()

    def __str__(self):
        return self.title


class Vote(models.Model):
    VOTE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike')
    ]

    choice = models.CharField(max_length=7, choices=VOTE_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='votes')
    voted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("post", "voted_by")

    def __str__(self):
        return f'{self.post} was {self.choice}d by {self.voted_by}'
