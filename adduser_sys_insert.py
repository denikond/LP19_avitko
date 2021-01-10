from app import db
from app.models import Item, Image, User
from datetime import datetime

u = User(creation_date=datetime.now(), username='_sys_insert', email='_sys_insert@local')

db.session.add(u)
try:
    db.session.commit()
except Exception as err:
    db.session.rollback()
    print(err)

Item.query.update({'user_id': 1})
try:
    db.session.commit()
except Exception as err:
    print(err)
    db.session.rollback()
