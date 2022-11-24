from APIBackendService.settings.common import *

# Production env settings. Must not be used in production.
# Connects to the production database.
# from config import HOST

DEBUG = False
# SESSION_COOKIE_SECURE = True
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['0.0.0.0', 'localhost']


# CORS_ORIGIN_WHITELIST = [
#     'http://resttesttest.com'
# ]
