from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def get_published_posts(
    queryset=Post.objects, filter_posts=True, count_comments=True
):
    queryset = queryset.select_related('category', 'author', 'location')

    if filter_posts:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    if count_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.order_by(
        '-pub_date',
    )
