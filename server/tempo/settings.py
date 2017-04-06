from os import getenv

def get(name, default = None):
    return globals().get(name, default)

def bool_env(name, default = False):
    ret = getenv(name, default)

    if ret in ('false', 'False', 0):
        return False

    return bool(ret)

def int_env(name, default = 0):
    return int(getenv(name, default))

def str_env(name, default = ''):
    return getenv(name, default)

DEBUG = bool_env('DEBUG', False)
PORT = int_env('PORT', 8080)

SECRET_KEY = str_env('SECRET_KEY', 'tempo-secret-key')

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s' % (
    str_env('TEMPO_DATABASE_USER'),
    str_env('TEMPO_DATABASE_PASSWORD'),
    str_env('TEMPO_DATABASE_HOST'),
    str_env('TEMPO_DATABASE_DB')
)

AWS_S3_URL_EXPIRATION = 60 * 60     # 1 hour
