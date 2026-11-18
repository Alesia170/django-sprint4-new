from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    UpdateView,
    DetailView,
    ListView,
    DeleteView,
)

from .models import Category, Post, Comment
from .forms import CommentForm

LIMIT_POSTS = 5
POSTS_BY_PAGE = 10

User = get_user_model()


class UserMixin:
    model = User


class PostMixin:
    model = Post
    fields = ['title', 'text', 'category', 'pub_date', 'location', 'image']
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        return redirect(
            'blog:post_detail',
            pk=self.get_object().pk,
        )


def get_published_posts():
    return (
        Post.objects.select_related('category', 'author', 'location')
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        .annotate(comment_count=Count('comments'))
        .order_by(
            '-pub_date',
        )
    )


class PostListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        return get_published_posts()


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'

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
        return get_published_posts().filter(category=self.category)

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
            kwargs={'pk': self.object.pk},
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

        if self.request.user == self.object:
            posts = Post.objects.filter(author=self.object)
        else:
            posts = get_published_posts().filter(author=self.object)

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
        return reverse_lazy(
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
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk},
        )


class CommentUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, UpdateView
):
    form_class = CommentForm

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['post_id'], pk=self.kwargs['pk']
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk},
        )


class CommentDeleteView(
    OnlyAuthorMixin, LoginRequiredMixin, CommentMixin, DeleteView
):

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.pk},
        )
