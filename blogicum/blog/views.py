from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm
from blog.mixins import CommentMixin, OnlyAuthorMixin, PostMixin, UserMixin
from blog.models import Category, Comment, Post
from blog.service import get_published_posts

POSTS_BY_PAGE = 10

User = get_user_model()


class PostListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        return get_published_posts()


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return (
                Post.objects.filter(author=self.request.user)
                | get_published_posts()
            ).distinct()
        return get_published_posts()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryPostListView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return get_published_posts(self.category.posts.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, PostMixin, UpdateView
):

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.pk},
        )


class PostDeleteView(
    LoginRequiredMixin, OnlyAuthorMixin, PostMixin, DeleteView
):

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class UserDetailView(UserMixin, DetailView):
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = get_published_posts(
            queryset=self.object.posts.all(),
            filter_posts=self.request.user != self.object,
        )

        paginator = Paginator(posts, POSTS_BY_PAGE)

        context['page_obj'] = paginator.get_page(self.request.GET.get('page'))

        return context


class UserUpdateView(LoginRequiredMixin, UserMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = (
        'first_name',
        'last_name',
        'username',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )


class CommentUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, UpdateView
):
    form_class = CommentForm

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['post_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )


class CommentDeleteView(
    OnlyAuthorMixin, LoginRequiredMixin, CommentMixin, DeleteView
):

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk},
        )
