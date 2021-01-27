import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'avitko.db?check_same_thread=False')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '48x7nKY4'
    ITEMS_PER_PAGE = 20
    TEMP_FOLDER = os.path.join(basedir, "app", "static", "images", "temp")

#создание путей под картинки
img_normal_dir = os.path.join(basedir, "app", "static", "images", "normal")
img_thumb_dir = os.path.join(basedir, "app", "static", "images", "thumb")
THUMB_SIZE = (250, 200)
SYS_IMPORT_USERNAME = '_sys_import'
SYS_IMPORT_MAIL = 'sysimport@localhost'

#создание каталогов под картинки
f_im = os.path.join(basedir, "app", "static", "images")
if not os.path.exists(f_im):
    os.mkdir(f_im)
del f_im

if not os.path.exists(img_normal_dir):
    os.mkdir(img_normal_dir)
if not os.path.exists(img_thumb_dir):
    os.mkdir(img_thumb_dir)
