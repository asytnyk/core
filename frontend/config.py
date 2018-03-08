import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Q8kBexsnBz9k1Fycr'
