from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Attachment


@receiver(post_delete, sender=Attachment)
def delete_attachment_file(sender, instance, **kwargs):
    """
    Удаляет физический файл вложения с диска после удаления записи Attachment.

    Срабатывает и при удалении самого вложения, и при каскадном удалении заявки
    (Django отправляет post_delete для каждого связанного Attachment).
    Файл удаляется через transaction.on_commit — только если удаление записей
    в БД успешно закоммичено, иначе при откате транзакции мы бы потеряли файл
    у записи, которая осталась.
    """
    file = instance.file
    if not file:
        return
    storage, name = file.storage, file.name
    transaction.on_commit(lambda: storage.delete(name))