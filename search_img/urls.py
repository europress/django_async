from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('list/', views.ListImageView.as_view(), name='list'),
    path('download/', views.search_save, name='download'),
    path('pixels-update-cache/', views.cache_update, name='cache_update'),
    path('img', views.SearchImageView.as_view()),
    path('', views.MyView.as_view())
]

# Serving the media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()
