from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from blog.models import Comment, Post

User = get_user_model()


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        return redirect(
            'blog:post_detail',
            post_id=self.get_object().pk,
        )


class PostMixin:
    model = Post
    fields = [
        'title',
        'text',
        'category',
        'pub_date',
        'location',
        'image',
        'is_published',
    ]
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class UserMixin:
    model = User
