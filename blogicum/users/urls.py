from django.urls import include, path

from .views import UserCreateView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('registration/', UserCreateView.as_view(), name='registration'),
]
