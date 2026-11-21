from textwrap import shorten

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

MAX_TITLE_LENGTH = 256
SHORT_TITLE_LENGTH = 20

User = get_user_model()


class PublishableTimestampedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(PublishableTimestampedModel):
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH, verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        ),
    )

    class Meta(PublishableTimestampedModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return shorten(self.title, SHORT_TITLE_LENGTH, placeholder='...')


class Location(PublishableTimestampedModel):
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH, verbose_name='Название места'
    )

    class Meta(PublishableTimestampedModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return shorten(self.name, SHORT_TITLE_LENGTH, placeholder='...')


class Post(PublishableTimestampedModel):
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH, verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        verbose_name='Изображение', upload_to='post_images/', blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    @admin.display(description='Изображение')
    def image_tag(self):
        if self.image:
            return format_html(
                '<img src="{}" width="150" height="150">',
                self.image.url,
            )
        return 'Нет изображения'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})

    def __str__(self):
        return shorten(self.title, SHORT_TITLE_LENGTH, placeholder='...')


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
        default_related_name = 'comments'

    def __str__(self):
        short_text = shorten(self.text, SHORT_TITLE_LENGTH, placeholder='...')
        return (
            f'Комментарий автора {self.author} '
            f'к посту "{self.post}" '
            f'текст комментария: {short_text}'
        )
