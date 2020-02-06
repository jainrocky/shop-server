# from .models import User, UserProfile, UserHistory
import os


def profile_image_upload_to(instance, filename, *args, **kwargs):
    return os.path.join(
        'accounts',
        instance.full_name,
        filename,
    )
