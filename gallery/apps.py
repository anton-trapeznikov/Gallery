from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = 'gallery'
    verbose_name = "Галерея изображений"

    def ready(self):
        import gallery.signals