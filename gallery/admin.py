from django.contrib import admin
from django import forms
from gallery.models import *


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('src', 'owner', 'created_at', 'rating',)
    readonly_fields = ('created_at',)

admin.site.register(Photo, PhotoAdmin)