from django.urls import path, include

from .views import UserCreateView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('registration/', UserCreateView.as_view(), name='registration'),
]
