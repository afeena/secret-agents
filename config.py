import configparser
import os
import sys

class Config:
    configparser.ConfigParser()
    config = configparser.ConfigParser()
    if not os.path.exists('config.cfg'):
        print("Can\'t find config file!")
        sys.exit(1)
    config.read('config.cfg')



