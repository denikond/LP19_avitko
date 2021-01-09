from app import db

class Item(db.Model):

    key = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), index=True)
    num_of_ad = db.Column(db.String(32), index=True, unique=True)
    creation_date = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    price = db.Column(db.Integer)
    extended_text = db.Column(db.Text)

    def __repr__(self):
        return '<num_of_ad:{} | description:{}>'.format(self.num_of_ad, self.description)

class Image(db.Model):

    key = db.Column(db.Integer, primary_key=True)
    num_of_ad = db.Column(db.String(32), db.ForeignKey('item.num_of_ad'))
    image_path = db.Column(db.String(255))

    def __repr__(self):
        return '<image_path {}>'.format(self.image_path)
