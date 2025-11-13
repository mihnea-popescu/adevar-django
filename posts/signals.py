from django.db.models.signals import post_delete
from django.dispatch import receiver
from posts.models.Post import Post


@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    """
    Deletes image from R2 when the post is deleted.
    """
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception as e:
            print("Error deleting image:", e)