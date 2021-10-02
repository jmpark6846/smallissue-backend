from .base import *
print('production settings loaded')
ALLOWED_HOSTS = ['smallissue.eba-4uzry5z8.ap-northeast-2.elasticbeanstalk.com',
                'awseb-e-f-AWSEBLoa-1EUNDVO81EY6P-1847361572.ap-northeast-2.elb.amazonaws.com',
                'api.smallissue.app',]

JWT_AUTH_SECURE = True
DEBUG = False
