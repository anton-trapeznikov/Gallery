from django.conf.urls import url
from django.contrib import admin
import gallery.views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^photo/(?P<photo_id>[-\d]+)/$', gallery.views.photo, name='photo'),
    url(r'^tag/(?P<tag_id>[-\d]+)/$', gallery.views.tag, name='tag'),
]
