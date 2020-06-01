import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    """
    Universal Config, stuff here should work for development and production!
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'event_stats.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    


class DevConfig(Config):
    DEBUG=True
    ROUTES={'basedir':basedir}
    PORT=5000
    HOST="localhost"


class ProdConfig(Config):
    HOST="0.0.0.0"
    DEBUG=False
    ROUTES={'basedir':'/home/homaverick/UFC-API/'}

    
