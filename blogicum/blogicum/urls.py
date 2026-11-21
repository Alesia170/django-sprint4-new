from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('blog.urls', namespace='blog')),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
