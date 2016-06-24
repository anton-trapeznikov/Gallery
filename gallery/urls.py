from django.conf.urls import url
from django.contrib import admin
from gallery.views import PhotoListView
import gallery.views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', PhotoListView.as_view(), name='homepage'),
    url(r'^ajax/like/photo/(?P<pid>[-\d]+)/value/(?P<val>-?[-\d]+)/$',
        gallery.views.set_like, name='set_like'),
]
