from django.db import models

from django.urls import reverse

from protect.models import User


class Category (models.Model):
    name = models.CharField(max_length=50, unique=True)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.name.title()


class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Post (models.Model):
    news = "NW"

    POST_TYPES = [
        (news, "Объявление"),
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    news = models.CharField(max_length=2, choices=POST_TYPES, default=news)
    category = models.ManyToManyField(Category, through="PostCategory")
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def preview(self):
        return f"{self.text[:124]}"

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.get_news_display()}:{self.text}'

    def get_absolute_url(self):
        return reverse('post-detail',args=[str(self.pk)])

    
class PostCategory (models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment (models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()