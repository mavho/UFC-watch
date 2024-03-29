import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    """
    Universal Config, stuff here should work for development and production!
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'UFC_API.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    


class DevConfig(Config):
    DEBUG=True
    ROUTES={'basedir':basedir}
    PORT=80
    HOST="localhost"


class ProdConfig(Config):
    HOST="0.0.0.0"
    DEBUG=False
    PORT=80
    ROUTES={'basedir':basedir}
