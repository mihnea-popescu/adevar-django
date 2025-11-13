from rest_framework import serializers
from posts.models.Post import Post
from mysite.helpers.storage import generate_media_presigned_url


class PostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'image', 'image_url', 'created_at']
        extra_kwargs = {
            "image": {"required": True, "allow_null": False, "write_only": True},
        }

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return generate_media_presigned_url(obj.image.name)