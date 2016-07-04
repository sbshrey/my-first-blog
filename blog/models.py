from django.db import models
from django.utils import timezone

from django.core.urlresolvers import reverse


# Create your models here.

class Post(models.Model):
    author = models.ForeignKey('auth.user')
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to='images/%Y/%m/%d',
                                   blank=True,
                                   null=True,
                                   height_field="height_field",
                                   width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"id", self.id})

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    author = models.ForeignKey('auth.user')
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.published_date = timezone.now()
        self.approved_comment = True
        self.save()

    def __str__(self):
        return str(self.author)
