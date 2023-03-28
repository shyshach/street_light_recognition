import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"autoflush": False})


class City(db.Model):
    __tablename__ = 'cities'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(30), index=True, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))


class Street(db.Model):
    __tablename__ = 'streets'
    street_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    street_name = db.Column(db.String(30), index=True, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))


class House(db.Model):
    __tablename__ = 'houses'
    house_id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.Integer, db.ForeignKey('streets.street_id'))
    house_number = db.Column(db.Integer, index=True, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))


class Record(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.house_id'))
    original_photo = db.Column(db.String(150), index=True)
    processed_photo = db.Column(db.String(150), index=True)
    quantity = db.Column(db.Integer)
    timestamp = db.Column(db.Integer, default=int(time.time()), index=True)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password_hash = db.Column(db.String(150))
    joined_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    role = db.Column(db.Integer, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), index=True, unique=True)
