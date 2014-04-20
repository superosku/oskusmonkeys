import sys

from monkeyapp.database import Base, db_session
from flask import flash
from wtforms.validators import Email, Required, NumberRange

from sqlalchemy import Column, Integer, String, ForeignKey, Table, func
from sqlalchemy.orm import relationship, backref, joinedload, subqueryload
from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import Query

friendship = Table(
    'friendship', Base.metadata,
    Column('m1_id', Integer, ForeignKey('user.id')),
    Column('m2_id', Integer, ForeignKey('user.id')))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(
        String(120), unique=True, nullable=False,
        info={'validators': [Email()]})
    age = Column(Integer(), info={'min': 0})

    best_friend_id = Column(Integer, ForeignKey('user.id'))
    best_friend = relationship(
        lambda: User, remote_side=[id],
        order_by=lambda: User.name, lazy='joined')
    friends = relationship(
        'User',
        secondary=friendship,
        primaryjoin=id == friendship.c.m1_id,
        secondaryjoin=id == friendship.c.m2_id,
        backref=backref('ofriends', lazy='dynamic'),
        lazy='dynamic')

    def add_friend(self, other):
        if self != other:
            if other not in self.friends:
                self.friends.append(other)
            if self not in other.friends:
                other.friends.append(self)
        db_session.add(self)
        db_session.commit()

    def remove_friend(self, other):
        try:
            if other.best_friend == self:
                other.best_friend = None
                # Needed to avoid sqlalchemy.exc.CircularDependencyError
                db_session.commit()
            if self.best_friend == other:
                self.best_friend = None
            if self not in other.friends:
                raise Exception
            self.friends.remove(other)
            other.friends.remove(self)
            db_session.commit()
        except Exception as inst:
            db_session.rollback()
            raise inst

    def get_non_friends(self):
        return User.query.except_(self.friends).filter(User.id != self.id)

    def make_best_friend(self, other):
        self.best_friend = other
        db_session.commit()

    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return '<User %r>' % self.name


def query_users(order=None):
    best_friend_alias = aliased(User, name="bfalias")
    query = (
        db_session.query(
            User, func.count(friendship.c.m1_id),
            best_friend_alias.id, best_friend_alias.name)
        .outerjoin(friendship, User.id == friendship.c.m1_id)
        .outerjoin((best_friend_alias, User.best_friend))
        .group_by(User, best_friend_alias))
    if order == 'name':
        query = query.order_by(User.name)
    elif order == '-name':
        query = query.order_by(User.name.desc())
    elif order == 'email':
        query = query.order_by(User.email)
    elif order == '-email':
        query = query.order_by(User.email.desc())
    elif order == 'age':
        query = query.order_by(User.age)
    elif order == '-age':
        query = query.order_by(User.age.desc())
    elif order == 'bf':
        query = query.order_by(best_friend_alias.name)
    elif order == '-bf':
        query = query.order_by(best_friend_alias.name.desc())
    elif order == 'friends':
        query = query.order_by(func.count(friendship.c.m1_id))
    elif order == '-friends':
        query = query.order_by(func.count(friendship.c.m1_id).desc())
    return query
