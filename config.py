

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'avitko.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#создание путей под картинки
img_normal_dir = os.path.join(basedir, "images", "normal")
img_thumb_dir = os.path.join(basedir, "images", "thumb")
thumb_size = (640, 480)

#создание каталогов под картинки
f_im = os.path.join(basedir, 'images')
if not os.path.exists(f_im):
    os.mkdir(f_im)
del f_im

if not os.path.exists(img_normal_dir):
    os.mkdir(img_normal_dir)
if not os.path.exists(img_thumb_dir):
    os.mkdir(img_thumb_dir)
