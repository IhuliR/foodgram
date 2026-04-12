from django.urls import path

from .views import redirect_short_link

urlpatterns = [
    path('', redirect_short_link, name='short-link-redirect'),
]
