from mysite.models import BaseModel
from users.models import User
from django.db import models
import io
from PIL import Image
from django.core.files.base import ContentFile
from mysite.helpers.storage import generate_post_image_path


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(upload_to=generate_post_image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Convert uploaded image → WEBP.
        Preserve the upload_to path already assigned.
        """
        # Only reprocess if a new upload is present
        if self.image and not self.image.name.endswith(".webp"):

            # Load into PIL
            img = Image.open(self.image)
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Convert → WEBP
            output = io.BytesIO()
            img.save(output, format="WEBP", quality=85)
            output.seek(0)

            # Preserve the auto-generated path but change extension to .webp
            base_path = self.image.name.rsplit(".", 1)[0]
            new_filename = base_path + ".webp"

            # Replace file content
            self.image.save(new_filename, ContentFile(output.read()), save=False)

        super().save(*args, **kwargs)