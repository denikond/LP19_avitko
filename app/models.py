from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class Item(db.Model):

    key = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), index=True)
    num_of_ad = db.Column(db.String(32), index=True, unique=True)
    creation_date = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    price = db.Column(db.Integer)
    extended_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, db.ForeignKey('item_status.key'))

    def __repr__(self):
        return '<num_of_ad:{} | description:{}>'.format(self.num_of_ad, self.description)


class Image(db.Model):

    key = db.Column(db.Integer, primary_key=True)
    num_of_ad = db.Column(db.String(32), db.ForeignKey('item.num_of_ad'))
    image_path = db.Column(db.String(255))

    def __repr__(self):
        return '<image_path {}>'.format(self.image_path)


class Item_status(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    usr_desc = db.Column(db.String(255))


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    items = db.relationship('Item', backref='author', lazy='dynamic')
    list_page = db.Column(db.Integer, default=1)
    filter_my = db.Column(db.Integer, default=0)
    filter_public = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
