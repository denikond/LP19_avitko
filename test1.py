import os
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'avitko.db')
print(SQLALCHEMY_DATABASE_URI)

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

Base = declarative_base()

#db = SQLAlchemy()

class Items(Base):

    __tablename__ = "Items"

    key = Column(Integer, primary_key=True)
    description = Column(String)
    num_of_ad = Column(String)
    creation_date = Column(Date)
    address = Column(String)
    price = Column(String)
    extended_text = Column(Text)
#    
#    num_of_ad = db.Column(db.String, unique=True, nullable=False)
#    creation_date = db.Column(db.DateTime, nullable=False)
#   address = db.Column(db.String, nullable=False)
#    price = db.Column(db.String, nullable=False)
#    extended_text = db.Column(db.Text, nullable=True)

"""
    def __init__ (self, description, num_of_ad, creation_date, address, price, extended_text):
        self.description = description
        self.num_of_ad = num_of_ad
        self.creation_date = creation_date
        self.address = address
        self.price = price
        self.extended_text = extended_text

    def __repr__(self):
            return '<News {} {}>'.format(self.title, self.url)
"""

class Images(Base):

    __tablename__ = "Images"

    key = Column(Integer, primary_key=True)
    num_of_ad = Column(String)
    image_path = Column(String)

    def __init__ (self, num_of_ad, image_path):
        self.num_of_ad = num_of_ad
        self.image_path = image_path


Base.metadata.create_all(engine)

