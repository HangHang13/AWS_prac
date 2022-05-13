from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail

# Create your models here.
class User(AbstractUser):
    #재귀
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')

    image=ProcessedImageField(
        blank=True,
        upload_to='thumbnails/',
        processors=[Thumbnail(100,100)],
        format='JPEG',
        options={'quality': 60})