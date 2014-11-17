from django.conf import settings

from py3s3.storage import S3Storage


class S3StaticStorage(S3Storage):
    def __init__(self, name_prefix=settings.STATIC_DIR,
                 bucket=settings.AWS_STORAGE_BUCKET_NAME,
                 aws_access_key=settings.AWS_ACCESS_KEY_ID,
                 aws_secret_key=settings.AWS_SECRET_ACCESS_KEY):
        super().__init__(name_prefix, bucket, aws_access_key, aws_secret_key)


class S3MediaStorage(S3Storage):
    def __init__(self, name_prefix=settings.MEDIA_DIR,
                 bucket=settings.AWS_STORAGE_BUCKET_NAME,
                 aws_access_key=settings.AWS_ACCESS_KEY_ID,
                 aws_secret_key=settings.AWS_SECRET_ACCESS_KEY):
        super().__init__(name_prefix, bucket, aws_access_key, aws_secret_key)
