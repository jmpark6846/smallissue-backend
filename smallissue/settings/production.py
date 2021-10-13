from .base import *
print('production settings loaded')
ALLOWED_HOSTS = ['smallissue.eba-4uzry5z8.ap-northeast-2.elasticbeanstalk.com',
                'awseb-e-f-AWSEBLoa-1EUNDVO81EY6P-1847361572.ap-northeast-2.elb.amazonaws.com',
                'api.smallissue.app',]

JWT_AUTH_SECURE = True
DEBUG = False

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

