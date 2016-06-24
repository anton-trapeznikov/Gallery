from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from gallery.models import Like, Photo


@receiver(post_save, sender=Like, dispatch_uid='like-post-save')
def like_post_save(sender, **kwargs):
    '''
    Посылает сигнал на пересчет рейтинга фотографии
    после сохранения связанного с ней лайка.

    '''

    instance = kwargs['instance'] if 'instance' in kwargs else None

    if instance and isinstance(instance, Like):
        pid, old_pid = instance.photo_id, instance._original_photo_id

        if old_pid and old_pid != pid:
            photo_ids = [pid, old_pid]
        else:
            photo_ids = [pid,]

        Photo.prepare(photo_ids=photo_ids)


@receiver(post_delete, sender=Like, dispatch_uid='like-post-delete')
def like_post_delete(sender, **kwargs):
    '''
    Посылает сигнал на пересчет рейтинга фотографии
    после удаления связанного с ней лайка.

    '''

    instance = kwargs['instance'] if 'instance' in kwargs else None
    if instance and isinstance(instance, Like):
        Photo.prepare(photo_ids=[instance.photo_id,])
