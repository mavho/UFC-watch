import os
import logging
from logging.handlers import RotatingFileHandler 

def create_directory(path_dir):
    if not os.path.exists(path_dir):
        try:
            os.mkdir(path_dir)
        except PermissionError:
            print(f"Rnable to create the {path_dir} directory - please correct permissions or add it manually (config)")
        except:
            print(f"{path_dir} directory - error (config)")

def setup_logger(name,formatter,path, level=logging.INFO,maxBytes=5*1024*1024, backupCount=10):
    
    handler = RotatingFileHandler( os.path.join(path, name), maxBytes=maxBytes, backupCount=backupCount) 
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger