from django.contrib import admin
from django import forms
from gallery.models import *


class PhotoTagInlie(admin.TabularInline):
    model = PhotoTags
    extra = 1
    fk_name = 'photo'
    raw_id_fields = ('tag',)


class LikeInline(admin.TabularInline):
    model = Like
    extra = 1
    fk_name = 'photo'
    raw_id_fields = ('user',)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('src', 'owner', 'created_at', 'rating',)
    readonly_fields = ('created_at',)
    search_fields = ['id',]
    inlines = (PhotoTagInlie, LikeInline)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name',]


admin.site.register(Photo, PhotoAdmin)
admin.site.register(Tag, TagAdmin)