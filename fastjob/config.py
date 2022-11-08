import os

# in this class we're gonna a Best Practice that consists in keeping sensible info
# such as the secret key, the db uri, mail_username and password as environment variables

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['EMAIL_USERNAME'] # set env variable -> insert gmail address
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') # set env variable -> insert app pswd

    print('%s' % MAIL_USERNAME)
    print('%s' % MAIL_PASSWORD)
